"""
Retail Sales Intelligence & Forecasting Platform
Raw Data Loader
"""
from pathlib import Path
from typing import Optional
import pandas as pd

from src.config import RAW_DATA_FILE
from src.ingestion.generator import generate_retail_dataset


REQUIRED_RAW_COLUMNS = [
    "Order ID", "Order Line ID", "Order Date", "Product ID", "Product Name",
    "Category", "Customer ID", "Customer Name", "Customer Segment",
    "Region", "Country", "Quantity", "Unit Price", "Unit Cost",
    "Discount", "Revenue", "Cost", "Profit", "Profit Margin"
]


def load_raw_dataset(file_path: Optional[Path] = None, auto_generate: bool = True) -> pd.DataFrame:
    """
    Loads the raw retail dataset from CSV. If the file is missing and auto_generate is True,
    triggers deterministic generation.
    """
    target = file_path or RAW_DATA_FILE
    if not target.exists():
        if auto_generate:
            print(f"[Loader] Raw dataset not found at {target}. Generating reproducible demo data...")
            return generate_retail_dataset(output_path=target)
        raise FileNotFoundError(f"Raw data file not found at {target}")

    df = pd.read_csv(target)
    print(f"[Loader] Successfully loaded {len(df)} rows from {target}")
    return df
