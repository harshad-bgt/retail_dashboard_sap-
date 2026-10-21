"""
Retail Sales Intelligence & Forecasting Platform
Database Connection Factory
==============================================================================
Provides a unified SQLAlchemy engine supporting:
  1. MySQL 8.0+ (Production Analytical Data Warehouse)
  2. SQLite 3 (Standalone local testing & continuous demonstration fallback)
==============================================================================
"""

import sys
import logging
from typing import Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.config import (
    DB_TYPE, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD,
    SQLITE_DB_PATH
)

logger = logging.getLogger("RetailSalesDW.Connection")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_db_engine() -> Tuple[Engine, str]:
    """
    Creates and returns a SQLAlchemy Engine and the active engine name ('mysql' or 'sqlite').
    If configured for MySQL but MySQL is unreachable, it logs a clear warning and seamlessly
    falls back to the local SQLite analytical warehouse.
    """
    if DB_TYPE == "mysql":
        connection_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
        try:
            engine = create_engine(connection_url, echo=False, pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"Connected successfully to MySQL database '{DB_NAME}' at {DB_HOST}:{DB_PORT}")
            return engine, "mysql"
        except Exception as e:
            logger.warning(
                f"MySQL connection to '{DB_HOST}:{DB_PORT}' could not be established ({e}). "
                f"Falling back to local SQLite analytical warehouse at: {SQLITE_DB_PATH}"
            )

    # SQLite fallback / standalone
    SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    sqlite_url = f"sqlite:///{SQLITE_DB_PATH.as_posix()}"
    engine = create_engine(sqlite_url, echo=False)
    logger.info(f"Using local analytical warehouse (SQLite) at: {SQLITE_DB_PATH}")
    return engine, "sqlite"
