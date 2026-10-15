"""Kiểm thử độc lập cho quan hệ đầu vào đã ổn định, không dùng pha Private."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from test_defense import BASE, FakeTools, NORMAL_LINEAGE, defense
from api import SiegeContext


class LineageAdaptiveTests(unittest.TestCase):
    def setUp(self):
        self.tools = FakeTools({'lineage_graph_slice': dict(NORMAL_LINEAGE)})
        self.ctx = SiegeContext(self.tools, dict(BASE))
        defense.register(self.ctx)

    def check(self, model, run_id, actual, expected=None):
        # Giả lập mỗi lần chạy có định danh mới và dữ liệu công cụ đã công bố.
        self.tools.responses['lineage_graph_slice'] = {
            'duration_ms': 2000,
            'actual_upstream': list(actual),
            'actual_downstream_count': 2,
        }
        payload={'run_id':run_id,'model':model}
        if expected is not None:
            payload['expected_upstream']=expected
        return defense.check_lineage_run(payload,self.ctx)

    def test_unrecognized_model_detects_subset_after_three_clean_runs(self):
        for n in range(3):
            self.assertFalse(self.check('dbt:dim_accounts',f'a{n}',{'raw.orders','raw.accounts'}).alert)
        result=self.check('dbt:dim_accounts','a3',{'raw.orders'})
        self.assertTrue(result.alert)
        self.assertIn('raw.accounts',result.reason)
        self.assertEqual(len(self.tools.calls),4)

    def test_no_alert_with_only_two_references(self):
        for n in range(2):
            self.assertFalse(self.check('dbt:dim_accounts',f'a{n}',{'raw.orders','raw.accounts'}).alert)
        self.assertFalse(self.check('dbt:dim_accounts','a2',{'raw.orders'}).alert)

    def test_no_transfer_across_models(self):
        for n in range(4):
            self.assertFalse(self.check('dbt:dim_accounts',f'a{n}',{'raw.orders','raw.accounts'}).alert)
        self.assertFalse(self.check('dbt:dim_users','b1',{'raw.orders'}).alert)

    def test_no_alert_when_history_has_two_common_valid_patterns(self):
        for n in range(3):
            self.assertFalse(self.check('dbt:dim_accounts',f'a{n}',{'raw.orders','raw.accounts'}).alert)
        for n in range(2):
            # Khác biệt trên mô hình khi chưa có cơ sở gọi là lỗi: không cảnh báo.
            self.check('dbt:dim_accounts',f'b{n}',{'raw.orders','raw.customers'})
        self.assertFalse(self.check('dbt:dim_accounts','c0',{'raw.orders'}).alert)

    def test_existing_explicit_model_rule_unchanged(self):
        self.assertTrue(self.check('dbt:stg_orders','x1',{'raw.orders'}).alert)

    def test_package_qualified_dbt_name_recognized(self):
        for name in ('stg_orders', 'dbt:stg_orders', 'project.stg_orders',
                     'dbt:project.stg_orders'):
            with self.subTest(name=name):
                self.assertTrue(self.check(name,'s'+name,{'raw.orders'}).alert)

    def test_other_similar_model_name_not_assumed(self):
        self.assertFalse(self.check('project.stg_orders_archive','other',{'raw.orders'}).alert)

    def test_reset_state_across_runs(self):
        for n in range(3):
            self.assertFalse(self.check('dbt:dim_accounts',f'a{n}',{'raw.orders','raw.accounts'}).alert)
        fresh=SiegeContext(FakeTools({'lineage_graph_slice':{'duration_ms':2000,'actual_upstream':['raw.orders'],'actual_downstream_count':2}}),dict(BASE))
        defense.register(fresh)
        self.assertFalse(defense.check_lineage_run({'run_id':'a3','model':'dbt:dim_accounts'},fresh).alert)

if __name__=='__main__':
    unittest.main()
