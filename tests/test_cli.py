import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout
from io import StringIO

import httpx

from math_agent.__main__ import main, save_proof
from math_agent.model import IFMModel


class CLITests(unittest.TestCase):
    def test_aliases_save_numbered_proofs_without_overwriting(self):
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix='math-agent-cli-', dir='/tmp') as directory:
            root = Path(directory)
            original = root / 'result/run_1/proof.md'
            original.parent.mkdir(parents=True)
            original.write_text('existing proof\n')
            for index in (2, 3):
                command = [sys.executable, '-m', 'math_agent', '--demo',
                           '--i', '2', '--j', '2', '--k', '3', '--output', 'trace.json']
                completed = subprocess.run(command, cwd=root, env={**os.environ, 'PYTHONPATH': str(repo)},
                                           text=True, capture_output=True, timeout=30)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                proof = root / f'result/run_{index}/proof.md'
                self.assertIn('x+y=2(a+b)', proof.read_text())
                self.assertIn(f'result/run_{index}/proof.md', completed.stdout)
                result = json.loads((root / 'trace.json').read_text())
                self.assertEqual(result, json.loads((proof.parent / 'run.json').read_text()))
                self.assertEqual(len(result['results']), 2)
                self.assertTrue(all(len(r['objects']) == 2 and len(r['candidates']) == 6
                                    for r in result['results']))
            self.assertEqual(original.read_text(), 'existing proof\n')

    def test_incomplete_output_is_labeled(self):
        with tempfile.TemporaryDirectory(prefix='math-agent-output-', dir='/tmp') as directory:
            with patch('math_agent.__main__.Path', side_effect=lambda name: Path(directory) / name):
                proof = save_proof({'status': 'incomplete', 'solution': 'Unresolved subproblem 1.'})
            self.assertEqual(proof.read_text(), '# Incomplete\n\nUnresolved subproblem 1.\n')

    def test_draft_prose_is_saved_despite_incomplete_search(self):
        result = {'status': 'complete', 'search_status': 'incomplete',
                  'solution': 'Theorem. The claimed identity follows by induction.'}
        with tempfile.TemporaryDirectory(prefix='math-agent-draft-', dir='/tmp') as directory:
            with patch('math_agent.__main__.Path', side_effect=lambda name: Path(directory) / name):
                proof = save_proof(result)
            self.assertEqual(proof.read_text(), result['solution'] + '\n')
            self.assertEqual(json.loads((proof.parent / 'run.json').read_text())['search_status'], 'incomplete')


class DiagnosticCLITests(unittest.IsolatedAsyncioTestCase):
    async def test_truncated_call_diagnostics_are_saved(self):
        def handler(request):
            self.assertEqual(json.loads(request.content)['max_tokens'], 1024)
            self.assertEqual(request.extensions['timeout']['read'], 450)
            return httpx.Response(200, json={
                'choices': [{'finish_reason': 'length', 'message': {
                    'role': 'assistant', 'content': '{"subproblems": ['}}],
                'usage': {'prompt_tokens': 100, 'completion_tokens': 1024, 'total_tokens': 1124},
            })

        class MockIFM(IFMModel):
            def __init__(self, **kwargs):
                super().__init__(api_key='fixture-secret', **kwargs, http_async_client=
                                 httpx.AsyncClient(transport=httpx.MockTransport(handler)))

        with tempfile.TemporaryDirectory(prefix='math-agent-diagnostics-', dir='/tmp') as directory:
            with patch('math_agent.__main__.IFMModel', MockIFM), \
                 patch('math_agent.__main__.Path', side_effect=lambda name: Path(directory) / name), \
                 patch('sys.argv', ['math_agent', 'Prove PNT', '--i', '9', '--max-tokens', '1024',
                                    '--request-timeout', '450', '--api-retries', '0']), \
                 redirect_stdout(StringIO()):
                code = await main()
            result = json.loads((Path(directory) / 'result/run_1/run.json').read_text())
        self.assertEqual(code, 1)
        self.assertEqual(result['llm_errors'][0]['finish_reason'], 'length')
        self.assertEqual(result['llm_errors'][0]['usage']['completion_tokens'], 1024)
        self.assertEqual(result['llm_errors'][0]['partial_output'], '{"subproblems": [')
        self.assertNotIn('fixture-secret', json.dumps(result))
