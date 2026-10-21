"""
Retail Sales Intelligence & Forecasting Platform
Dashboard Data Exporter
==============================================================================
Serializes cleaned records, forecast projections, and KPI summaries into
dashboard/data.json and dashboard/data.js for instant zero-latency loading.
==============================================================================
"""

import json
from pathlib import Path
import pandas as pd

from src.config import BASE_DIR, CLEAN_DATA_FILE, FORECASTS_DIR

DASHBOARD_DIR = BASE_DIR / "dashboard"
JSON_OUTPUT = DASHBOARD_DIR / "data.json"
JS_OUTPUT = DASHBOARD_DIR / "data.js"


def export_dashboard_payload() -> None:
    """Exports structured data payload for the interactive dashboard."""
    if not CLEAN_DATA_FILE.exists():
        raise FileNotFoundError(f"Cleaned dataset missing at {CLEAN_DATA_FILE}")

    df = pd.read_csv(CLEAN_DATA_FILE)

    # Load forecast if available
    fc_file = FORECASTS_DIR / "forecast_results.csv"
    if fc_file.exists():
        fc_df = pd.read_csv(fc_file)
        forecast_list = fc_df.to_dict(orient="records")
    else:
        forecast_list = []

    payload = {
        "records": df.to_dict(orient="records"),
        "forecast": forecast_list,
        "metadata": {
            "total_records": len(df),
            "distinct_orders": int(df["order_id"].nunique()),
            "distinct_customers": int(df["customer_id"].nunique()),
            "total_revenue": round(float(df["revenue"].sum()), 2),
            "total_profit": round(float(df["profit"].sum()), 2),
            "profit_margin_pct": round((df["profit"].sum() / df["revenue"].sum()) * 100.0, 2)
        }
    }

    # Write data.json
    JSON_OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[Dashboard Export] Wrote {JSON_OUTPUT}")

    # Write data.js for direct file:/// opening
    js_content = f"window.EMBEDDED_DATA = {json.dumps(payload)};"
    JS_OUTPUT.write_text(js_content, encoding="utf-8")
    print(f"[Dashboard Export] Wrote {JS_OUTPUT}")


if __name__ == "__main__":
    export_dashboard_payload()
