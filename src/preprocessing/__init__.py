"""
Retail Sales Intelligence & Forecasting Platform
Preprocessing Pipeline Orchestrator
"""

from typing import Tuple, Dict, Any
import pandas as pd

from src.config import CLEAN_DATA_FILE, SAC_SALES_MODEL_FILE
from src.ingestion.loader import load_raw_dataset
from src.preprocessing.cleaner import clean_dataset
from src.preprocessing.transformer import transform_dataset
from src.preprocessing.validator import validate_dataframe, DataValidationError


def run_preprocessing_pipeline() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Executes the end-to-end Python preprocessing pipeline:
      Raw Ingestion -> Cleaning -> Transformation -> Validation -> Export Cleaned & SAC Formats.
    """
    print("=" * 70)
    print("RUNNING PYTHON ETL PREPROCESSING PIPELINE")
    print("=" * 70)

    # 1. Ingestion
    raw_df = load_raw_dataset()

    # 2. Cleaning
    clean_df, clean_stats = clean_dataset(raw_df)
    print(f"[ETL Cleaning] Started with {clean_stats['initial_rows']} rows.")
    print(f"[ETL Cleaning] Removed {clean_stats['duplicates_removed']} duplicate records.")
    print(f"[ETL Cleaning] Cleaned record count: {clean_stats['final_rows']}")

    # 3. Transformation
    trans_df = transform_dataset(clean_df)
    print(f"[ETL Transform] Generated calendar dimensions and verified financial calculations.")

    # 4. Validation
    validation_report = validate_dataframe(trans_df)
    if not validation_report["is_valid"]:
        error_msg = f"Data validation failed with errors: {validation_report['errors']}"
        print(f"[ETL Validation ERROR] {error_msg}")
        raise DataValidationError(error_msg)

    print(f"[ETL Validation] Data integrity verified: 0 boundary violations, 0 math discrepancies.")

    # 5. Persist Cleaned Dataset
    CLEAN_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    trans_df.to_csv(CLEAN_DATA_FILE, index=False)
    print(f"[ETL Export] Cleaned dataset saved to: {CLEAN_DATA_FILE}")

    # 6. Persist SAP Analytics Cloud Prepared Dataset
    # SAC prefers standardized headers, YYYY-MM-DD dates, and explicit dimension/measure layout
    sac_df = trans_df[[
        "order_id", "order_line_id", "order_date", "date_key", "year", "quarter", "month", "month_name",
        "product_id", "product_name", "category",
        "customer_id", "customer_name", "customer_segment",
        "region", "country",
        "quantity", "unit_price", "unit_cost", "discount_rate", "discount_tier",
        "revenue", "cost", "profit", "profit_margin_pct", "profitability_status"
    ]].copy()
    sac_df.rename(columns={
        "order_id": "Order_ID",
        "order_line_id": "Order_Line_ID",
        "order_date": "Date",
        "date_key": "Date_Key",
        "year": "Year",
        "quarter": "Quarter",
        "month": "Month",
        "month_name": "Month_Name",
        "product_id": "Product_ID",
        "product_name": "Product_Name",
        "category": "Category",
        "customer_id": "Customer_ID",
        "customer_name": "Customer_Name",
        "customer_segment": "Customer_Segment",
        "region": "Region",
        "country": "Country",
        "quantity": "Quantity",
        "unit_price": "Unit_Price",
        "unit_cost": "Unit_Cost",
        "discount_rate": "Discount_Rate",
        "discount_tier": "Discount_Tier",
        "revenue": "Revenue",
        "cost": "Cost",
        "profit": "Profit",
        "profit_margin_pct": "Profit_Margin_Pct",
        "profitability_status": "Profitability_Status"
    }, inplace=True)
    sac_df.to_csv(SAC_SALES_MODEL_FILE, index=False)
    print(f"[ETL Export] SAC-ready dataset saved to: {SAC_SALES_MODEL_FILE}")

    print("=" * 70)
    print(f"ETL PIPELINE COMPLETED SUCCESSFULLY: {len(trans_df)} verified records ready.")
    print("=" * 70)

    return trans_df, validation_report


if __name__ == "__main__":
    run_preprocessing_pipeline()
