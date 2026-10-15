"""Regression tests for declared OpenLineage job metadata without private data."""
import unittest
from test_defense import FakeTools, BASE, NORMAL_LINEAGE, defense
from api import SiegeContext


class LineageJobMetadataTests(unittest.TestCase):
    def setUp(self):
        self.tools = FakeTools({"lineage_graph_slice": {**NORMAL_LINEAGE,
                            "actual_upstream": ["raw.orders"]}})
        self.ctx = SiegeContext(self.tools, dict(BASE))
        defense.register(self.ctx)

    def verdict(self, job):
        return defense.check_lineage_run({"run_id": "run-123", "job": job}, self.ctx)

    def test_job_name_string(self):
        result = self.verdict("dbt:stg_orders")
        self.assertTrue(result.alert)
        self.assertIn("raw.customers", result.reason)
        self.assertEqual(len(self.tools.calls), 1)

    def test_job_name_mapping(self):
        result = self.verdict({"name": "dbt:stg_orders"})
        self.assertTrue(result.alert)
        self.assertIn("raw.customers", result.reason)

    def test_qualified_job_name(self):
        result = self.verdict("dbt:shop.stg_orders")
        self.assertTrue(result.alert)

    def test_different_job_not_assumed_to_require_customers(self):
        result = self.verdict("dbt:dim_customers")
        self.assertFalse(result.alert)

    def test_no_job_no_false_positive(self):
        result = defense.check_lineage_run({"run_id": "run-123"}, self.ctx)
        self.assertFalse(result.alert)

    def test_bad_job_type_ignored(self):
        result = self.verdict({"name": 77})
        self.assertFalse(result.alert)


if __name__ == "__main__":
    unittest.main()
