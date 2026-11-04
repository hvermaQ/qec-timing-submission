import re
import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import fixed_sleep_d3 as f
from build_sleep_probe import call_counts,SOURCE

class FixedSleepTests(unittest.TestCase):
 def test_baseline_quantum_sequence(self):
  def calls(t):
   return [l.strip() for l in t.splitlines() if re.search(r'\bcall\b.*@__quantum__qis__',l) and 'sleep__' not in l and 'barrier10' not in l]
  self.assertEqual(calls(f.qir(2)),calls(SOURCE.with_suffix('.ll').read_text()))
 def test_all_rounds_and_outputs(self):
  for n in f.ROUNDS:
   with self.subTest(n=n):
    t=f.qir(n);c=call_counts(t)
    self.assertEqual(c['__quantum__qis__sleep__body'],9*(n-1))
    self.assertEqual(c['__quantum__qis__barrier10__body'],2*(n-1))
    self.assertEqual(c['__quantum__qis__mz__body'],4*n+9)
    self.assertEqual(c['__quantum__qis__rzz__body'],12*n)
    self.assertEqual(c['__quantum__rt__bool_record_output'],4*n+9)
    self.assertAlmostEqual((n-1)/(n-1),1)
    for r in range(n):
     for k in range(4):
      v=k+1 if r<n-1 else k+5
      self.assertIn(f'i1 %r{r}_v{v},',t)
      self.assertIn(f'c"s{r}_{k}\\00"',t)
    for q in range(9):self.assertIn(f'@tag_{4*n+q},',t)
    self.assertNotRegex(t,r'@__quantum__qis__sleep__body\(%Qubit\* (?:nonnull )?inttoptr \(i64 9 ')
 def test_parts_preserve_500_shots(self):
  for p in f.PLAN:self.assertEqual(sum(p['parts']),500)
