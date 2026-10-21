"""
Retail Sales Intelligence & Forecasting Platform
Data Transformation Module
"""

import pandas as pd
import numpy as np


def transform_dataset(df_cleaned: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches the cleaned transaction dataset with:
      - Star Schema date keys and calendar dimensions
      - Recomputed and validated financial measures
      - Categorical business tiers (Discount Tiers, Profitability Status)
    """
    df = df_cleaned.copy()

    # 1. Calendar dimensions & Date Key
    df["date_key"] = df["order_date"].dt.strftime("%Y%m%d").astype(int)
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month
    df["month_name"] = df["order_date"].dt.strftime("%B")
    df["quarter"] = "Q" + df["order_date"].dt.quarter.astype(str)
    df["day"] = df["order_date"].dt.day
    df["is_weekend"] = df["order_date"].dt.dayofweek.isin([5, 6]).astype(int)

    # 2. Re-verify financial calculations strictly
    df["revenue"] = (df["quantity"] * df["unit_price"] * (1.0 - df["discount_rate"])).round(2)
    df["cost"] = (df["quantity"] * df["unit_cost"]).round(2)
    df["profit"] = (df["revenue"] - df["cost"]).round(2)

    # Profit Margin %
    def _calc_margin(row):
        rev = row["revenue"]
        if rev > 0:
            return round((row["profit"] / rev) * 100.0, 2)
        return 0.0

    df["profit_margin_pct"] = df.apply(_calc_margin, axis=1)

    # 3. Business Categorizations
    def _get_discount_tier(rate: float) -> str:
        if rate == 0.0:
            return "No Discount (0%)"
        elif rate <= 0.10:
            return "Low (1-10%)"
        elif rate <= 0.20:
            return "Medium (11-20%)"
        else:
            return "High (>20%)"

    df["discount_tier"] = df["discount_rate"].apply(_get_discount_tier)

    def _get_profit_status(margin: float) -> str:
        if margin < 0:
            return "Loss Making (<0%)"
        elif margin <= 10.0:
            return "Low Margin (0-10%)"
        elif margin <= 25.0:
            return "Moderate (10-25%)"
        else:
            return "Highly Profitable (>25%)"

    df["profitability_status"] = df["profit_margin_pct"].apply(_get_profit_status)

    return df
