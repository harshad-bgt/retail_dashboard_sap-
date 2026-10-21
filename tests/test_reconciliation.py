"""
Retail Sales Intelligence & Forecasting Platform
Integration Tests: KPI Reconciliation (Python vs SQL)
"""

import pytest
from src.analytics.reconciliation import reconcile_kpis


def test_python_vs_sql_kpi_reconciliation():
    """Verify that all 8 core KPIs reconcile exactly between Python and SQL."""
    result = reconcile_kpis()
    assert result["reconciled"] is True, "Reconciliation failed between Python and SQL"
    assert result["metrics_evaluated"] == 8, "Expected 8 reconciled metrics"
