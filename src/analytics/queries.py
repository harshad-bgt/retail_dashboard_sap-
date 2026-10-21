"""
Retail Sales Intelligence & Forecasting Platform
SQL Analytics Engine
==============================================================================
Executes structured analytical queries against the Star Schema database.
Supports both MySQL and SQLite dialect nuances.
==============================================================================
"""

from typing import Dict, Any, List
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.database.connection import get_db_engine


def get_executive_kpis(engine: Engine = None) -> Dict[str, Any]:
    """Retrieves top-level enterprise KPIs from Fact_Sales."""
    if engine is None:
        engine, _ = get_db_engine()

    sql = """
        SELECT
            ROUND(SUM(f.revenue), 2) AS total_revenue,
            ROUND(SUM(f.cost), 2) AS total_cost,
            ROUND(SUM(f.profit), 2) AS total_profit,
            ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS profit_margin_pct,
            COUNT(DISTINCT f.order_id) AS total_orders,
            COUNT(DISTINCT f.customer_key) AS total_customers,
            SUM(f.quantity) AS total_units_sold,
            ROUND(SUM(f.revenue) / COUNT(DISTINCT f.order_id), 2) AS average_order_value
        FROM Fact_Sales f;
    """
    with engine.connect() as conn:
        res = conn.execute(text(sql)).mappings().first()
        return dict(res)


def get_monthly_trends(engine: Engine = None) -> pd.DataFrame:
    """Retrieves monthly revenue and profit trends ordered chronologically."""
    if engine is None:
        engine, _ = get_db_engine()

    sql = """
        SELECT
            d.year,
            d.month,
            d.month_name,
            COUNT(DISTINCT f.order_id) AS orders_count,
            SUM(f.quantity) AS units_sold,
            ROUND(SUM(f.revenue), 2) AS monthly_revenue,
            ROUND(SUM(f.cost), 2) AS monthly_cost,
            ROUND(SUM(f.profit), 2) AS monthly_profit,
            ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS monthly_margin_pct
        FROM Fact_Sales f
        JOIN Dim_Date d ON f.date_key = d.date_key
        GROUP BY d.year, d.month, d.month_name
        ORDER BY d.year ASC, d.month ASC;
    """
    with engine.connect() as conn:
        return pd.read_sql(sql, con=conn)


def get_category_performance(engine: Engine = None) -> pd.DataFrame:
    """Retrieves category-level sales, profits, and margin breakdown."""
    if engine is None:
        engine, _ = get_db_engine()

    sql = """
        SELECT
            p.category,
            COUNT(DISTINCT f.order_id) AS orders_count,
            SUM(f.quantity) AS total_units,
            ROUND(SUM(f.revenue), 2) AS category_revenue,
            ROUND(SUM(f.cost), 2) AS category_cost,
            ROUND(SUM(f.profit), 2) AS category_profit,
            ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS profit_margin_pct
        FROM Fact_Sales f
        JOIN Dim_Product p ON f.product_key = p.product_key
        GROUP BY p.category
        ORDER BY category_revenue DESC;
    """
    with engine.connect() as conn:
        return pd.read_sql(sql, con=conn)


def get_regional_performance(engine: Engine = None) -> pd.DataFrame:
    """Retrieves regional revenue, profit, and customer distribution."""
    if engine is None:
        engine, _ = get_db_engine()

    sql = """
        SELECT
            r.region_name AS region,
            COUNT(DISTINCT f.order_id) AS orders_count,
            COUNT(DISTINCT f.customer_key) AS unique_customers,
            ROUND(SUM(f.revenue), 2) AS region_revenue,
            ROUND(SUM(f.cost), 2) AS region_cost,
            ROUND(SUM(f.profit), 2) AS region_profit,
            ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS profit_margin_pct,
            ROUND(SUM(f.revenue) / COUNT(DISTINCT f.order_id), 2) AS regional_aov
        FROM Fact_Sales f
        JOIN Dim_Region r ON f.region_key = r.region_key
        GROUP BY r.region_name
        ORDER BY region_revenue DESC;
    """
    with engine.connect() as conn:
        return pd.read_sql(sql, con=conn)


def get_product_rankings(engine: Engine = None, limit: int = 5) -> Dict[str, pd.DataFrame]:
    """Retrieves top products by revenue and lowest margin products."""
    if engine is None:
        engine, _ = get_db_engine()

    sql_top_rev = f"""
        SELECT
            p.product_id,
            p.product_name,
            p.category,
            SUM(f.quantity) AS units_sold,
            ROUND(SUM(f.revenue), 2) AS revenue,
            ROUND(SUM(f.profit), 2) AS profit,
            ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS profit_margin_pct
        FROM Fact_Sales f
        JOIN Dim_Product p ON f.product_key = p.product_key
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY revenue DESC
        LIMIT {limit};
    """

    sql_bottom_margin = f"""
        SELECT
            p.product_id,
            p.product_name,
            p.category,
            SUM(f.quantity) AS units_sold,
            ROUND(SUM(f.revenue), 2) AS revenue,
            ROUND(SUM(f.profit), 2) AS profit,
            ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS profit_margin_pct
        FROM Fact_Sales f
        JOIN Dim_Product p ON f.product_key = p.product_key
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY profit_margin_pct ASC
        LIMIT {limit};
    """

    with engine.connect() as conn:
        top_rev = pd.read_sql(sql_top_rev, con=conn)
        bottom_margin = pd.read_sql(sql_bottom_margin, con=conn)
        return {"top_revenue": top_rev, "bottom_margin": bottom_margin}


def get_customer_segment_analysis(engine: Engine = None) -> pd.DataFrame:
    """Retrieves customer segment metrics."""
    if engine is None:
        engine, _ = get_db_engine()

    sql = """
        SELECT
            c.customer_segment,
            COUNT(DISTINCT f.order_id) AS orders_count,
            COUNT(DISTINCT f.customer_key) AS unique_customers,
            ROUND(SUM(f.revenue), 2) AS segment_revenue,
            ROUND(SUM(f.profit), 2) AS segment_profit,
            ROUND(SUM(f.revenue) / COUNT(DISTINCT f.order_id), 2) AS average_order_value,
            ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS profit_margin_pct
        FROM Fact_Sales f
        JOIN Dim_Customer c ON f.customer_key = c.customer_key
        GROUP BY c.customer_segment
        ORDER BY segment_revenue DESC;
    """
    with engine.connect() as conn:
        return pd.read_sql(sql, con=conn)


def get_discount_impact_analysis(engine: Engine = None) -> pd.DataFrame:
    """Retrieves discount tier impact on revenue and profitability."""
    if engine is None:
        engine, _ = get_db_engine()

    sql = """
        SELECT
            f.discount_tier,
            COUNT(f.sales_key) AS line_items,
            ROUND(AVG(f.discount_rate) * 100.0, 2) AS avg_discount_pct,
            ROUND(SUM(f.revenue), 2) AS total_revenue,
            ROUND(SUM(f.profit), 2) AS total_profit,
            ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS profit_margin_pct
        FROM Fact_Sales f
        GROUP BY f.discount_tier
        ORDER BY avg_discount_pct ASC;
    """
    with engine.connect() as conn:
        return pd.read_sql(sql, con=conn)
