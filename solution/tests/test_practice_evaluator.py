"""Kiểm tra công cụ tổng hợp Practice bằng nhãn giả lập."""
import importlib.util
from pathlib import Path
import unittest

SRC = Path(__file__).resolve().parents[1] / 'evaluate_practice.py'
spec = importlib.util.spec_from_file_location('practice_evaluator', SRC)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PracticeEvalTests(unittest.TestCase):
    def setUp(self):
        self.truth=[
            {'seq': 0, 'is_faulty':True, 'pillar':'checks','fault_key':'volume_spike'},
            {'seq': 1, 'is_faulty':False, 'pillar':None},
            {'seq': 2, 'is_faulty':False, 'pillar':None},
            {'seq': 3, 'is_faulty':False, 'pillar':None},
        ]
        self.report={'result':{'phase':'practice','verdicts':[
            {'seq': 2, 'alert':False},{'seq':0,'alert':True},
            {'seq':3,'alert':False},{'seq':1,'alert':True}],
            'tpr':1.0,'fpr':0.3333,'cost_ledger':5.0,'budget':10.0,
            'cost_overage':0.0,'score':40.0}}

    def test_matches_out_of_order_seq(self):
        x=module.evaluate(self.report,self.truth)
        self.assertEqual((x['tp'],x['fp'],x['fn'],x['tn']),(1,1,0,2))
        self.assertEqual(x['score_recomputed'],40.0)
        self.assertTrue(all(x['matches_harness'].values()))

    def test_detects_duplicate_seq(self):
        self.report['result']['verdicts'][1]['seq']=2
        with self.assertRaises(ValueError):
            module.evaluate(self.report,self.truth)

    def test_detects_mismatched_score(self):
        self.report['result']['score']=50.0
        x=module.evaluate(self.report,self.truth)
        self.assertFalse(x['matches_harness']['score'])

    def test_rejects_other_phase(self):
        self.report['result']['phase']='private'
        with self.assertRaises(ValueError):
            module.evaluate(self.report,self.truth)

    def test_cost_overage_penalty(self):
        self.report['result'].update(cost_ledger=12,budget=10,cost_overage=0.2,score=36.0)
        x=module.evaluate(self.report,self.truth)
        self.assertEqual(x['score_recomputed'],36.0)
        self.assertTrue(all(x['matches_harness'].values()))

if __name__ == '__main__':
    unittest.main()