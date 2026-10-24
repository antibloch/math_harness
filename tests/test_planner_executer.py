import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx

from planner_executer.graph import run_agent, validate_plan
from planner_executer.model import PlannerModel
from planner_executer.__main__ import main


def step(ident, dependencies=()):
    return dict(id=ident, claim='claim ' + str(ident), assumptions=[],
                dependencies=list(dependencies), completion_condition='prove ' + str(ident))


class Fixture:
    def __init__(self, partial=False, fail=None):
        self.calls = []
        self.partial = partial
        self.fail = fail

    async def __call__(self, stage, payload):
        self.calls.append((stage, copy.deepcopy(payload)))
        if stage == self.fail:
            raise RuntimeError('synthetic provider failure')
        if stage == 'planner':
            return {'steps': [step('a'), step('b'), step('c', ['a'])]}
        if stage == 'executor':
            ident = payload['step']['id']
            partial = self.partial and ident == 'a'
            return dict(proof='proof ' + ident, status='partial' if partial else 'draft',
                        unresolved_obligations=['INTERNAL_GAP'] if partial else [])
        return {'proof': 'Standalone final fixture proof.'}


class PlannerTests(unittest.IsolatedAsyncioTestCase):
    async def test_truncated_plain_synthesis_is_rejected_and_retains_limit(self):
        model = PlannerModel(api_key='fixture-key', synthesis_max_tokens=4096,
                             http_async_client=httpx.AsyncClient(transport=httpx.MockTransport(
                                 lambda request: httpx.Response(200, json={'choices': [
                                     {'finish_reason': 'length', 'message': {
                                         'role': 'assistant', 'content': 'Unfinished proof'}}]}))))
        self.addAsyncCleanup(model.aclose)
        with self.assertRaises(RuntimeError):
            await model('responder', {})
        self.assertEqual(len(model.errors), 1)
        self.assertEqual(model.errors[0]['finish_reason'], 'length')
        self.assertEqual(model.errors[0]['max_tokens'], 4096)
        self.assertFalse(model.errors[0]['will_retry'])

    async def test_numeric_plan_identifiers_are_normalized(self):
        plan = validate_plan({'steps': [step(1), step(2, [1])]}, 5)
        self.assertEqual([s['id'] for s in plan], ['1', '2'])
        self.assertEqual(plan[1]['dependencies'], ['1'])
        with self.assertRaises(ValueError):
            validate_plan({'steps': [step(1), step('1')]}, 5)

    async def test_complete_context_isolation_and_synthesis(self):
        model = Fixture()
        result = await run_agent(model, 'original problem')
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(result['search_status'], 'full')
        self.assertEqual([s for s, _ in model.calls], ['planner', 'executor', 'executor', 'executor', 'responder'])
        payload = model.calls[3][1]
        self.assertEqual(set(payload['required_predecessor_proofs']), {'a'})
        self.assertNotIn('proof b', json.dumps(payload))
        self.assertEqual(payload['original_problem'], 'original problem')
        synthesis = model.calls[-1][1]
        self.assertEqual(synthesis['executor_outputs'], [{'proof': 'proof a'}, {'proof': 'proof b'}, {'proof': 'proof c'}])
        self.assertNotIn('unresolved_obligations', json.dumps(synthesis))

    async def test_partial_blocks_dependents_but_independent_work_continues(self):
        model = Fixture(partial=True)
        result = await run_agent(model, 'problem')
        self.assertEqual([p['step']['id'] for s, p in model.calls if s == 'executor'], ['a', 'b'])
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(result['search_status'], 'incomplete')
        synthesis = json.dumps(model.calls[-1][1])
        self.assertIn('proof a', synthesis)
        self.assertNotIn('INTERNAL_GAP', synthesis)
        self.assertNotIn('Blocked', synthesis)

    async def test_failed_executor_keeps_independent_work(self):
        model = Fixture(fail='executor')
        result = await run_agent(model, 'problem')
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(sum(s == 'executor' for s, _ in model.calls), 2)
        self.assertTrue(all(o['status'] == 'partial' for o in result['outputs']))

    async def test_failed_synthesis_retains_derivations(self):
        result = await run_agent(Fixture(fail='responder'), 'problem')
        self.assertEqual(result['status'], 'error')
        self.assertIn('proof a', result['solution'])
        self.assertEqual(len(result['outputs']), 3)

    async def test_invalid_plan_rejected_before_execution(self):
        for steps in ([step('a', ['b']), step('b')], [step('a'), step('a')],
                      [step('a', ['a'])], [step('a'), step('b', ['a', 'a'])], []):
            calls = []
            async def model(stage, payload):
                calls.append(stage)
                return {'steps': steps}
            result = await run_agent(model, 'problem')
            self.assertEqual(result['status'], 'error')
            self.assertEqual(calls, ['planner'])
        self.assertEqual((await run_agent(Fixture(), 'problem', max_steps=1))['status'], 'error')

    async def test_cli_writes_outputs_with_shared_ifm_adapter(self):
        fixture = Fixture()
        async def handler(request):
            body = json.loads(request.content)
            stage = next(k for k, prompt in PlannerModel.prompts.items()
                         if body['messages'][0]['content'].endswith(prompt))
            self.assertEqual(request.extensions['timeout']['read'], 600)
            self.assertEqual(body['max_tokens'], 4096 if stage == 'responder' else 2048)
            if stage == 'responder':
                self.assertNotIn('response_format', body)
                self.assertEqual(body['chat_template_kwargs'], {'reasoning_effort': 'high'})
                self.assertEqual(body['temperature'], 1.0)
                self.assertEqual(body['top_p'], 0.95)
            else:
                self.assertEqual(body['response_format'], {'type': 'json_object'})
            output = await fixture(stage, json.loads(body['messages'][1]['content']))
            return httpx.Response(200, json={'choices': [{'finish_reason': 'stop',
                'message': {'role': 'assistant', 'content': output['proof'] if stage == 'responder'
                            else json.dumps(output)}}]})
        class MockModel(PlannerModel):
            def __init__(self, **kwargs):
                super().__init__(api_key='fixture-key', **kwargs, http_async_client=
                                 httpx.AsyncClient(transport=httpx.MockTransport(handler)))
        with tempfile.TemporaryDirectory(prefix='planner-port-', dir='/tmp') as directory:
            output = Path(directory) / 'run'
            with patch('planner_executer.__main__.PlannerModel', MockModel), patch('sys.argv',
                       ['planner_executer', '--problem', 'problem', '--output-dir', str(output),
                        '--request-timeout', '600', '--max-tokens', '2048', '--synthesis-max-tokens', '4096']):
                self.assertEqual(await main(), 0)
            self.assertEqual((output / 'proof.md').read_text(), 'Standalone final fixture proof.\n')
            self.assertEqual(json.loads((output / 'run.json').read_text())['search_status'], 'full')
