"""
Retail Sales Intelligence & Forecasting Platform
Short-Term Monthly Revenue Forecasting Engine
==============================================================================
Implements:
  1. Strict calendar aggregation with missing month imputation
  2. Chronological Train/Test splitting (Zero future data leakage)
  3. Naive & Moving Average baselines vs Feature-Engineered Ridge/ML Regressor
  4. Robust evaluation metrics (MAE, RMSE, MAPE)
  5. Recursive 3-Month Out-of-Sample Forecast (Jan 2026 - Mar 2026)
==============================================================================
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

from src.config import (
    CLEAN_DATA_FILE, FORECASTS_DIR, FIGURES_DIR, SAC_FORECAST_FILE,
    RANDOM_SEED
)


def prepare_monthly_series(df_clean: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates transactions into an uninterrupted monthly revenue series.
    Guarantees no missing months via explicit date range reindexing.
    """
    df = df_clean.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])

    monthly = df.groupby(pd.Grouper(key="order_date", freq="MS"))["revenue"].sum().reset_index()
    monthly.rename(columns={"order_date": "ds", "revenue": "y"}, inplace=True)

    # Reindex over complete 24-month horizon to guarantee zero missing calendar intervals
    full_range = pd.date_range(start=monthly["ds"].min(), end=monthly["ds"].max(), freq="MS")
    monthly = monthly.set_index("ds").reindex(full_range, fill_value=0.0).rename_axis("ds").reset_index()

    monthly["month_idx"] = np.arange(1, len(monthly) + 1)
    monthly["month_name"] = monthly["ds"].dt.strftime("%b %Y")
    monthly["calendar_month"] = monthly["ds"].dt.month

    return monthly


def build_supervised_features(series_df: pd.DataFrame) -> pd.DataFrame:
    """Creates lag and trend features for chronological time-series regression."""
    df = series_df.copy()

    # Lags
    df["lag_1"] = df["y"].shift(1)
    df["lag_2"] = df["y"].shift(2)
    df["lag_3"] = df["y"].shift(3)

    # Rolling statistics (3-month window)
    df["rolling_mean_3"] = df["y"].shift(1).rolling(window=3, min_periods=1).mean()

    # Cyclical seasonal harmonics (Month of Year)
    df["sin_month"] = np.sin(2 * np.pi * df["calendar_month"] / 12)
    df["cos_month"] = np.cos(2 * np.pi * df["calendar_month"] / 12)

    return df


def evaluate_and_forecast() -> Dict[str, Any]:
    """
    Executes chronological model training, evaluation against baselines,
    and out-of-sample short-term 3-month forecast generation.
    """
    print("=" * 70)
    print("EXECUTING SHORT-TERM SALES REVENUE FORECASTING WORKFLOW")
    print("=" * 70)

    raw_df = pd.read_csv(CLEAN_DATA_FILE)
    monthly = prepare_monthly_series(raw_df)
    n_total = len(monthly)

    # 1. Chronological Train/Test Split
    # Last 3 months for testing (Months 22, 23, 24: Oct, Nov, Dec 2025)
    test_size = 3
    train_size = n_total - test_size

    train_raw = monthly.iloc[:train_size].copy()
    test_raw = monthly.iloc[train_size:].copy()

    print(f"[Forecast] Historical Months Available: {n_total} (2024-01 to 2025-12)")
    print(f"[Forecast] Chronological Train Window: Months 1 to {train_size} ({train_raw['month_name'].iloc[0]} to {train_raw['month_name'].iloc[-1]})")
    print(f"[Forecast] Chronological Test Window:  Months {train_size + 1} to {n_total} ({test_raw['month_name'].iloc[0]} to {test_raw['month_name'].iloc[-1]})")

    # 2. Baseline Model 1: Naive (Last Known Value)
    last_train_val = train_raw["y"].iloc[-1]
    y_test_actual = test_raw["y"].values
    baseline_naive_preds = np.repeat(last_train_val, test_size)

    # Baseline Model 2: 3-Month Moving Average
    ma3_val = train_raw["y"].iloc[-3:].mean()
    baseline_ma3_preds = np.repeat(ma3_val, test_size)

    # 3. Supervised ML Model (Ridge Regressor with Lag & Seasonal Features)
    feature_df = build_supervised_features(monthly)
    feature_cols = ["month_idx", "lag_1", "lag_2", "lag_3", "rolling_mean_3", "sin_month", "cos_month"]

    # Drop initial rows with NaN from lags
    valid_features = feature_df.dropna(subset=feature_cols).copy()

    train_data = valid_features[valid_features["month_idx"] <= train_size]
    test_data = valid_features[valid_features["month_idx"] > train_size]

    X_train = train_data[feature_cols]
    y_train = train_data["y"]
    X_test = test_data[feature_cols]

    # Fit Ridge Model
    model = Ridge(alpha=1.0, random_state=RANDOM_SEED)
    model.fit(X_train, y_train)

    # Multi-step recursive test prediction
    test_preds = []
    # Build a running history to step through test period without ground-truth leakage
    simulated_history = list(train_raw["y"].values)
    for idx in range(test_size):
        curr_m_idx = train_size + 1 + idx
        curr_ds = test_raw["ds"].iloc[idx]
        cal_m = curr_ds.month
        l1 = simulated_history[-1]
        l2 = simulated_history[-2]
        l3 = simulated_history[-3]
        r3 = np.mean(simulated_history[-3:])
        s_m = np.sin(2 * np.pi * cal_m / 12)
        c_m = np.cos(2 * np.pi * cal_m / 12)

        x_step = pd.DataFrame([{
            "month_idx": curr_m_idx, "lag_1": l1, "lag_2": l2, "lag_3": l3,
            "rolling_mean_3": r3, "sin_month": s_m, "cos_month": c_m
        }])
        pred = float(model.predict(x_step)[0])
        test_preds.append(pred)
        simulated_history.append(pred)

    test_preds = np.array(test_preds)

    # 4. Evaluation Metrics
    def calc_metrics(actual, pred):
        mae = float(mean_absolute_error(actual, pred))
        rmse = float(root_mean_squared_error(actual, pred))
        mape = float(np.mean(np.abs((actual - pred) / actual)) * 100.0)
        return {"mae": round(mae, 2), "rmse": round(rmse, 2), "mape_pct": round(mape, 2)}

    metrics_naive = calc_metrics(y_test_actual, baseline_naive_preds)
    metrics_ma3 = calc_metrics(y_test_actual, baseline_ma3_preds)
    metrics_ml = calc_metrics(y_test_actual, test_preds)

    print("\n" + "-" * 70)
    print("CHRONOLOGICAL MODEL EVALUATION ON OUT-OF-SAMPLE TEST MONTHS")
    print("-" * 70)
    print(f"  Naive Baseline (Last Value):  MAE=${metrics_naive['mae']:,.2f} | RMSE=${metrics_naive['rmse']:,.2f} | MAPE={metrics_naive['mape_pct']:.2f}%")
    print(f"  3-Month Moving Average:       MAE=${metrics_ma3['mae']:,.2f} | RMSE=${metrics_ma3['rmse']:,.2f} | MAPE={metrics_ma3['mape_pct']:.2f}%")
    print(f"  Ridge Regression (Lags+Trend): MAE=${metrics_ml['mae']:,.2f} | RMSE=${metrics_ml['rmse']:,.2f} | MAPE={metrics_ml['mape_pct']:.2f}%")
    print("-" * 70 + "\n")

    # 5. Out-of-Sample 3-Month Future Forecast (Jan, Feb, Mar 2026)
    # Refit model on full 24-month historical observations
    full_train_df = feature_df.dropna(subset=feature_cols)
    X_full = full_train_df[feature_cols]
    y_full = full_train_df["y"]

    full_model = Ridge(alpha=1.0, random_state=RANDOM_SEED)
    full_model.fit(X_full, y_full)

    # Residual standard deviation for prediction intervals
    in_sample_preds = full_model.predict(X_full)
    residuals = y_full - in_sample_preds
    residual_std = float(np.std(residuals))

    future_dates = [
        pd.Timestamp("2026-01-01"),
        pd.Timestamp("2026-02-01"),
        pd.Timestamp("2026-03-01")
    ]

    forecast_records = []
    full_history = list(monthly["y"].values)

    for i, f_date in enumerate(future_dates, start=1):
        f_idx = n_total + i
        cal_m = f_date.month
        l1 = full_history[-1]
        l2 = full_history[-2]
        l3 = full_history[-3]
        r3 = np.mean(full_history[-3:])
        s_m = np.sin(2 * np.pi * cal_m / 12)
        c_m = np.cos(2 * np.pi * cal_m / 12)

        x_step = pd.DataFrame([{
            "month_idx": f_idx, "lag_1": l1, "lag_2": l2, "lag_3": l3,
            "rolling_mean_3": r3, "sin_month": s_m, "cos_month": c_m
        }])
        pred_rev = float(full_model.predict(x_step)[0])
        # Multi-step variance expansion: std * sqrt(step)
        step_uncertainty = residual_std * np.sqrt(i)
        lower_80 = max(0.0, round(pred_rev - 1.28 * step_uncertainty, 2))
        upper_80 = round(pred_rev + 1.28 * step_uncertainty, 2)

        full_history.append(pred_rev)

        forecast_records.append({
            "period": f_date.strftime("%Y-%m-%d"),
            "month_name": f_date.strftime("%b %Y"),
            "type": "Forecast (Estimate)",
            "forecast_revenue": round(pred_rev, 2),
            "lower_bound_80": lower_80,
            "upper_bound_80": upper_80
        })

    forecast_df = pd.DataFrame(forecast_records)
    print("[Forecast] 3-Month Out-of-Sample Predictions:")
    print(forecast_df.to_string(index=False))

    # 6. Save Forecast Results & Evaluation Metadata
    FORECASTS_DIR.mkdir(parents=True, exist_ok=True)
    forecast_results_path = FORECASTS_DIR / "forecast_results.csv"
    forecast_df.to_csv(forecast_results_path, index=False)

    eval_summary = {
        "model_name": "Ridge Regression with Autoregressive Lags & Trend",
        "historical_months": n_total,
        "evaluation_period": f"{test_raw['month_name'].iloc[0]} to {test_raw['month_name'].iloc[-1]}",
        "metrics": {
            "naive_baseline": metrics_naive,
            "moving_average_3m": metrics_ma3,
            "ml_model": metrics_ml
        },
        "forecast_horizon": [r["month_name"] for r in forecast_records],
        "limitations": (
            "Model trained on 24 months of historical transactions. While short-term trends "
            "and moving averages provide reasonable directional estimates, robust multi-year seasonal "
            "cycle decomposition requires 3+ years of data. All figures are predictive estimates, not guarantees."
        )
    }
    eval_json_path = FORECASTS_DIR / "forecast_evaluation.json"
    eval_json_path.write_text(json.dumps(eval_summary, indent=2), encoding="utf-8")

    # 7. Generate SAP Analytics Cloud Forecast Import CSV
    # Standard format: Date, Version, Revenue, Margin_Pct
    sac_rows = []
    # Historical actuals
    for _, row in monthly.iterrows():
        sac_rows.append({
            "Date": row["ds"].strftime("%Y-%m-%d"),
            "Version": "Actual",
            "Revenue": round(row["y"], 2),
            "Status": "Historical"
        })
    # Forecast estimates
    for _, row in forecast_df.iterrows():
        sac_rows.append({
            "Date": row["period"],
            "Version": "Forecast",
            "Revenue": row["forecast_revenue"],
            "Status": "Forecast (Estimate)"
        })
    pd.DataFrame(sac_rows).to_csv(SAC_FORECAST_FILE, index=False)
    print(f"[Forecast] Saved SAC Forecast Import dataset to: {SAC_FORECAST_FILE}")

    # 8. Generate Visualization Figure: 08_sales_forecast_3months.png
    fig, ax = plt.subplots(figsize=(13, 6), dpi=300)

    # Historical line
    hist_labels = monthly["month_name"].tolist()
    hist_rev_k = (monthly["y"] / 1000).tolist()
    ax.plot(hist_labels, hist_rev_k, marker="o", color="#0070f3", linewidth=2.5, label="Historical Revenue ($K)")

    # Connect last historical point to forecast
    future_labels = forecast_df["month_name"].tolist()
    full_plot_labels = hist_labels + future_labels
    forecast_plot_rev_k = [hist_rev_k[-1]] + (forecast_df["forecast_revenue"] / 1000).tolist()
    forecast_plot_x = [hist_labels[-1]] + future_labels

    ax.plot(forecast_plot_x, forecast_plot_rev_k, marker="D", color="#e63946",
            linestyle="--", linewidth=2.5, label="3-Month Revenue Forecast ($K)")

    # Prediction interval shading
    lower_k = [hist_rev_k[-1]] + (forecast_df["lower_bound_80"] / 1000).tolist()
    upper_k = [hist_rev_k[-1]] + (forecast_df["upper_bound_80"] / 1000).tolist()
    ax.fill_between(forecast_plot_x, lower_k, upper_k, color="#e63946", alpha=0.15,
                    label="80% Prediction Confidence Band")

    # Demarcation line
    ax.axvline(hist_labels[-1], color="#64748b", linestyle=":", linewidth=1.5, label="Historical Cutoff (Dec 2025)")

    # Data value callouts for forecast months
    for _, f_row in forecast_df.iterrows():
        ax.annotate(
            f"${f_row['forecast_revenue']/1000:,.1f}K",
            xy=(f_row["month_name"], f_row["forecast_revenue"] / 1000),
            xytext=(0, 12), textcoords="offset points",
            ha="center", fontsize=9, fontweight="bold", color="#e63946"
        )

    ax.set_title("Retail Sales Short-Term Revenue Forecast: Next 3 Months (Jan – Mar 2026)",
                 fontsize=14, fontweight="bold", color="#1d2d44", pad=15)
    ax.set_xlabel("Calendar Month", fontsize=11, fontweight="bold", color="#2d3748")
    ax.set_ylabel("Revenue ($ in Thousands)", fontsize=11, fontweight="bold", color="#2d3748")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(True, linestyle="--", alpha=0.5, color="#e2e8f0")
    ax.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#cbd5e1", fontsize=9.5)

    plt.tight_layout()
    fig8_path = FIGURES_DIR / "08_sales_forecast_3months.png"
    fig.savefig(fig8_path)
    plt.close(fig)
    print(f"[Forecast] Saved Figure: {fig8_path}")

    print("=" * 70)
    print("FORECASTING WORKFLOW COMPLETED SUCCESSFULLY")
    print("=" * 70 + "\n")

    return {
        "monthly_series": monthly,
        "evaluation": eval_summary,
        "forecast": forecast_df
    }


if __name__ == "__main__":
    evaluate_and_forecast()
