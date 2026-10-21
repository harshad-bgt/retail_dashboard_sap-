"""
Retail Sales Intelligence & Forecasting Platform
Star Schema ETL Data Loader
==============================================================================
Populates Dim_Date, Dim_Product, Dim_Customer, Dim_Region, and Fact_Sales.
Guarantees idempotent execution, surrogate key resolution, and row count reconciliation.
==============================================================================
"""

import logging
from typing import Dict, Any, Tuple
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.config import CLEAN_DATA_FILE
from src.database.connection import get_db_engine
from src.database.schema import initialize_schema
from src.preprocessing import run_preprocessing_pipeline

logger = logging.getLogger("RetailSalesDW.Loader")


def load_star_schema(
    engine: Engine = None,
    dialect: str = None,
    df_clean: pd.DataFrame = None
) -> Dict[str, Any]:
    """
    Loads dimensional data and fact records into the Star Schema warehouse.
    """
    if engine is None or dialect is None:
        engine, dialect = get_db_engine()

    # Ensure clean dataset exists
    if df_clean is None:
        if not CLEAN_DATA_FILE.exists():
            logger.info("Clean dataset missing; triggering preprocessing pipeline...")
            df_clean, _ = run_preprocessing_pipeline()
        else:
            df_clean = pd.read_csv(CLEAN_DATA_FILE)
            df_clean["order_date"] = pd.to_datetime(df_clean["order_date"])

    logger.info("Initializing Star Schema tables...")
    initialize_schema(engine, dialect)

    with engine.begin() as conn:
        # ----------------------------------------------------------------------
        # 1. Populate Dim_Date
        # ----------------------------------------------------------------------
        dim_date = df_clean[[
            "date_key", "order_date", "day", "month", "month_name", "quarter", "year", "is_weekend"
        ]].drop_duplicates(subset=["date_key"]).copy()
        dim_date.rename(columns={"order_date": "full_date"}, inplace=True)
        dim_date["full_date"] = dim_date["full_date"].dt.strftime("%Y-%m-%d")

        dim_date.to_sql("Dim_Date", con=conn, if_exists="append", index=False)
        date_count = len(dim_date)
        logger.info(f"Loaded {date_count} records into Dim_Date.")

        # ----------------------------------------------------------------------
        # 2. Populate Dim_Product
        # ----------------------------------------------------------------------
        dim_product = df_clean[[
            "product_id", "product_name", "category", "unit_price", "unit_cost"
        ]].drop_duplicates(subset=["product_id"]).copy()

        dim_product.to_sql("Dim_Product", con=conn, if_exists="append", index=False)
        product_count = len(dim_product)
        logger.info(f"Loaded {product_count} records into Dim_Product.")

        # ----------------------------------------------------------------------
        # 3. Populate Dim_Customer
        # ----------------------------------------------------------------------
        dim_customer = df_clean[[
            "customer_id", "customer_name", "customer_segment"
        ]].drop_duplicates(subset=["customer_id"]).copy()

        dim_customer.to_sql("Dim_Customer", con=conn, if_exists="append", index=False)
        customer_count = len(dim_customer)
        logger.info(f"Loaded {customer_count} records into Dim_Customer.")

        # ----------------------------------------------------------------------
        # 4. Populate Dim_Region
        # ----------------------------------------------------------------------
        dim_region = df_clean[[
            "region", "country"
        ]].drop_duplicates().copy()
        dim_region.rename(columns={"region": "region_name"}, inplace=True)

        dim_region.to_sql("Dim_Region", con=conn, if_exists="append", index=False)
        region_count = len(dim_region)
        logger.info(f"Loaded {region_count} records into Dim_Region.")

        # ----------------------------------------------------------------------
        # 5. Retrieve Dimension Surrogate Keys for Fact Table Joining
        # ----------------------------------------------------------------------
        db_products = pd.read_sql("SELECT product_key, product_id FROM Dim_Product", con=conn)
        db_customers = pd.read_sql("SELECT customer_key, customer_id FROM Dim_Customer", con=conn)
        db_regions = pd.read_sql("SELECT region_key, region_name, country FROM Dim_Region", con=conn)

        # Merge surrogate keys onto fact records
        fact = df_clean.copy()
        fact = fact.merge(db_products, on="product_id", how="left")
        fact = fact.merge(db_customers, on="customer_id", how="left")
        fact = fact.merge(db_regions, left_on=["region", "country"], right_on=["region_name", "country"], how="left")

        fact_sales = fact[[
            "order_id", "order_line_id", "date_key", "product_key", "customer_key", "region_key",
            "quantity", "unit_price", "unit_cost", "discount_rate", "discount_tier",
            "revenue", "cost", "profit", "profit_margin_pct", "profitability_status"
        ]].copy()

        fact_sales.to_sql("Fact_Sales", con=conn, if_exists="append", index=False)
        fact_count = len(fact_sales)
        logger.info(f"Loaded {fact_count} records into Fact_Sales.")

    stats = {
        "engine": dialect,
        "dim_date_rows": date_count,
        "dim_product_rows": product_count,
        "dim_customer_rows": customer_count,
        "dim_region_rows": region_count,
        "fact_sales_rows": fact_count,
        "reconciled": fact_count == len(df_clean)
    }

    print("\n" + "=" * 70)
    print("STAR SCHEMA LOADING REPORT")
    print("=" * 70)
    for k, v in stats.items():
        print(f"  {k:20s}: {v}")
    print("=" * 70 + "\n")

    return stats


if __name__ == "__main__":
    load_star_schema()
