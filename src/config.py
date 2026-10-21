"""
Retail Sales Intelligence & Forecasting Platform
Configuration Module
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SQL_DIR = BASE_DIR / "sql"
OUTPUTS_DIR = BASE_DIR / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
FORECASTS_DIR = OUTPUTS_DIR / "forecasts"
SAC_DIR = BASE_DIR / "sac"

# Ensure runtime directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, FIGURES_DIR, FORECASTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

# Database Configuration
DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "retail_sales_dw")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# SQLite analytical warehouse path (fallback & instant standalone mode)
SQLITE_DB_PATH = PROCESSED_DATA_DIR / "retail_analytics.db"

# Data Generation & Pipeline Constants
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))
START_DATE = "2024-01-01"
END_DATE = "2025-12-31"

# Raw and Processed File Names
RAW_DATA_FILE = RAW_DATA_DIR / "retail_sales_raw.csv"
CLEAN_DATA_FILE = PROCESSED_DATA_DIR / "retail_sales_cleaned.csv"
SAC_SALES_MODEL_FILE = PROCESSED_DATA_DIR / "sac_prepared_sales_model.csv"
SAC_FORECAST_FILE = PROCESSED_DATA_DIR / "sac_forecast_import.csv"

# Dashboard configuration
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "127.0.0.1")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8501"))
