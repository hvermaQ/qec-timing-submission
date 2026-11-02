"""Structural tests of the actual pinned artifact; no provider access."""
import math
import json
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from build_sleep_probe import ROOT, SOURCE, SLEEP, BOUNDARY, transform, call_counts, variants_from_config


class SleepProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.with_suffix(".ll").read_text()

    def test_baseline_is_byte_identical(self):
        self.assertEqual(transform(self.source, None), self.source)

    def test_sleep_on_unconditional_boundary_and_only_change(self):
        config = json.loads((ROOT / "configs/sleep_probe.json").read_text())
        for duration in (value for value in variants_from_config(config).values() if value is not None):
            with self.subTest(duration=duration):
                ir = transform(self.source, duration)
                pos = ir.index("  call void @" + SLEEP)
                before, after = ir[:pos], ir[pos:]
                self.assertTrue(before.endswith(BOUNDARY))
                self.assertEqual(before.count("call void @__quantum__qis__mz__body"), 4)
                self.assertEqual(after.count("call void @__quantum__qis__mz__body"), 13)
                counts = call_counts(ir)
                self.assertEqual(counts.pop(SLEEP), 1)
                self.assertEqual(counts, call_counts(self.source))
                stripped = "\n".join(line for line in ir.split("\n") if SLEEP not in line)
                # Removing the added declaration leaves its separator blank line.
                stripped = stripped.replace("\n\n\ndeclare i64 @___get_current_shot()",
                                            "\n\ndeclare i64 @___get_current_shot()")
                self.assertEqual(stripped, self.source)

    def test_sweep_preserves_distinct_arguments(self):
        config = json.loads((ROOT / "configs/sleep_probe.json").read_text())
        variants = variants_from_config(config)
        self.assertEqual(list(variants.values()), [None, 0.0, 0.01, 0.05, 0.1, 0.2, 0.5])
        self.assertEqual(len({transform(self.source, value) for value in variants.values()}), 7)
        for name, value in variants.items():
            if value is not None:
                self.assertIn(f"double {value:.17e})", transform(self.source, value))

    def test_invalid_sweep_refused(self):
        for values in ([], [0.0], [-0.1], [math.nan], [math.inf], [0.01, 0.01]):
            with self.subTest(values=values), self.assertRaises(ValueError):
                variants_from_config({"finite_durations_raw": values})

    def test_changed_baseline_refused(self):
        with self.assertRaisesRegex(ValueError, "Baseline changed"):
            transform(self.source + "\n", 0.01)

    def test_invalid_duration_and_ancilla_refused(self):
        for value in (-1.0, math.nan, math.inf):
            with self.assertRaises(ValueError):
                transform(self.source, value)
        with self.assertRaises(ValueError):
            transform(self.source, 0.01, 9)


if __name__ == "__main__":
    unittest.main()
