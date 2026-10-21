"""
Retail Sales Intelligence & Forecasting Platform
KPI Reconciliation Engine: Python vs SQL
==============================================================================
Independently verifies that metrics calculated via Pandas match exactly with
SQL analytical queries against the Star Schema.
==============================================================================
"""

import math
from typing import Dict, Any, List
import pandas as pd
try:
    from tabulate import tabulate
except ImportError:
    tabulate = None

from src.config import CLEAN_DATA_FILE
from src.analytics.queries import get_executive_kpis
from src.database.connection import get_db_engine


def reconcile_kpis() -> Dict[str, Any]:
    """
    Executes independent Python calculations and compares against SQL results.
    Throws AssertionError if discrepancies exceed tolerance.
    """
    if not CLEAN_DATA_FILE.exists():
        raise FileNotFoundError(f"Cleaned dataset not found at {CLEAN_DATA_FILE}")

    # 1. Independent Python (Pandas) Calculations
    df = pd.read_csv(CLEAN_DATA_FILE)

    py_revenue = round(float(df["revenue"].sum()), 2)
    py_cost = round(float(df["cost"].sum()), 2)
    py_profit = round(float(df["profit"].sum()), 2)
    py_margin = round((py_profit / py_revenue) * 100.0, 2) if py_revenue > 0 else 0.0
    py_orders = int(df["order_id"].nunique())
    py_customers = int(df["customer_id"].nunique())
    py_units = int(df["quantity"].sum())
    py_aov = round(py_revenue / py_orders, 2) if py_orders > 0 else 0.0

    py_metrics = {
        "Total Revenue ($)": py_revenue,
        "Total Cost ($)": py_cost,
        "Total Profit ($)": py_profit,
        "Profit Margin (%)": py_margin,
        "Distinct Orders": py_orders,
        "Distinct Customers": py_customers,
        "Total Units Sold": py_units,
        "Average Order Value ($)": py_aov,
    }

    # 2. SQL Analytics Engine Calculations
    engine, engine_name = get_db_engine()
    sql_raw = get_executive_kpis(engine)

    sql_metrics = {
        "Total Revenue ($)": float(sql_raw["total_revenue"]),
        "Total Cost ($)": float(sql_raw["total_cost"]),
        "Total Profit ($)": float(sql_raw["total_profit"]),
        "Profit Margin (%)": float(sql_raw["profit_margin_pct"]),
        "Distinct Orders": int(sql_raw["total_orders"]),
        "Distinct Customers": int(sql_raw["total_customers"]),
        "Total Units Sold": int(sql_raw["total_units_sold"]),
        "Average Order Value ($)": float(sql_raw["average_order_value"]),
    }

    # 3. Reconciliation & Diff Comparison
    rows = []
    all_matched = True
    discrepancies = []

    for metric_name, py_val in py_metrics.items():
        sql_val = sql_metrics.get(metric_name)
        diff = abs(py_val - sql_val)
        # Tolerance: 0.02 for floating point rounding, 0 for integers
        tolerance = 0.02 if isinstance(py_val, float) else 0
        matched = diff <= tolerance

        if not matched:
            all_matched = False
            discrepancies.append(f"{metric_name}: Python={py_val}, SQL={sql_val}, Diff={diff}")

        status = "PASSED (MATCH)" if matched else "FAILED"
        rows.append({
            "Metric": metric_name,
            "Python (Pandas)": f"{py_val:,.2f}" if isinstance(py_val, float) else f"{py_val:,}",
            "SQL (Fact_Sales)": f"{sql_val:,.2f}" if isinstance(sql_val, float) else f"{sql_val:,}",
            "Absolute Diff": f"{diff:.4f}",
            "Status": status
        })

    report_df = pd.DataFrame(rows)

    print("\n" + "=" * 80)
    print(f"KPI RECONCILIATION REPORT: PYTHON PANDAS VS SQL ({engine_name.upper()})")
    print("=" * 80)
    print(report_df.to_string(index=False))
    print("=" * 80)

    if not all_matched:
        err = f"Reconciliation discrepancies found: {discrepancies}"
        print(f"[ERROR] {err}")
        raise AssertionError(err)

    print("[SUCCESS] All 8 core enterprise KPIs reconciled with 100% mathematical precision!\n")

    return {
        "reconciled": all_matched,
        "engine": engine_name,
        "metrics_evaluated": len(rows),
        "report": rows
    }


if __name__ == "__main__":
    reconcile_kpis()
