# SAP Analytics Cloud (SAC) Architecture & Setup Documentation

**Project:** Retail Sales Intelligence & Forecasting Platform  
**Target BI Solution:** SAP Analytics Cloud (Enterprise Edition / SAC Free Tier / Trial)  
**Data Sources:** MySQL Relational Data Warehouse / Cleaned Analytical Extracts (`data/processed/`)  

---

## 1. Architectural Overview & Connectivity Strategy

The platform supports two official SAC connectivity architectures:

```
[MySQL / Relational DW] 
       │
       ├──► Method A: Live Data Connection (SAP Cloud Connector + SAC Agent)
       │              └──► Real-time queries push down to MySQL Star Schema
       │
       └──► Method B: Import Data Connection (Scheduled or Manual Acquire)
                      └──► Loads data directly into SAC Cloud In-Memory Model
                            (Supported via MySQL JDBC or CSV Drag-and-Drop)
```

### Method A: Live Data Connection via SAP Cloud Connector & SAC Agent
1. **SAP Cloud Connector (SCC):** Installed on premise or cloud VM hosting the MySQL instance. Configures an SSL tunnel into your SAC subaccount.
2. **SAP Analytics Cloud Agent:** Deployed on Apache Tomcat with the MySQL Connector/J driver (`mysql-connector-j-8.x.jar`).
3. **Data Source Mapping:** Exposes `vw_sales_performance` directly. Aggregations, filters, and calculations execute natively inside the database.

### Method B: Import Data Connection (Recommended for Portfolio & Fast Prototyping)
1. In SAC, navigate to **Connections** > **Add Connection** > **SQL Database**.
2. Provide JDBC URL: `jdbc:mysql://<host>:3306/retail_sales_dw`.
3. Select tables: `Fact_Sales`, `Dim_Date`, `Dim_Product`, `Dim_Customer`, `Dim_Region` (or point directly to the analytical extract).
4. Alternatively, use the pre-generated model file created by the ETL pipeline:
   - **Primary Model Extract:** [`data/processed/sac_prepared_sales_model.csv`](../data/processed/sac_prepared_sales_model.csv)
   - **Forecast Model Extract:** [`data/processed/sac_forecast_import.csv`](../data/processed/sac_forecast_import.csv)

---

## 2. SAC Analytical Model Configuration (New Model Workflow)

Navigate to **Modeler** > **New Model** > **Start with data**. Upload `sac_prepared_sales_model.csv`.

### Step 1: Dimension Setup
| SAC Dimension Name | Column Source | Type | Hierarchy / Attributes | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Date** | `Date` (YYYY-MM-DD) | Date Dimension | Time Hierarchy: Year > Quarter > Month | Defines chronological granularity (2024-01-01 to 2025-12-31) |
| **Product** | `Product_Name` | Generic Dimension | **Parent:** `Category`<br>**ID:** `Product_ID` | Master product dimension with 2-level category hierarchy |
| **Category** | `Category` | Generic Dimension | Attribute of Product | Top-level catalog grouping (Electronics, Furniture, etc.) |
| **Customer** | `Customer_Name` | Generic Dimension | **Attribute:** `Customer_Segment`<br>**ID:** `Customer_ID` | Customer entity with segment profiling |
| **Region** | `Region` | Organization / Generic | **Parent:** Global<br>**Child:** `Country` | Geographic hierarchy for regional sales rollups |
| **Order_ID** | `Order_ID` | Generic Dimension | - | Unique transaction order identifier for distinct count logic |
| **Discount_Tier**| `Discount_Tier` | Generic Dimension | - | Categorical bucket (0%, Low, Medium, High) |
| **Version** | Version Dimension | Version | `Actual` and `Forecast` | Separates historical realized figures from ML projections |

### Step 2: Base Measures Configuration
| SAC Measure Name | Source Column | Aggregation Type | Decimal Places | Unit / Format |
| :--- | :--- | :--- | :--- | :--- |
| **Revenue** | `Revenue` | `SUM` | 2 | `$#,##0.00` |
| **Cost** | `Cost` | `SUM` | 2 | `$#,##0.00` |
| **Profit** | `Profit` | `SUM` | 2 | `$#,##0.00` |
| **Quantity** | `Quantity` | `SUM` | 0 | `#,##0` |
| **Discount_Rate**| `Discount_Rate` | `AVERAGE` | 4 | `0.0%` |

### Step 3: Calculated Measures & Business Formulas
In the SAC Model Formula Builder, configure the following calculated measures:

1. **Profit Margin %:**
   ```formula
   ([Profit] / [Revenue]) * 100
   ```
   - Format: `Percentage (0.00%)`
   - Exception Aggregation: `None` (calculated after aggregation)

2. **Average Order Value (AOV):**
   ```formula
   [Revenue] / COUNT([Order_ID])
   ```
   - Format: `Currency ($#,##0.00)`

3. **Profitability Status Indicator (Conditional):**
   ```formula
   IF([Profit_Margin_Pct] < 0, "Loss Making", IF([Profit_Margin_Pct] <= 15, "Low Margin", "Healthy"))
   ```

---

## 3. Integrating the Short-Term Forecast into SAC

SAC supports two distinct methods for presenting the short-term forecast:

### Option 1: Native SAC Smart Predict / Time Series Forecast
1. In the SAC Story, select the **Monthly Revenue Line Chart**.
2. Click the **More Options (...)** icon > **Forecast** > **Automatic Forecast** or **Linear Regression**.
3. Set Forecast Horizon: `3 Months`.
4. Review the auto-generated confidence bounds and prediction quality score.

### Option 2: Uploading Verified Python ML Projections (Recommended for Portfolio Alignment)
1. In the Model Modeler, open the `Version` dimension.
2. Ensure both `Actual` and `Forecast` versions are active.
3. Import [`data/processed/sac_forecast_import.csv`](../data/processed/sac_forecast_import.csv) into the model.
4. Historical months (2024-01 to 2025-12) populate the `Actual` version.
5. Projected months (2026-01 to 2026-03) populate the `Forecast` version.
6. In the SAC Story, display a **Variance Chart** or a combined **Time Series Chart** showing `Actual` transitioning into `Forecast` with a dotted line style.

---

## 4. Verification & Quality Assurance Checklist

Before finalizing the SAC Model:
- [x] Total Gross Revenue matches: **$990,871.85**
- [x] Total Net Profit matches: **$388,117.85**
- [x] Overall Profit Margin matches: **39.17%**
- [x] Distinct Orders count matches: **2,400**
- [x] Distinct Customers count matches: **350**
- [x] Date hierarchy correctly drills from Year > Quarter > Month.
- [x] Story filters (Date, Region, Category, Segment) dynamically recalculate all linked charts.
