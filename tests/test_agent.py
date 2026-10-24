import asyncio
import copy
import json
import unittest
from unittest.mock import AsyncMock, patch

import httpx

from math_agent.graph import build_agent, run_agent, stitch
from math_agent.model import IFMModel, PROMPTS


class ScriptedModel:
    """Distinct synthetic identifiers make branch/context leakage observable."""
    def __init__(self, verdicts=None, fail=None, repeat=False):
        self.verdicts = verdicts or {}
        self.fail = fail
        self.repeat = repeat
        self.calls = []
        self.active = 0
        self.peak = 0

    async def __call__(self, stage, payload):
        self.calls.append((stage, copy.deepcopy(payload)))
        self.active += 1
        self.peak = max(self.peak, self.active)
        try:
            await asyncio.sleep(0.002)
            sid = payload.get('subproblem', {}).get('id', 0)
            attempt = payload.get('attempt', 0)
            if self.fail == (stage, sid, attempt):
                raise RuntimeError('synthetic provider failure')
            tag = f's{sid}-a{0 if self.repeat else attempt}'
            if stage == 'decompose':
                return {'subproblems': [f'goal {i}' for i in range(payload['count'])]}
            if stage == 'objects':
                return {'objects': [f'{tag}-object-{i}' for i in range(payload['count'])]}
            if stage == 'manipulations':
                return {'manipulations': [f'{tag}-o{payload["object_id"]}-operation-{i}' for i in range(payload['count'])]}
            if stage == 'trajectory':
                return {'proof': f'{tag}: {payload["object"]}; {payload["text"]}'}
            if stage == 'critic':
                return {'best_id': payload['candidates'][-1]['id'],
                        'verdict': self.verdicts.get((sid, attempt), 'full'),
                        'feedback': f'feedback for {tag}'}
            if stage == 'stitch':
                return {'solution': 'stitched fixture solution'}
            raise AssertionError(stage)
        finally:
            self.active -= 1


class AgentTests(unittest.IsolatedAsyncioTestCase):
    async def test_subproblem_can_reach_critic_while_sibling_objects_are_pending(self):
        base = ScriptedModel()
        first_critic_started = asyncio.Event()

        async def model(stage, payload):
            sid = payload.get('subproblem', {}).get('id')
            if stage == 'objects' and sid == 2:
                await first_critic_started.wait()
            if stage == 'critic' and sid == 1:
                first_critic_started.set()
            return await base(stage, payload)

        result = await asyncio.wait_for(run_agent(model, 'problem', subproblems=2,
                                                 objects=1, manipulations=1), timeout=2)
        self.assertEqual(result['status'], 'complete')

    async def test_object_finishes_trajectories_before_next_object(self):
        base = ScriptedModel()
        trajectory_started = asyncio.Event()
        slow_manipulation_finished = False

        async def model(stage, payload):
            nonlocal slow_manipulation_finished
            if stage == 'manipulations' and payload['object_id'] == 2:
                await trajectory_started.wait()
                slow_manipulation_finished = True
            if stage == 'trajectory' and payload['object_id'] == 1:
                self.assertFalse(slow_manipulation_finished)
                trajectory_started.set()
            return await base(stage, payload)

        result = await asyncio.wait_for(run_agent(model, 'problem', subproblems=1,
                                                 objects=2, manipulations=1), timeout=2)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(len(result['results'][0]['candidates']), 2)

    async def test_branch_topology_context_and_join(self):
        model = ScriptedModel()
        result = await run_agent(model, 'original problem', subproblems=3, objects=2, manipulations=3)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(len(result['results']), 3)
        self.assertEqual(sum(s == 'trajectory' for s, _ in model.calls), 18)
        self.assertEqual(model.peak, 1)
        for branch in result['results']:
            sid = branch['subproblem']['id']
            self.assertEqual(len(branch['objects']), 2)
            self.assertEqual(len(branch['candidates']), 6)
            self.assertTrue(all(c['proof'].startswith(f's{sid}-') for c in branch['candidates']))
        for stage, payload in model.calls:
            if stage == 'trajectory':
                self.assertEqual(payload['problem'], 'original problem')
                self.assertIn('goal', payload['subproblem'])
            if stage == 'critic':
                self.assertEqual(len(payload['candidates']), 6)
        stitched = [p for s, p in model.calls if s == 'stitch']
        self.assertEqual(len(stitched), 1)
        self.assertEqual(stitched[0]['problem'], 'original problem')
        self.assertEqual([r['subproblem']['id'] for r in stitched[0]['results']], [1, 2, 3])

    async def test_partial_retries_only_its_origin_and_supplies_history(self):
        model = ScriptedModel({(1, 0): 'partial'})
        result = await run_agent(model, 'problem')
        self.assertEqual(result['status'], 'complete')
        self.assertEqual([len(r['history']) for r in result['results']], [2, 1])
        retries = [p for s, p in model.calls if s == 'objects' and p['attempt'] == 1]
        self.assertEqual(len(retries), 1)
        self.assertEqual(retries[0]['subproblem']['id'], 1)
        self.assertEqual(retries[0]['history'][0]['review']['verdict'], 'partial')
        self.assertEqual(len(retries[0]['history'][0]['candidates']), 4)
        stages = [s for s, _ in model.calls]
        self.assertGreater(stages.index('stitch'), max(i for i, s in enumerate(stages) if s == 'critic'))

    async def test_exhaustion_is_incomplete_and_keeps_all_attempts(self):
        model = ScriptedModel({(1, 0): 'partial', (1, 1): 'partial'})
        result = await run_agent(model, 'problem')
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(result['search_status'], 'incomplete')
        self.assertEqual(len(result['results'][0]['history']), 2)
        self.assertEqual(result['results'][0]['status'], 'partial')
        self.assertEqual(sum(s == 'stitch' for s, _ in model.calls), 1)
        group = next(p for s, p in model.calls if s == 'stitch')['results'][0]
        self.assertEqual(group['selection'], 'critic_selected')
        self.assertEqual(group['verdict'], 'partial')

    async def test_critic_execution_failure_is_not_a_partial_or_retry(self):
        model = ScriptedModel(fail=('critic', 1, 0))
        result = await run_agent(model, 'problem')
        branch = result['results'][0]
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(result['search_status'], 'incomplete')
        self.assertEqual(branch['status'], 'error')
        self.assertEqual(len(branch['candidates']), 4)
        self.assertEqual(branch['history'], [])
        self.assertFalse(any(p.get('attempt') == 1 for _, p in model.calls))
        self.assertEqual(result['results'][1]['status'], 'full')
        groups = next(p for s, p in model.calls if s == 'stitch')['results']
        self.assertEqual(groups[0]['selection'], 'unranked')
        self.assertEqual(len(groups[0]['candidates']), 4)
        self.assertEqual(groups[1]['selection'], 'critic_selected')

    async def test_failed_retry_preserves_previous_assessed_work(self):
        model = ScriptedModel({(1, 0): 'partial'}, fail=('objects', 1, 1))
        result = await run_agent(model, 'problem')
        branch = result['results'][0]
        self.assertEqual(branch['status'], 'error')
        self.assertEqual(len(branch['history']), 1)
        self.assertEqual(branch['history'][0]['review']['verdict'], 'partial')
        self.assertEqual(len(branch['history'][0]['candidates']), 4)

    async def test_repeated_object_is_rejected_without_extra_retry(self):
        model = ScriptedModel({(1, 0): 'partial'}, repeat=True)
        result = await run_agent(model, 'problem')
        branch = result['results'][0]
        self.assertEqual(branch['status'], 'error')
        self.assertIn('reused', branch['error'])
        self.assertEqual(sum(s == 'objects' and p['subproblem']['id'] == 1 for s, p in model.calls), 2)

    async def test_repeated_manipulation_is_rejected(self):
        base = ScriptedModel({(1, 0): 'partial'})
        async def model(stage, payload):
            response = await base(stage, payload)
            if stage == 'manipulations' and payload['attempt'] == 1:
                old = payload['history'][0]['manipulations']
                response['manipulations'] = [m['text'] for m in old if m['object_id'] == payload['object_id']]
            return response
        result = await run_agent(model, 'problem')
        self.assertEqual(result['results'][0]['status'], 'error')
        self.assertIn('previous manipulation', result['results'][0]['error'])

    async def test_failed_stage_leaves_no_requests_running(self):
        base = ScriptedModel()
        async def model(stage, payload):
            if stage == 'trajectory' and payload['object_id'] == 1:
                raise RuntimeError('trajectory request failed')
            return await base(stage, payload)
        result = await run_agent(model, 'problem')
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(result['search_status'], 'incomplete')
        self.assertEqual(base.active, 0)
        self.assertTrue(all(len(r['candidates']) == 2 for r in result['results']))

    async def test_invalid_best_id_does_not_get_full_status(self):
        base = ScriptedModel()
        async def model(stage, payload):
            response = await base(stage, payload)
            if stage == 'critic':
                response['best_id'] = 'nonexistent'
            return response
        result = await run_agent(model, 'problem')
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(result['search_status'], 'incomplete')
        self.assertTrue(all(r['status'] == 'error' for r in result['results']))

    async def test_bad_decomposition_and_stitch_failure(self):
        async def malformed(stage, payload):
            return {'subproblems': []}
        result = await run_agent(malformed, 'problem')
        self.assertEqual(result['status'], 'error')
        model = ScriptedModel(fail=('stitch', 0, 0))
        result = await run_agent(model, 'problem')
        self.assertEqual(result['status'], 'error')
        self.assertEqual(len(result['results']), 2)
        self.assertTrue(all(r['status'] == 'full' for r in result['results']))

    async def test_new_runs_have_no_old_branch_results(self):
        graph = build_agent(ScriptedModel(), subproblems=1, objects=1, manipulations=1)
        for problem in ('first', 'second'):
            result = await graph.ainvoke({'problem': problem, 'results': []})
            self.assertEqual(len(result['results']), 1)
            self.assertEqual(result['results'][0]['problem'], problem)

    async def test_no_candidate_goal_still_reaches_stitch(self):
        model = ScriptedModel(fail=('objects', 1, 0))
        result = await run_agent(model, 'original problem')
        self.assertEqual(result['status'], 'complete')
        payload = next(p for s, p in model.calls if s == 'stitch')
        self.assertEqual(payload['problem'], 'original problem')
        self.assertEqual(len(payload['results']), 2)
        self.assertEqual(payload['results'][0]['selection'], 'none')
        self.assertEqual(payload['results'][0]['subproblem']['goal'], 'goal 0')

    async def test_failed_retry_critic_uses_prior_assessed_proof(self):
        model = ScriptedModel({(1, 0): 'partial'}, fail=('critic', 1, 1))
        result = await run_agent(model, 'problem')
        group = next(p for s, p in model.calls if s == 'stitch')['results'][0]
        self.assertEqual(result['status'], 'complete')
        self.assertTrue(group['trajectory']['proof'].startswith('s1-a0:'))
        self.assertEqual(group['verdict'], 'partial')
        self.assertTrue(result['results'][0]['candidates'][0]['proof'].startswith('s1-a1:'))

    async def test_saved_state_can_stitch_without_repeating_search(self):
        model = ScriptedModel()
        state = {'problem': 'saved problem',
                 'subproblems': [{'id': 1, 'goal': 'first'}, {'id': 2, 'goal': 'second'}],
                 'results': [{'subproblem': {'id': 1, 'goal': 'first'}, 'status': 'error',
                              'candidates': [{'id': '1.1', 'proof': 'retained reasoning'}]}]}
        result = await stitch(model, state)
        self.assertEqual([s for s, _ in model.calls], ['stitch'])
        groups = model.calls[0][1]['results']
        self.assertEqual(groups[0]['candidates'][0]['proof'], 'retained reasoning')
        self.assertEqual(groups[1]['selection'], 'none')
        self.assertEqual(result['solution'], 'stitched fixture solution')
        state['results'][0]['status'] = 'full'
        self.assertEqual((await stitch(model, state))['search_status'], 'incomplete')

    async def test_positive_counts(self):
        for options in ({'objects': 0}, {'manipulations': -1}, {'subproblems': True}):
            with self.assertRaises(ValueError):
                build_agent(ScriptedModel(), **options)


class AdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_total_deadline_cancels_stalled_call_and_retries(self):
        model = IFMModel(api_key='fixture-key', timeout=0.03, api_retries=1)
        self.addAsyncCleanup(model.aclose)
        calls = 0
        cancelled = asyncio.Event()
        async def invoke(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 1:
                try:
                    await asyncio.sleep(10)
                finally:
                    cancelled.set()
            from langchain_core.messages import AIMessage
            return AIMessage(content='{"proof":"recovered"}', response_metadata={'finish_reason':'stop'})
        model.wait_for_cooldown = AsyncMock()
        with patch.object(type(model.llm), 'ainvoke', side_effect=invoke):
            result = await model('trajectory', {})
        self.assertEqual(result, {'proof': 'recovered'})
        self.assertTrue(cancelled.is_set())
        self.assertEqual(calls, 2)
        self.assertEqual(model.errors[0]['error_type'], 'TimeoutError')
        self.assertTrue(model.errors[0]['recovered'])

    async def make_model(self, handler):
        model = IFMModel(api_key='fixture-key', http_async_client=
                         httpx.AsyncClient(transport=httpx.MockTransport(handler)))
        self.addAsyncCleanup(model.aclose)
        return model

    async def test_timeout_retries_only_failed_request_without_mathematical_retry(self):
        scripted = ScriptedModel()
        requests = []
        async def handler(request):
            body = json.loads(request.content)
            payload = json.loads(body['messages'][1]['content'])
            stage = next(k for k, prompt in PROMPTS.items() if body['messages'][0]['content'].endswith(prompt))
            requests.append((stage, payload))
            self.assertEqual(request.extensions['timeout'], {'connect': 15, 'read': 900, 'write': 30, 'pool': 30})
            if stage == 'trajectory' and sum(s == 'trajectory' for s, _ in requests) == 1:
                raise httpx.ReadTimeout('synthetic slow provider', request=request)
            response = await scripted(stage, payload)
            return httpx.Response(200, json={'choices': [{'finish_reason': 'stop',
                'message': {'role': 'assistant', 'content': json.dumps(response)}}]})
        model = await self.make_model(handler)
        model.wait_for_cooldown = AsyncMock()
        result = await run_agent(model, 'problem', subproblems=2, objects=1, manipulations=1)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual([len(b['history']) for b in result['results']], [1, 1])
        self.assertEqual(sum(s == 'objects' for s, _ in requests), 2)
        self.assertEqual(sum(s == 'trajectory' for s, _ in requests), 3)
        self.assertEqual(sum(s == 'stitch' for s, _ in requests), 1)
        self.assertEqual(len(model.errors), 1)
        self.assertEqual(model.errors[0]['api_attempt'], 1)
        self.assertTrue(model.errors[0]['recovered'])

    async def test_rate_limit_honors_retry_after_and_recovers(self):
        calls = 0
        def handler(request):
            nonlocal calls
            calls += 1
            if calls == 1:
                return httpx.Response(429, headers={'Retry-After': '37'}, json={
                    'error': {'type': 'rate_limit_error', 'message': 'temporary'}})
            return httpx.Response(200, json={'choices': [{'finish_reason': 'stop',
                'message': {'role': 'assistant', 'content': '{"proof":"recovered"}'}}]})
        model = await self.make_model(handler)
        model.wait_for_cooldown = AsyncMock()
        self.assertEqual(await model('trajectory', {}), {'proof': 'recovered'})
        self.assertEqual(calls, 2)
        self.assertEqual(model.errors[0]['retry_delay_seconds'], 37)
        self.assertTrue(model.errors[0]['recovered'])

    async def test_retry_limit_and_daily_quota_are_bounded(self):
        model = await self.make_model(lambda request: httpx.Response(429, headers={'Retry-After': '0'},
                json={'error': {'type': 'rate_limit_error', 'message': 'busy'}}))
        with self.assertRaises(RuntimeError):
            await model('objects', {})
        self.assertEqual(len(model.errors), 3)
        self.assertFalse(model.errors[-1]['will_retry'])
        self.assertFalse(any(e['recovered'] for e in model.errors))
        for headers in ({'Retry-After': '0', 'x-ratelimit-remaining-tokens-daily': '0'},
                        {'Retry-After': '86400'}):
            quota_model = await self.make_model(lambda request, headers=headers: httpx.Response(429,
                headers=headers, json={'error': {'type': 'rate_limit_error', 'message': 'quota'}}))
            with self.assertRaises(RuntimeError):
                await quota_model('objects', {})
            self.assertEqual(len(quota_model.errors), 1)
            self.assertFalse(quota_model.errors[0]['will_retry'])

    async def test_shared_cooldown_delays_other_calls(self):
        import time
        calls = []
        def handler(request):
            calls.append(request)
            return httpx.Response(200, json={'choices': [{'finish_reason': 'stop',
                'message': {'role': 'assistant', 'content': '{}'}}]})
        model = await self.make_model(handler)
        model._cooldown_until = time.monotonic() + 0.05
        first = asyncio.create_task(model('objects', {}))
        second = asyncio.create_task(model('stitch', {}))
        await asyncio.sleep(0.005)
        self.assertEqual(calls, [])
        await asyncio.gather(first, second)
        self.assertEqual(len(calls), 2)

    async def test_default_graph_serializes_api_calls(self):
        model = ScriptedModel()
        result = await run_agent(model, 'problem', subproblems=2, objects=2, manipulations=2)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(model.peak, 1)

    async def test_ifm_environment_key_and_missing_key(self):
        with patch.dict('os.environ', {'IFM_API_KEY': 'environment-key'}, clear=True):
            model = IFMModel()
            self.addAsyncCleanup(model.aclose)
            self.assertEqual(model.llm.openai_api_key.get_secret_value(), 'environment-key')
            self.assertEqual(model.llm.openai_api_base, 'https://api.ifm.ai/v1')
            self.assertEqual(model.llm.model_name, 'IFM/K2-Horizon-375B-A23B')
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaisesRegex(ValueError, 'IFM_API_KEY'):
                IFMModel()

    async def test_http_contract(self):
        def handler(request):
            self.assertEqual(str(request.url), 'https://api.ifm.ai/v1/chat/completions')
            body = json.loads(request.content)
            self.assertEqual(body['model'], 'IFM/K2-Horizon-375B-A23B')
            self.assertEqual(request.headers['authorization'], 'Bearer fixture-key')
            self.assertEqual(body['response_format'], {'type': 'json_object'})
            self.assertEqual(body['max_tokens'], 32768)
            self.assertNotIn('max_completion_tokens', body)
            self.assertEqual(json.loads(body['messages'][1]['content'])['problem'], 'original')
            return httpx.Response(200, json={'choices': [{'finish_reason': 'stop', 'message': {'role': 'assistant', 'content': '{"subproblems":["goal"]}'}}]})
        model = await self.make_model(handler)
        self.assertEqual(await model('decompose', {'problem': 'original', 'count': 1}), {'subproblems': ['goal']})

    async def test_truncation_retains_sanitized_response_and_usage(self):
        model = await self.make_model(lambda request: httpx.Response(200, json={
            'choices': [{'finish_reason': 'length', 'message': {
                'role': 'assistant', 'content': '{"subproblems": ["fixture-key'}}],
            'usage': {'prompt_tokens': 100, 'completion_tokens': 32768, 'total_tokens': 32868,
                      'completion_tokens_details': {'reasoning_tokens': 32000}},
        }))
        with self.assertRaisesRegex(RuntimeError, 'LengthFinishReasonError'):
            await model('decompose', {'problem': 'Prove PNT', 'count': 9})
        diagnostic = model.errors[0]
        self.assertEqual(diagnostic['finish_reason'], 'length')
        self.assertEqual(diagnostic['usage']['completion_tokens'], 32768)
        self.assertEqual(diagnostic['usage']['reasoning_tokens'], 32000)
        self.assertEqual(diagnostic['partial_output'], '{"subproblems": ["[REDACTED]')
        self.assertNotIn('fixture-key', json.dumps(model.errors))

    async def test_custom_token_budget_is_sent(self):
        def handler(request):
            self.assertEqual(json.loads(request.content)['max_tokens'], 8192)
            return httpx.Response(200, json={'choices': [{'finish_reason': 'stop',
                'message': {'role': 'assistant', 'content': '{"solution":"proof"}'}}]})
        model = IFMModel(api_key='fixture-key', max_tokens=8192, http_async_client=
                         httpx.AsyncClient(transport=httpx.MockTransport(handler)))
        self.addAsyncCleanup(model.aclose)
        await model('stitch', {})
        self.assertEqual(model.errors, [])
        with self.assertRaisesRegex(ValueError, 'positive integer'):
            IFMModel(api_key='fixture-key', max_tokens=0)

    async def test_truncated_malformed_and_http_failure(self):
        responses = [httpx.Response(200, json={'choices': [{'finish_reason': 'length', 'message': {'role': 'assistant', 'content': '{}'}}]}),
                     httpx.Response(200, json={'choices': [{'finish_reason': 'stop', 'message': {'role': 'assistant', 'content': 'not json'}}]}),
                     httpx.Response(401, text='private provider body')]
        for response in responses:
            model = await self.make_model(lambda request, response=response: response)
            with self.assertRaises(RuntimeError) as error:
                await model('critic', {})
            self.assertNotIn('private provider body', str(error.exception))
            self.assertNotIn('private provider body', json.dumps(model.errors))
            self.assertEqual(len(model.errors), 1)


if __name__ == '__main__':
    unittest.main()
