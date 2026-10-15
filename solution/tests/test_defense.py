"""Kiểm thử hợp đồng Toolkit API và các điều kiện phát hiện lỗi.

Không thay thế kết quả chạy Practice/Public chính thức.
"""
import importlib.util
import json
import pathlib
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'harness' / 'child_env'))
from api import SiegeContext, Verdict
BASE = json.loads((ROOT / 'data' / 'baselines.json').read_text())
SPEC = importlib.util.spec_from_file_location('student_defense', ROOT / 'solution' / 'defense.py')
defense = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(defense)


class FakeTools:
    def __init__(self, responses=None):
        self.responses = responses or {}
        self.calls = []

    def _answer(self, name, *args):
        self.calls.append((name, args))
        answer = self.responses.get(name, {'error':'mock has no response'})
        return answer

    def batch_profile(self, batch_id):
        return self._answer('batch_profile', batch_id)

    def contract_diff(self, contract_id, checkpoint_batch_id):
        return self._answer('contract_diff', contract_id, checkpoint_batch_id)

    def lineage_graph_slice(self, run_id):
        return self._answer('lineage_graph_slice', run_id)

    def feature_drift(self, feature_view, ref):
        return self._answer('feature_drift', feature_view, ref)

    def embedding_drift(self, corpus, ref):
        return self._answer('embedding_drift', corpus, ref)


NORMAL_PROFILE = {'row_count':499, 'null_rate':{'customer_id':0.003}, 'mean_amount':81.6,
                  'std_amount':16, 'staleness_min':4}
NORMAL_CONTRACT = {'freshness_delay_min':5, 'violations':[]}
NORMAL_LINEAGE = {'duration_ms':2400, 'actual_upstream':['raw.orders','raw.customers'],
                  'actual_downstream_count':2}
NORMAL_FEATURE = {'serve_mean':0.01,'train_mean':0,'train_std':1,'mean_shift_sigma':0.35}
NORMAL_EMBEDDING = {'centroid_shift':0.019, 'avg_doc_age_days':23}
PAYLOADS = [
    ('data_batch', {'batch_id':'b1'}, 'batch_profile'),
    ('contract_checkpoint', {'contract_id':'c1','checkpoint_batch_id':'c1b','declared_sla':{'freshness_min':15}},'contract_diff'),
    ('lineage_run', {'run_id':'l1','model':'dbt:stg_orders'},'lineage_graph_slice'),
    ('feature_materialization', {'feature_view':'v','batch_id':'f1'}, 'feature_drift'),
    ('embedding_batch', {'corpus':'c','chunk_batch_id':'e1'},'embedding_drift'),
]
RESPONSES = {
    'batch_profile': NORMAL_PROFILE, 'contract_diff':NORMAL_CONTRACT,
    'lineage_graph_slice':NORMAL_LINEAGE, 'feature_drift':NORMAL_FEATURE,
    'embedding_drift':NORMAL_EMBEDDING
}


class DefenseTests(unittest.TestCase):
    def setUp(self):
        self.tools=FakeTools(dict(RESPONSES))
        self.ctx=SiegeContext(self.tools,dict(BASE))
        defense.register(self.ctx)

    def verdict(self, event, payload=None):
        for kind, sample, method in PAYLOADS:
            if kind==event:
                return self.ctx._handlers[kind](dict(sample if payload is None else payload),self.ctx)
        raise AssertionError('unknown event')

    def test_registration(self):
        self.assertEqual(set(self.ctx._handlers),set(row[0] for row in PAYLOADS))

    def test_all_normal(self):
        for event,payload,method in PAYLOADS:
            result=self.verdict(event)
            self.assertIsInstance(result,Verdict)
            self.assertFalse(result.alert, (event,result.reason))
        self.assertEqual(len(self.tools.calls),5)

    def test_pillars(self):
        exp=['checks','contracts','lineage','ai_infra','ai_infra']
        for (name,*_), pillar in zip(PAYLOADS,exp):
            self.assertEqual(self.verdict(name).pillar,pillar)

    def test_cost_cache_by_call_identity(self):
        first=self.verdict('data_batch')
        second=self.verdict('data_batch')
        self.assertEqual(first,second)
        self.assertEqual(len(self.tools.calls),1)

    def test_no_stdout(self):
        stream=StringIO()
        with redirect_stdout(stream):
            for name,*_ in PAYLOADS:
                self.verdict(name)
        self.assertEqual(stream.getvalue(),'')

    def test_missing_identifiers_do_not_call_tool(self):
        for kind,*_ in PAYLOADS:
            result=self.verdict(kind,{})
            self.assertFalse(result.alert)
        self.assertEqual(self.tools.calls,[])

    def test_error_result_is_not_fault(self):
        for kind,_,method in PAYLOADS:
            with self.subTest(event=kind):
                self.tools.responses[method]={'error':'no data'}
                self.ctx.state.clear()
                self.assertFalse(self.verdict(kind).alert)
                self.tools.responses[method]=RESPONSES[method]

    def test_non_dict_result_is_not_fault(self):
        self.tools.responses['batch_profile']=None
        self.assertFalse(self.verdict('data_batch').alert)

    def test_rows_spike_and_drop(self):
        for value in (420,590):
            with self.subTest(value=value):
                self.ctx.state.clear()
                self.tools.responses['batch_profile']={**NORMAL_PROFILE,'row_count':value}
                self.assertTrue(self.verdict('data_batch').alert)

    def test_row_bounds_are_not_alerts(self):
        for value in (BASE['row_count_min'],BASE['row_count_max']):
            with self.subTest(value=value):
                self.ctx.state.clear()
                self.tools.responses['batch_profile']={**NORMAL_PROFILE,'row_count':value}
                self.assertFalse(self.verdict('data_batch').alert)

    def test_null_spike(self):
        self.tools.responses['batch_profile']={**NORMAL_PROFILE,'null_rate':{'customer_id':0.02}}
        self.assertTrue(self.verdict('data_batch').alert)

    def test_amount_shift(self):
        self.tools.responses['batch_profile']={**NORMAL_PROFILE,'mean_amount':94}
        self.assertTrue(self.verdict('data_batch').alert)

    def test_staleness(self):
        self.tools.responses['batch_profile']={**NORMAL_PROFILE,'staleness_min':12}
        self.assertTrue(self.verdict('data_batch').alert)

    def test_combined_near_boundary(self):
        self.tools.responses['batch_profile']={**NORMAL_PROFILE,'row_count':553,
                                               'mean_amount':89.8}
        self.assertTrue(self.verdict('data_batch').alert)

    def test_single_near_boundary(self):
        self.tools.responses['batch_profile']={**NORMAL_PROFILE,'row_count':553}
        self.assertFalse(self.verdict('data_batch').alert)

    def test_invalid_numeric_is_not_fault(self):
        for value in (None,False,'unavailable',float('nan'),float('inf')):
            with self.subTest(value=value):
                self.ctx.state.clear()
                self.tools.responses['batch_profile']={**NORMAL_PROFILE,'row_count':value}
                self.assertFalse(self.verdict('data_batch').alert)

    def test_contract_schema_and_type(self):
        for v in ('schema_hash_mismatch','type_violation'):
            with self.subTest(v=v):
                self.ctx.state.clear()
                self.tools.responses['contract_diff']={'freshness_delay_min':5,'violations':[v]}
                self.assertTrue(self.verdict('contract_checkpoint').alert)

    def test_contract_sla(self):
        self.tools.responses['contract_diff']={'freshness_delay_min':13,'violations':[]}
        self.assertTrue(self.verdict('contract_checkpoint', {'contract_id':'c1','checkpoint_batch_id':'c1b','declared_sla':{'freshness_min':10}}).alert)

    def test_contract_baseline_freshness(self):
        self.tools.responses['contract_diff']={'freshness_delay_min':12,'violations':[]}
        self.assertTrue(self.verdict('contract_checkpoint').alert)

    def test_lineage_missing_required(self):
        self.tools.responses['lineage_graph_slice']={**NORMAL_LINEAGE,'actual_upstream':['raw.orders']}
        self.assertTrue(self.verdict('lineage_run').alert)

    def test_lineage_missing_declared(self):
        self.tools.responses['lineage_graph_slice']={**NORMAL_LINEAGE,'actual_upstream':['one']}
        self.assertTrue(self.verdict('lineage_run', {'run_id':'l1','expected_upstream':['one','two']}).alert)

    def test_lineage_nonstandard_model_not_overrestricted(self):
        self.tools.responses['lineage_graph_slice']={**NORMAL_LINEAGE,'actual_upstream':['raw.other']}
        self.assertFalse(self.verdict('lineage_run', {'run_id':'l1','model':'dbt:dim_users'}).alert)

    def test_lineage_orphan(self):
        self.tools.responses['lineage_graph_slice']={**NORMAL_LINEAGE,'actual_downstream_count':0}
        self.assertTrue(self.verdict('lineage_run').alert)

    def test_lineage_runtime(self):
        self.tools.responses['lineage_graph_slice']={**NORMAL_LINEAGE,'duration_ms':8000}
        self.assertTrue(self.verdict('lineage_run').alert)

    def test_feature_shift_threshold(self):
        for value,expected in ((0.472,False),(0.65,False),(0.651,True),(0.97,True)):
            with self.subTest(value=value):
                self.ctx.state.clear()
                self.tools.responses['feature_drift']={**NORMAL_FEATURE,'mean_shift_sigma':value}
                self.assertEqual(self.verdict('feature_materialization').alert,expected)

    def test_feature_reconstruct_sigma(self):
        self.tools.responses['feature_drift']={'serve_mean':3,'train_mean':1,'train_std':2}
        self.assertTrue(self.verdict('feature_materialization').alert)

    def test_embedding_centroid(self):
        self.tools.responses['embedding_drift']={**NORMAL_EMBEDDING,'centroid_shift':0.05}
        self.assertTrue(self.verdict('embedding_batch').alert)

    def test_embedding_age(self):
        self.tools.responses['embedding_drift']={**NORMAL_EMBEDDING,'avg_doc_age_days':55}
        self.assertTrue(self.verdict('embedding_batch').alert)

    def test_embedding_at_bound(self):
        self.tools.responses['embedding_drift']={'centroid_shift':BASE['embedding_centroid_shift_max'],
                                                  'avg_doc_age_days':BASE['corpus_avg_doc_age_days_max']}
        self.assertFalse(self.verdict('embedding_batch').alert)

    def test_stateless_independence_across_runs(self):
        self.tools.responses['batch_profile']={**NORMAL_PROFILE,'row_count':590}
        self.assertTrue(self.verdict('data_batch').alert)
        other=SiegeContext(FakeTools(dict(RESPONSES)),dict(BASE))
        defense.register(other)
        self.assertFalse(other._handlers['data_batch']({'batch_id':'b1'},other).alert)

if __name__=='__main__':
    unittest.main()