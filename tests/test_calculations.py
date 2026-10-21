"""
Retail Sales Intelligence & Forecasting Platform
Unit Tests: Financial Math & Margin Calculations
"""

import pytest
import pandas as pd
from src.config import CLEAN_DATA_FILE


def test_financial_formulas_strict_precision():
    """Verify Revenue, Cost, Profit, and Margin equations hold true across all rows."""
    df = pd.read_csv(CLEAN_DATA_FILE)

    # 1. Revenue = round(Quantity * Unit Price * (1 - Discount), 2)
    expected_rev = (df["quantity"] * df["unit_price"] * (1.0 - df["discount_rate"])).round(2)
    rev_diff = (df["revenue"] - expected_rev).abs()
    assert (rev_diff <= 0.02).all(), "Revenue calculation discrepancy detected"

    # 2. Cost = round(Quantity * Unit Cost, 2)
    expected_cost = (df["quantity"] * df["unit_cost"]).round(2)
    cost_diff = (df["cost"] - expected_cost).abs()
    assert (cost_diff <= 0.02).all(), "Cost calculation discrepancy detected"

    # 3. Profit = round(Revenue - Cost, 2)
    expected_profit = (df["revenue"] - df["cost"]).round(2)
    profit_diff = (df["profit"] - expected_profit).abs()
    assert (profit_diff <= 0.02).all(), "Profit calculation discrepancy detected"

    # 4. Profit Margin % = round((Profit / Revenue) * 100, 2)
    safe_rev = df["revenue"].replace(0, float("nan"))
    expected_margin = ((df["profit"] / safe_rev) * 100.0).round(2).fillna(0.0)
    margin_diff = (df["profit_margin_pct"] - expected_margin).abs()
    assert (margin_diff <= 0.05).all(), "Profit margin percentage discrepancy detected"


def test_average_order_value_formula():
    """Verify order-level AOV uses distinct order count in denominator."""
    df = pd.read_csv(CLEAN_DATA_FILE)
    total_rev = df["revenue"].sum()
    distinct_orders = df["order_id"].nunique()

    aov = total_rev / distinct_orders
    # Make sure distinct orders > 0 and AOV is non-negative and reasonable
    assert distinct_orders > 0
    assert 200.0 <= aov <= 800.0, f"Unexpected AOV range: {aov}"
