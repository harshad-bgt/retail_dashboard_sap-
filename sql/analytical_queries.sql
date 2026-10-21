-- ==============================================================================
-- Retail Sales Intelligence & Forecasting Platform
-- Business Analytics & KPI SQL Queries
-- ==============================================================================

USE retail_sales_dw;

-- ------------------------------------------------------------------------------
-- 1. Executive Summary KPIs
-- Answers: How much revenue and profit does the business generate?
-- ------------------------------------------------------------------------------
SELECT
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(SUM(f.cost), 2) AS total_cost,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS overall_profit_margin_pct,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(DISTINCT f.customer_key) AS total_customers,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.revenue) / COUNT(DISTINCT f.order_id), 2) AS average_order_value
FROM Fact_Sales f;

-- ------------------------------------------------------------------------------
-- 2. Monthly Revenue & Profit Trends
-- Answers: How has monthly revenue changed over time?
-- ------------------------------------------------------------------------------
SELECT
    d.year,
    d.month,
    d.month_name,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.quantity) AS units_sold,
    ROUND(SUM(f.revenue), 2) AS monthly_revenue,
    ROUND(SUM(f.cost), 2) AS monthly_cost,
    ROUND(SUM(f.profit), 2) AS monthly_profit,
    ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS monthly_margin_pct
FROM Fact_Sales f
JOIN Dim_Date d ON f.date_key = d.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year ASC, d.month ASC;

-- ------------------------------------------------------------------------------
-- 3. Category Performance Analysis
-- Answers: Which categories perform best in revenue and profitability?
-- ------------------------------------------------------------------------------
SELECT
    p.category,
    COUNT(DISTINCT f.order_id) AS orders_count,
    SUM(f.quantity) AS total_units,
    ROUND(SUM(f.revenue), 2) AS category_revenue,
    ROUND(SUM(f.profit), 2) AS category_profit,
    ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS profit_margin_pct,
    ROUND(SUM(f.revenue) * 100.0 / (SELECT SUM(revenue) FROM Fact_Sales), 2) AS revenue_share_pct
FROM Fact_Sales f
JOIN Dim_Product p ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY category_revenue DESC;

-- ------------------------------------------------------------------------------
-- 4. Regional Performance Breakdown
-- Answers: Which regions generate the most revenue and profit?
-- ------------------------------------------------------------------------------
SELECT
    r.region_name,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(DISTINCT f.customer_key) AS total_customers,
    ROUND(SUM(f.revenue), 2) AS region_revenue,
    ROUND(SUM(f.profit), 2) AS region_profit,
    ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS profit_margin_pct,
    ROUND(SUM(f.revenue) / COUNT(DISTINCT f.order_id), 2) AS regional_aov
FROM Fact_Sales f
JOIN Dim_Region r ON f.region_key = r.region_key
GROUP BY r.region_name
ORDER BY region_revenue DESC;

-- ------------------------------------------------------------------------------
-- 5. Top 5 Products by Revenue
-- ------------------------------------------------------------------------------
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(f.quantity) AS units_sold,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS profit_margin_pct
FROM Fact_Sales f
JOIN Dim_Product p ON f.product_key = p.product_key
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 5;

-- ------------------------------------------------------------------------------
-- 6. Top 5 Products by Profit
-- ------------------------------------------------------------------------------
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(f.quantity) AS units_sold,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS profit_margin_pct
FROM Fact_Sales f
JOIN Dim_Product p ON f.product_key = p.product_key
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_profit DESC
LIMIT 5;

-- ------------------------------------------------------------------------------
-- 7. Lowest-Profit Margin Products (Risk & Optimization Targets)
-- ------------------------------------------------------------------------------
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(f.quantity) AS units_sold,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS profit_margin_pct
FROM Fact_Sales f
JOIN Dim_Product p ON f.product_key = p.product_key
GROUP BY p.product_id, p.product_name, p.category
ORDER BY profit_margin_pct ASC
LIMIT 5;

-- ------------------------------------------------------------------------------
-- 8. Customer Segment Performance & Average Order Value
-- Answers: How do customer segments differ in purchasing power?
-- ------------------------------------------------------------------------------
SELECT
    c.customer_segment,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(DISTINCT f.customer_key) AS unique_customers,
    ROUND(SUM(f.revenue), 2) AS segment_revenue,
    ROUND(SUM(f.profit), 2) AS segment_profit,
    ROUND(SUM(f.revenue) / COUNT(DISTINCT f.order_id), 2) AS average_order_value,
    ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS profit_margin_pct
FROM Fact_Sales f
JOIN Dim_Customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_segment
ORDER BY segment_revenue DESC;

-- ------------------------------------------------------------------------------
-- 9. Discount Impact on Profitability Analysis
-- Answers: How do discounts relate to profitability?
-- ------------------------------------------------------------------------------
SELECT
    f.discount_tier,
    COUNT(f.sales_key) AS total_line_items,
    ROUND(AVG(f.discount_rate) * 100.0, 2) AS avg_discount_pct,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.revenue)) * 100.0, 2) AS profit_margin_pct
FROM Fact_Sales f
GROUP BY f.discount_tier
ORDER BY avg_discount_pct ASC;
