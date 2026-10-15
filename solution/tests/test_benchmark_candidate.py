import importlib.util
from pathlib import Path
import unittest

SRC=Path(__file__).resolve().parents[1]/'benchmark_candidate.py'
spec=importlib.util.spec_from_file_location('benchmark_candidate',SRC)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class ComparatorTests(unittest.TestCase):
    def setUp(self):
        self.rows={k:dict(v) for k,v in mod.BASELINE.items()}

    def test_exact_baseline_is_not_improvement(self):
        self.assertFalse(mod.compare(self.rows)['practice_better'])

    def test_improving_practice_only_can_pass(self):
        self.rows['practice']['score']=48.48
        result=mod.compare(self.rows)
        self.assertTrue(result['practice_better'] and result['public_not_worse'] and result['fpr_not_worse'])

    def test_regression_public_rejected(self):
        self.rows['practice']['score']=48.48
        self.rows['public']['score']=42.0
        self.assertFalse(mod.compare(self.rows)['public_not_worse'])

    def test_fpr_regression_rejected(self):
        self.rows['practice']['score']=48.48
        self.rows['public']['fpr']=0.0001
        self.assertFalse(mod.compare(self.rows)['fpr_not_worse'])

    def test_missing_phase_rejected(self):
        with self.assertRaises(ValueError):
            mod.compare({'practice':self.rows['practice']})

if __name__=='__main__':unittest.main()
