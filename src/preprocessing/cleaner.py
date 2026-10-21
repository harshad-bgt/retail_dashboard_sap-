"""
Retail Sales Intelligence & Forecasting Platform
Data Cleaning Module
"""

import pandas as pd
from typing import Tuple, Dict, Any


COLUMN_MAPPING = {
    "Order ID": "order_id",
    "Order Line ID": "order_line_id",
    "Order Date": "order_date",
    "Product ID": "product_id",
    "Product Name": "product_name",
    "Category": "category",
    "Customer ID": "customer_id",
    "Customer Name": "customer_name",
    "Customer Segment": "customer_segment",
    "Region": "region",
    "Country": "country",
    "Quantity": "quantity",
    "Unit Price": "unit_price",
    "Unit Cost": "unit_cost",
    "Discount": "discount_rate",
    "Revenue": "revenue",
    "Cost": "cost",
    "Profit": "profit",
    "Profit Margin": "profit_margin_pct"
}


def clean_dataset(df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cleans raw retail transaction records:
      - Renames columns to standardized snake_case
      - Trims string whitespace
      - Fixes casing inconsistencies
      - De-duplicates order lines
      - Coerces correct data types
    """
    df = df_raw.copy()
    initial_rows = len(df)
    cleaning_stats = {
        "initial_rows": initial_rows,
        "duplicates_removed": 0,
        "trimmed_fields": 0,
        "final_rows": 0
    }

    # Standardize column names
    df.rename(columns=COLUMN_MAPPING, inplace=True)

    # String stripping and casing
    str_cols = df.select_dtypes(include=["object", "string"]).columns
    for c in str_cols:
        df[c] = df[c].astype(str).str.strip()

    # Normalize specific category and region casing
    if "region" in df.columns:
        # Title case regions while respecting acronyms like EMEA
        def _clean_region(val: str) -> str:
            v_low = val.lower()
            if "emea" in v_low:
                return "EMEA"
            if "north america" in v_low:
                return "North America"
            if "asia pacific" in v_low or "apac" in v_low:
                return "Asia Pacific"
            if "latin america" in v_low or "latam" in v_low:
                return "Latin America"
            return val.title()

        df["region"] = df["region"].apply(_clean_region)

    if "customer_segment" in df.columns:
        df["customer_segment"] = df["customer_segment"].str.title()

    # Parse and validate dates
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    invalid_dates = df["order_date"].isnull().sum()
    if invalid_dates > 0:
        raise ValueError(f"Found {invalid_dates} unparseable dates during cleaning.")

    # Convert numeric fields
    numeric_floats = ["unit_price", "unit_cost", "discount_rate", "revenue", "cost", "profit", "profit_margin_pct"]
    for col in numeric_floats:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)

    if "quantity" in df.columns:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").astype(int)

    # De-duplicate by primary business line key
    if "order_line_id" in df.columns:
        dups_count = df.duplicated(subset=["order_line_id"]).sum()
        cleaning_stats["duplicates_removed"] = int(dups_count)
        df.drop_duplicates(subset=["order_line_id"], keep="first", inplace=True)

    df.reset_index(drop=True, inplace=True)
    cleaning_stats["final_rows"] = len(df)

    return df, cleaning_stats
