import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import run_simple_emulator as runner


class SimpleEmulatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def provider(self, status='COMPLETED'):
        job = Mock(job_id='example-job')
        job.refresh.return_value = dict(status=status)
        job.results.return_value = [SimpleNamespace(
            index=0, raw='{}', serialization_format='json', error=None)]
        return SimpleNamespace(QPU=Mock(return_value=SimpleNamespace(run=Mock(return_value=job))),
                               QPUJob=SimpleNamespace(from_id=Mock(return_value=job)))

    def test_build_roundtrip_and_settings_guard(self):
        manifest = runner.build(self.folder, 100, 'q_sq')
        self.assertEqual(manifest['config']['rounds'], 2)
        text = (self.folder / 'program.roundtrip.ll').read_text()
        self.assertEqual(runner.call_counts(text)['__quantum__qis__sleep__body'], 9)
        self.assertEqual(runner.build(self.folder, 100, 'q_sq'), manifest)
        with self.assertRaisesRegex(RuntimeError, 'Settings changed'):
            runner.build(self.folder, 200, 'q_sq')

    def test_run_collect_and_resume_without_duplicate_submission(self):
        (self.folder / 'program.bc').write_bytes(b'test program')
        provider = self.provider()
        with patch.dict(sys.modules, aqora=provider):
            for stage, platform, shots in [('check', 'nexus:H2-1SC', 1),
                                            ('execute', 'nexus:H2-1E', 100)]:
                folder = self.folder / stage
                first = runner.run_job(folder, platform, shots, 'q_sq', 1, 10)
                second = runner.run_job(folder, platform, shots, 'q_sq', 1, 10)
                self.assertEqual(first, second)
                self.assertEqual(first['shots'], shots)
            self.assertEqual(provider.QPU.return_value.run.call_count, 2)
            raw = self.folder / 'execute/result_0.txt'
            raw.write_text('corrupted')
            with self.assertRaisesRegex(RuntimeError, 'hash mismatch'):
                runner.run_job(raw.parent, 'nexus:H2-1E', 100, 'q_sq', 1, 10)

    def test_failed_checker_stops_workflow(self):
        provider = self.provider('FAILED')
        # Only the analysis dependency is replaced; the real LLVM build and
        # job orchestration run, with no provider/network access.
        with patch.dict(sys.modules, aqora=provider, pymatching=Mock(), stim=Mock()), \
                patch.object(runner, 'analyze') as analyze, \
                patch.object(sys, 'argv', ['runner', '--output', str(self.folder)]):
            with self.assertRaisesRegex(RuntimeError, 'did not succeed'):
                runner.main()
            provider.QPU.assert_called_once_with(platform='nexus:H2-1SC', as_entity='q_sq')
            analyze.assert_not_called()

    def test_ambiguous_submission_is_not_retried(self):
        folder = self.folder / 'execute'
        folder.mkdir()
        (folder / 'request.json').write_text('{}')
        provider = self.provider()
        with patch.dict(sys.modules, aqora=provider):
            with self.assertRaisesRegex(RuntimeError, 'Unresolved submission'):
                runner.run_job(folder, 'nexus:H2-1E', 100, 'q_sq', 1, 10)
            provider.QPU.assert_not_called()

    @unittest.skipUnless(importlib.util.find_spec('pymatching'), 'PyMatching is not installed')
    def test_decode_reproduces_archived_n2_result(self):
        source = runner.ROOT / 'runs/d3_fixed_sleep_690baca08b24dfd2/execute/n2_part1'
        folder = self.folder / 'execute'
        folder.mkdir()
        shutil.copyfile(source / 'result_0.txt', folder / 'result_0.txt')
        job = json.loads((source / 'job.json').read_text())
        manifest = runner.build(self.folder, 500, 'q_sq')
        result = runner.analyze(self.folder, manifest, job)
        self.assertEqual(result['logical_failures'], 59)
        self.assertEqual(result['shots'], 500)
        self.assertAlmostEqual(result['logical_error_probability'], .118)


if __name__ == '__main__':
    unittest.main()
