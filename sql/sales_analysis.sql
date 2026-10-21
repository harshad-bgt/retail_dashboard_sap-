-- ==============================================================================
-- Retail Sales Analysis - SQL Business Queries
-- ==============================================================================
-- Dataset: Tableau Sample Superstore (9,994 retail transaction records)
-- Compatible with: MySQL 8.0+, SQLite 3, PostgreSQL
--
-- Table Loading Instructions:
--   To run these queries locally, load 'data/retail_sales.csv' into a table named
--   'retail_sales'. The notebook (notebooks/retail_sales_analysis.ipynb) also executes
--   these queries directly via Python's built-in sqlite3 engine.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. Executive Summary: Core Business KPIs
-- Question: What are the total sales, total profit, overall margin, and average order value?
-- ------------------------------------------------------------------------------
SELECT
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100.0, 2) AS overall_profit_margin_pct,
    COUNT(DISTINCT Order_ID) AS total_orders,
    COUNT(DISTINCT Customer_ID) AS total_customers,
    SUM(Quantity) AS total_units_sold,
    ROUND(SUM(Sales) / COUNT(DISTINCT Order_ID), 2) AS average_order_value
FROM retail_sales;

-- ------------------------------------------------------------------------------
-- 2. Sales and Profit by Category
-- Question: Which high-level categories generate the most revenue and margin?
-- ------------------------------------------------------------------------------
SELECT
    Category,
    COUNT(DISTINCT Order_ID) AS total_orders,
    SUM(Quantity) AS units_sold,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100.0, 2) AS profit_margin_pct
FROM retail_sales
GROUP BY Category
ORDER BY total_sales DESC;

-- ------------------------------------------------------------------------------
-- 3. Sub-Category Performance (Identifying Profit Leaders vs Loss-Makers)
-- Question: Which specific sub-categories drive profits and which operate at a loss?
-- ------------------------------------------------------------------------------
SELECT
    Category,
    Sub_Category,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100.0, 2) AS profit_margin_pct
FROM retail_sales
GROUP BY Category, Sub_Category
ORDER BY total_profit DESC;

-- ------------------------------------------------------------------------------
-- 4. Regional Performance Breakdown
-- Question: How do sales, profitability, and customer purchasing power vary across regions?
-- ------------------------------------------------------------------------------
SELECT
    Region,
    COUNT(DISTINCT Order_ID) AS total_orders,
    COUNT(DISTINCT Customer_ID) AS unique_customers,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100.0, 2) AS profit_margin_pct,
    ROUND(SUM(Sales) / COUNT(DISTINCT Order_ID), 2) AS average_order_value
FROM retail_sales
GROUP BY Region
ORDER BY total_sales DESC;

-- ------------------------------------------------------------------------------
-- 5. Customer Segment Analysis
-- Question: Which customer cohort generates the highest sales volume and basket size?
-- ------------------------------------------------------------------------------
SELECT
    Segment,
    COUNT(DISTINCT Order_ID) AS total_orders,
    COUNT(DISTINCT Customer_ID) AS unique_customers,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100.0, 2) AS profit_margin_pct,
    ROUND(SUM(Sales) / COUNT(DISTINCT Order_ID), 2) AS average_order_value
FROM retail_sales
GROUP BY Segment
ORDER BY total_sales DESC;

-- ------------------------------------------------------------------------------
-- 6. Discount Impact on Profitability
-- Question: Does higher discounting erode profit margins?
-- ------------------------------------------------------------------------------
SELECT
    CASE
        WHEN Discount = 0 THEN '0% (No Discount)'
        WHEN Discount <= 0.20 THEN '1-20% (Low to Moderate)'
        ELSE '>20% (High Discount)'
    END AS discount_tier,
    COUNT(*) AS total_transactions,
    ROUND(AVG(Discount) * 100.0, 1) AS avg_discount_pct,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100.0, 2) AS profit_margin_pct
FROM retail_sales
GROUP BY discount_tier
ORDER BY total_sales DESC;

-- ------------------------------------------------------------------------------
-- 7. Top 10 Most Profitable Products
-- Question: Which individual products contribute the most to the bottom line?
-- ------------------------------------------------------------------------------
SELECT
    Product_Name,
    Category,
    Sub_Category,
    SUM(Quantity) AS units_sold,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100.0, 2) AS profit_margin_pct
FROM retail_sales
GROUP BY Product_Name, Category, Sub_Category
ORDER BY total_profit DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- 8. Top 10 Loss-Making Products (Optimization & Pricing Review Targets)
-- Question: Which items are incurring the largest cumulative net losses?
-- ------------------------------------------------------------------------------
SELECT
    Product_Name,
    Category,
    Sub_Category,
    SUM(Quantity) AS units_sold,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100.0, 2) AS profit_margin_pct
FROM retail_sales
GROUP BY Product_Name, Category, Sub_Category
ORDER BY total_profit ASC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- 9. Shipping Mode Distribution
-- Question: Which fulfillment method is most popular, and does it impact profitability?
-- ------------------------------------------------------------------------------
SELECT
    Ship_Mode,
    COUNT(DISTINCT Order_ID) AS total_orders,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100.0, 2) AS profit_margin_pct
FROM retail_sales
GROUP BY Ship_Mode
ORDER BY total_orders DESC;

-- ------------------------------------------------------------------------------
-- 10. Annual Year-over-Year (YoY) Sales & Profit Growth
-- Question: How has annual performance evolved over the four-year period?
-- ------------------------------------------------------------------------------
SELECT
    SUBSTR(Order_Date, 1, 4) AS sales_year,
    COUNT(DISTINCT Order_ID) AS total_orders,
    ROUND(SUM(Sales), 2) AS annual_sales,
    ROUND(SUM(Profit), 2) AS annual_profit,
    ROUND((SUM(Profit) / SUM(Sales)) * 100.0, 2) AS profit_margin_pct
FROM retail_sales
GROUP BY sales_year
ORDER BY sales_year ASC;
