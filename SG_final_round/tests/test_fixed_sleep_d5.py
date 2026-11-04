import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import fixed_sleep_d5 as f
from build_sleep_probe import call_counts

class FixedSleepD5Tests(unittest.TestCase):
    def test_pinned_five_round_quantum_sequence(self):
        def calls(t):
            return [l.strip() for l in t.splitlines() if re.search(r'\bcall\b.*@__quantum__qis__',l)]
        self.assertEqual(calls(f.qir(5,False)),calls(f.SOURCE.read_text()))

    def test_counts_output_mapping_and_waits(self):
        for n in f.ROUNDS:
            with self.subTest(n=n):
                t=f.qir(n);c=call_counts(t)
                for gate,count in [('phasedx',116*n+50),('rz',104*n+50),('rzz',40*n),('mz',12*n+25),('reset',24*n),('sleep',25*(n-1)),('barrier26',2*(n-1))]:
                    self.assertEqual(c[f'__quantum__qis__{gate}__body'],count)
                ids=re.findall(r'@__quantum__qis__mz__body\([^\n]*%Result\* (?:nonnull )?(?:inttoptr \(i64 (\d+) to %Result\*\)|null)',t)
                self.assertEqual([int(i or 0) for i in ids],list(range(12*n+25)))
                for r in range(n):
                    for k in range(12):
                        v=k+1 if r<n-1 else k+49
                        self.assertIn(f'i1 %r{r}_v{v},',t)
                        self.assertIn(f'c"s{r}_{k}\\00"',t)
                self.assertNotRegex(t,r'@__quantum__qis__sleep__body\(%Qubit\* (?:nonnull )?inttoptr \(i64 25 ')
                for q in range(25):self.assertIn(f'@tag_{12*n+q},',t)
                self.assertIn(f'"required_num_results"="{12*n+25}"',t)
                self.assertIn('"required_num_qubits"="26"',t)

    def test_authorized_allocation_and_cost_caps(self):
        self.assertEqual(sum(p['shots'] for p in f.PLAN),13000)
        self.assertEqual(sum(len(p['parts']) for p in f.PLAN),25)
        for p in f.PLAN:
            self.assertEqual(sum(p['parts']),p['shots'])
            self.assertEqual(p['shots'],2000 if 6<=p['rounds']<=10 else 500)
            for shots in p['parts']:
                self.assertLessEqual(5+shots*(800*p['rounds']+355)/5000,1000)
