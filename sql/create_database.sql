-- ==============================================================================
-- Retail Sales Intelligence & Forecasting Platform
-- Database Creation Script (MySQL 8.0+)
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS retail_sales_dw
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE retail_sales_dw;

-- Verify database creation
SELECT DATABASE() AS current_database, CURRENT_TIMESTAMP AS initialized_at;
