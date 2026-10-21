"""
Retail Sales Intelligence & Forecasting Platform
Star Schema DDL Initializer
"""

import logging
from sqlalchemy import text
from sqlalchemy.engine import Engine

logger = logging.getLogger("RetailSalesDW.Schema")


def initialize_schema(engine: Engine, dialect: str) -> None:
    """
    Initializes the Star Schema tables and analytical view.
    Idempotent: Drops and recreates tables cleanly.
    """
    with engine.begin() as conn:
        if dialect == "mysql":
            # Enable foreign key checks
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            conn.execute(text("DROP VIEW IF EXISTS vw_sales_performance;"))
            conn.execute(text("DROP TABLE IF EXISTS Fact_Sales;"))
            conn.execute(text("DROP TABLE IF EXISTS Dim_Date;"))
            conn.execute(text("DROP TABLE IF EXISTS Dim_Product;"))
            conn.execute(text("DROP TABLE IF EXISTS Dim_Customer;"))
            conn.execute(text("DROP TABLE IF EXISTS Dim_Region;"))

            conn.execute(text("""
                CREATE TABLE Dim_Date (
                    date_key INT NOT NULL,
                    full_date DATE NOT NULL,
                    day INT NOT NULL,
                    month INT NOT NULL,
                    month_name VARCHAR(20) NOT NULL,
                    quarter VARCHAR(10) NOT NULL,
                    year INT NOT NULL,
                    is_weekend TINYINT NOT NULL DEFAULT 0,
                    PRIMARY KEY (date_key),
                    UNIQUE KEY uq_full_date (full_date),
                    INDEX idx_dim_date_year_month (year, month)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """))

            conn.execute(text("""
                CREATE TABLE Dim_Product (
                    product_key INT AUTO_INCREMENT NOT NULL,
                    product_id VARCHAR(30) NOT NULL,
                    product_name VARCHAR(150) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    unit_price DECIMAL(10,2) NOT NULL,
                    unit_cost DECIMAL(10,2) NOT NULL,
                    PRIMARY KEY (product_key),
                    UNIQUE KEY uq_product_id (product_id),
                    INDEX idx_dim_product_category (category)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """))

            conn.execute(text("""
                CREATE TABLE Dim_Customer (
                    customer_key INT AUTO_INCREMENT NOT NULL,
                    customer_id VARCHAR(30) NOT NULL,
                    customer_name VARCHAR(100) NOT NULL,
                    customer_segment VARCHAR(50) NOT NULL,
                    PRIMARY KEY (customer_key),
                    UNIQUE KEY uq_customer_id (customer_id),
                    INDEX idx_dim_customer_segment (customer_segment)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """))

            conn.execute(text("""
                CREATE TABLE Dim_Region (
                    region_key INT AUTO_INCREMENT NOT NULL,
                    region_name VARCHAR(50) NOT NULL,
                    country VARCHAR(50) NOT NULL,
                    PRIMARY KEY (region_key),
                    UNIQUE KEY uq_region_country (region_name, country),
                    INDEX idx_dim_region_name (region_name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """))

            conn.execute(text("""
                CREATE TABLE Fact_Sales (
                    sales_key BIGINT AUTO_INCREMENT NOT NULL,
                    order_id VARCHAR(50) NOT NULL,
                    order_line_id VARCHAR(60) NOT NULL,
                    date_key INT NOT NULL,
                    product_key INT NOT NULL,
                    customer_key INT NOT NULL,
                    region_key INT NOT NULL,
                    quantity INT NOT NULL,
                    unit_price DECIMAL(10,2) NOT NULL,
                    unit_cost DECIMAL(10,2) NOT NULL,
                    discount_rate DECIMAL(5,4) NOT NULL,
                    discount_tier VARCHAR(30) NOT NULL,
                    revenue DECIMAL(12,2) NOT NULL,
                    cost DECIMAL(12,2) NOT NULL,
                    profit DECIMAL(12,2) NOT NULL,
                    profit_margin_pct DECIMAL(6,2) NOT NULL,
                    profitability_status VARCHAR(30) NOT NULL,
                    PRIMARY KEY (sales_key),
                    UNIQUE KEY uq_order_line_id (order_line_id),
                    INDEX idx_fact_date (date_key),
                    INDEX idx_fact_product (product_key),
                    INDEX idx_fact_customer (customer_key),
                    INDEX idx_fact_region (region_key),
                    INDEX idx_fact_order (order_id),
                    CONSTRAINT fk_fact_date FOREIGN KEY (date_key) REFERENCES Dim_Date(date_key),
                    CONSTRAINT fk_fact_product FOREIGN KEY (product_key) REFERENCES Dim_Product(product_key),
                    CONSTRAINT fk_fact_customer FOREIGN KEY (customer_key) REFERENCES Dim_Customer(customer_key),
                    CONSTRAINT fk_fact_region FOREIGN KEY (region_key) REFERENCES Dim_Region(region_key)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """))

            conn.execute(text("""
                CREATE OR REPLACE VIEW vw_sales_performance AS
                SELECT
                    f.sales_key,
                    f.order_id,
                    f.order_line_id,
                    d.full_date AS order_date,
                    d.year,
                    d.quarter,
                    d.month,
                    d.month_name,
                    p.product_id,
                    p.product_name,
                    p.category,
                    c.customer_id,
                    c.customer_name,
                    c.customer_segment,
                    r.region_name AS region,
                    r.country,
                    f.quantity,
                    f.unit_price,
                    f.unit_cost,
                    f.discount_rate,
                    f.discount_tier,
                    f.revenue,
                    f.cost,
                    f.profit,
                    f.profit_margin_pct,
                    f.profitability_status
                FROM Fact_Sales f
                JOIN Dim_Date d ON f.date_key = d.date_key
                JOIN Dim_Product p ON f.product_key = p.product_key
                JOIN Dim_Customer c ON f.customer_key = c.customer_key
                JOIN Dim_Region r ON f.region_key = r.region_key;
            """))

            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

        else:
            # SQLite DDL
            conn.execute(text("DROP VIEW IF EXISTS vw_sales_performance;"))
            conn.execute(text("DROP TABLE IF EXISTS Fact_Sales;"))
            conn.execute(text("DROP TABLE IF EXISTS Dim_Date;"))
            conn.execute(text("DROP TABLE IF EXISTS Dim_Product;"))
            conn.execute(text("DROP TABLE IF EXISTS Dim_Customer;"))
            conn.execute(text("DROP TABLE IF EXISTS Dim_Region;"))

            conn.execute(text("""
                CREATE TABLE Dim_Date (
                    date_key INTEGER PRIMARY KEY,
                    full_date TEXT NOT NULL UNIQUE,
                    day INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    month_name TEXT NOT NULL,
                    quarter TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    is_weekend INTEGER NOT NULL DEFAULT 0
                );
            """))

            conn.execute(text("""
                CREATE TABLE Dim_Product (
                    product_key INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL UNIQUE,
                    product_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    unit_price REAL NOT NULL,
                    unit_cost REAL NOT NULL
                );
            """))

            conn.execute(text("""
                CREATE TABLE Dim_Customer (
                    customer_key INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id TEXT NOT NULL UNIQUE,
                    customer_name TEXT NOT NULL,
                    customer_segment TEXT NOT NULL
                );
            """))

            conn.execute(text("""
                CREATE TABLE Dim_Region (
                    region_key INTEGER PRIMARY KEY AUTOINCREMENT,
                    region_name TEXT NOT NULL,
                    country TEXT NOT NULL,
                    UNIQUE(region_name, country)
                );
            """))

            conn.execute(text("""
                CREATE TABLE Fact_Sales (
                    sales_key INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT NOT NULL,
                    order_line_id TEXT NOT NULL UNIQUE,
                    date_key INTEGER NOT NULL,
                    product_key INTEGER NOT NULL,
                    customer_key INTEGER NOT NULL,
                    region_key INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    unit_cost REAL NOT NULL,
                    discount_rate REAL NOT NULL,
                    discount_tier TEXT NOT NULL,
                    revenue REAL NOT NULL,
                    cost REAL NOT NULL,
                    profit REAL NOT NULL,
                    profit_margin_pct REAL NOT NULL,
                    profitability_status TEXT NOT NULL,
                    FOREIGN KEY (date_key) REFERENCES Dim_Date(date_key),
                    FOREIGN KEY (product_key) REFERENCES Dim_Product(product_key),
                    FOREIGN KEY (customer_key) REFERENCES Dim_Customer(customer_key),
                    FOREIGN KEY (region_key) REFERENCES Dim_Region(region_key)
                );
            """))

            conn.execute(text("CREATE INDEX idx_fact_date ON Fact_Sales(date_key);"))
            conn.execute(text("CREATE INDEX idx_fact_product ON Fact_Sales(product_key);"))
            conn.execute(text("CREATE INDEX idx_fact_customer ON Fact_Sales(customer_key);"))
            conn.execute(text("CREATE INDEX idx_fact_region ON Fact_Sales(region_key);"))
            conn.execute(text("CREATE INDEX idx_fact_order ON Fact_Sales(order_id);"))

            conn.execute(text("""
                CREATE VIEW vw_sales_performance AS
                SELECT
                    f.sales_key,
                    f.order_id,
                    f.order_line_id,
                    d.full_date AS order_date,
                    d.year,
                    d.quarter,
                    d.month,
                    d.month_name,
                    p.product_id,
                    p.product_name,
                    p.category,
                    c.customer_id,
                    c.customer_name,
                    c.customer_segment,
                    r.region_name AS region,
                    r.country,
                    f.quantity,
                    f.unit_price,
                    f.unit_cost,
                    f.discount_rate,
                    f.discount_tier,
                    f.revenue,
                    f.cost,
                    f.profit,
                    f.profit_margin_pct,
                    f.profitability_status
                FROM Fact_Sales f
                JOIN Dim_Date d ON f.date_key = d.date_key
                JOIN Dim_Product p ON f.product_key = p.product_key
                JOIN Dim_Customer c ON f.customer_key = c.customer_key
                JOIN Dim_Region r ON f.region_key = r.region_key;
            """))

    logger.info(f"Initialized Star Schema on {dialect.upper()} successfully.")
