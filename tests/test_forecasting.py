"""
Retail Sales Intelligence & Forecasting Platform
Unit Tests: Forecasting Logic & Horizon Validation
"""

import json
import pytest
import pandas as pd
from src.config import FORECASTS_DIR


def test_forecast_horizon_and_bounds():
    """Verify forecast results file exists, contains 3 future periods, and bounds are valid."""
    fc_file = FORECASTS_DIR / "forecast_results.csv"
    assert fc_file.exists(), "Forecast results CSV missing"

    df = pd.read_csv(fc_file)
    assert len(df) == 3, f"Expected 3 forecast periods, got {len(df)}"

    expected_months = ["Jan 2026", "Feb 2026", "Mar 2026"]
    assert list(df["month_name"]) == expected_months, "Forecast months do not follow the historical horizon"

    for _, row in df.iterrows():
        rev = row["forecast_revenue"]
        lower = row["lower_bound_80"]
        upper = row["upper_bound_80"]
        assert rev > 0, "Forecast revenue must be positive"
        assert lower <= rev <= upper, f"Confidence interval invalid: lower={lower}, rev={rev}, upper={upper}"


def test_forecast_evaluation_metrics():
    """Verify evaluation JSON exists and reports realistic baseline and ML metrics."""
    eval_file = FORECASTS_DIR / "forecast_evaluation.json"
    assert eval_file.exists(), "Forecast evaluation JSON missing"

    data = json.loads(eval_file.read_text(encoding="utf-8"))
    assert "metrics" in data
    assert "ml_model" in data["metrics"]
    assert "naive_baseline" in data["metrics"]

    ml_metrics = data["metrics"]["ml_model"]
    assert ml_metrics["mae"] > 0
    assert ml_metrics["mape_pct"] > 0
