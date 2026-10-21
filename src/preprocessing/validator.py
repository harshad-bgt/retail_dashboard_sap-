"""
Retail Sales Intelligence & Forecasting Platform
Data Validation Module
==============================================================================
Validates:
  1. Required schema columns
  2. Data types and null constraints
  3. Duplicate transaction keys
  4. Logical boundaries (Quantities > 0, Prices > 0, Costs > 0, 0 <= Discounts <= 1)
  5. Mathematical consistency of Revenue, Cost, Profit, and Profit Margin
==============================================================================
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class DataValidationError(Exception):
    """Raised when data validation fails critical integrity rules."""
    pass


def validate_schema(df: pd.DataFrame, required_columns: List[str]) -> None:
    """Verifies all mandatory columns exist in DataFrame."""
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise DataValidationError(f"Schema validation failed. Missing required columns: {missing}")


def validate_dataframe(df: pd.DataFrame, tolerance: float = 0.02) -> Dict[str, Any]:
    """
    Performs comprehensive data quality and mathematical consistency checks.
    
    Returns:
        dict: Summary report containing check results, counts, and anomaly tallies.
    """
    report = {
        "total_rows": len(df),
        "distinct_orders": df["order_id"].nunique() if "order_id" in df.columns else 0,
        "distinct_customers": df["customer_id"].nunique() if "customer_id" in df.columns else 0,
        "duplicate_order_lines": 0,
        "null_counts": {},
        "boundary_violations": 0,
        "math_discrepancies": {
            "revenue": 0,
            "cost": 0,
            "profit": 0,
            "margin": 0,
        },
        "is_valid": True,
        "warnings": [],
        "errors": []
    }

    # 1. Duplicate check on primary business line key
    if "order_line_id" in df.columns:
        dups = df.duplicated(subset=["order_line_id"]).sum()
        report["duplicate_order_lines"] = int(dups)
        if dups > 0:
            report["errors"].append(f"Found {dups} duplicate order_line_id values.")
            report["is_valid"] = False

    # 2. Null checks
    null_summary = df.isnull().sum().to_dict()
    report["null_counts"] = {k: int(v) for k, v in null_summary.items() if v > 0}
    for col, count in report["null_counts"].items():
        report["warnings"].append(f"Column '{col}' contains {count} missing values.")

    # 3. Numeric boundary checks
    neg_qty = (df["quantity"] <= 0).sum()
    neg_price = (df["unit_price"] <= 0).sum()
    neg_cost = (df["unit_cost"] <= 0).sum()
    invalid_discount = ((df["discount_rate"] < 0.0) | (df["discount_rate"] > 1.0)).sum()

    violations = neg_qty + neg_price + neg_cost + invalid_discount
    report["boundary_violations"] = int(violations)
    if violations > 0:
        report["errors"].append(f"Numeric boundaries violated: neg_qty={neg_qty}, neg_price={neg_price}, neg_cost={neg_cost}, invalid_discount={invalid_discount}")
        report["is_valid"] = False

    # 4. Mathematical consistency checks
    # Expected Revenue = Quantity * Unit Price * (1 - Discount)
    expected_rev = (df["quantity"] * df["unit_price"] * (1.0 - df["discount_rate"])).round(2)
    rev_diff = (df["revenue"] - expected_rev).abs()
    rev_bad = (rev_diff > tolerance).sum()
    report["math_discrepancies"]["revenue"] = int(rev_bad)

    # Expected Cost = Quantity * Unit Cost
    expected_cost = (df["quantity"] * df["unit_cost"]).round(2)
    cost_diff = (df["cost"] - expected_cost).abs()
    cost_bad = (cost_diff > tolerance).sum()
    report["math_discrepancies"]["cost"] = int(cost_bad)

    # Expected Profit = Revenue - Cost
    expected_profit = (df["revenue"] - df["cost"]).round(2)
    profit_diff = (df["profit"] - expected_profit).abs()
    profit_bad = (profit_diff > tolerance).sum()
    report["math_discrepancies"]["profit"] = int(profit_bad)

    # Expected Margin = (Profit / Revenue) * 100
    safe_rev = df["revenue"].replace(0, np.nan)
    expected_margin = ((df["profit"] / safe_rev) * 100.0).round(2).fillna(0.0)
    margin_diff = (df["profit_margin_pct"] - expected_margin).abs()
    margin_bad = (margin_diff > 0.05).sum()
    report["math_discrepancies"]["margin"] = int(margin_bad)

    math_total_errors = rev_bad + cost_bad + profit_bad + margin_bad
    if math_total_errors > 0:
        report["errors"].append(f"Mathematical discrepancies detected: {report['math_discrepancies']}")
        report["is_valid"] = False

    return report
