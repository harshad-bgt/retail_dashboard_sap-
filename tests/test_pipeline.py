"""
Retail Sales Intelligence & Forecasting Platform
Unit & Integration Tests: Pipeline & Data Quality
"""

import pytest
import pandas as pd
from pathlib import Path

from src.config import CLEAN_DATA_FILE, RAW_DATA_FILE
from src.preprocessing.cleaner import clean_dataset
from src.preprocessing.transformer import transform_dataset
from src.preprocessing.validator import validate_dataframe


def test_cleaned_dataset_exists_and_not_empty():
    """Verify cleaned dataset is present and populated."""
    assert CLEAN_DATA_FILE.exists(), "Cleaned dataset file does not exist"
    df = pd.read_csv(CLEAN_DATA_FILE)
    assert len(df) > 3000, f"Expected >3000 records, got {len(df)}"


def test_deduplication_logic():
    """Verify cleaner eliminates duplicate order line keys."""
    sample_data = pd.DataFrame([
        {
            "Order ID": "ORD-001",
            "Order Line ID": "ORD-001-1",
            "Order Date": "2024-01-15",
            "Product ID": "P1",
            "Product Name": "Test",
            "Category": "Electronics",
            "Customer ID": "C1",
            "Customer Name": "Alice",
            "Customer Segment": "Consumer",
            "Region": "North America",
            "Country": "United States",
            "Quantity": 2,
            "Unit Price": 100.0,
            "Unit Cost": 60.0,
            "Discount": 0.1,
            "Revenue": 180.0,
            "Cost": 120.0,
            "Profit": 60.0,
            "Profit Margin": 33.33
        },
        {
            "Order ID": "ORD-001",
            "Order Line ID": "ORD-001-1",  # Duplicate key
            "Order Date": "2024-01-15",
            "Product ID": "P1",
            "Product Name": "Test",
            "Category": "Electronics",
            "Customer ID": "C1",
            "Customer Name": "Alice",
            "Customer Segment": "Consumer",
            "Region": "North America",
            "Country": "United States",
            "Quantity": 2,
            "Unit Price": 100.0,
            "Unit Cost": 60.0,
            "Discount": 0.1,
            "Revenue": 180.0,
            "Cost": 120.0,
            "Profit": 60.0,
            "Profit Margin": 33.33
        }
    ])
    cleaned, stats = clean_dataset(sample_data)
    assert len(cleaned) == 1, "De-duplication failed to remove duplicate line item"
    assert stats["duplicates_removed"] == 1


def test_data_validation_passes():
    """Verify cleaned dataset passes all integrity and mathematical boundary checks."""
    df = pd.read_csv(CLEAN_DATA_FILE)
    report = validate_dataframe(df)
    assert report["is_valid"] is True, f"Validation failed: {report['errors']}"
    assert report["boundary_violations"] == 0
    assert report["duplicate_order_lines"] == 0
