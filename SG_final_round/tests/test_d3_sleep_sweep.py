"""Check wait placement against the actual archived extraction circuit."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from d3_sleep_sweep import qir, operand, VALUES
from build_sleep_probe import SOURCE, SLEEP, BOUNDARY, call_counts


class D3SleepTests(unittest.TestCase):
    def test_all_data_waits_between_extraction_rounds(self):
        baseline = call_counts(SOURCE.with_suffix('.ll').read_text())
        for duration in VALUES:
            with self.subTest(duration=duration):
                text = qir(duration)
                counts = call_counts(text)
                self.assertEqual(counts.pop(SLEEP), 9)
                self.assertEqual(counts.pop('__quantum__qis__barrier10__body'), 2)
                self.assertEqual(counts, baseline)
                before, after = text.split(BOUNDARY)
                self.assertEqual(call_counts(before)['__quantum__qis__mz__body'], 4)
                self.assertEqual(call_counts(after)['__quantum__qis__mz__body'], 13)
                block = after.split('  tail call', 1)[0]
                for q in range(9):
                    self.assertEqual(block.count(f'@{SLEEP}({operand(q)}, double {duration:.17e})'), 1)
                self.assertNotIn(f'@{SLEEP}({operand(9)}', block)


if __name__ == '__main__':
    unittest.main()
