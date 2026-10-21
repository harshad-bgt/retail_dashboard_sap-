# SAP Analytics Cloud (SAC) Story Design Specification

**Story Title:** Retail Sales Intelligence & Executive Performance Suite  
**Visual Theme:** SAP Horizon (Clean Enterprise Light Theme)  
**Primary Accent:** `#0070F3` (SAP Horizon Blue)  
**Positive / Profit Accent:** `#00A896` (Emerald Green)  
**Alert / Loss Accent:** `#E63946` (Signal Red)  
**Background:** `#F5F6F8` (Canvas Off-White)  
**Typography:** 72 / Roboto / Inter  

---

## Story Architecture: 4 Canvas Pages

```
┌────────────────────────────────────────────────────────────────────────┐
│  SAC Story Filter Bar: [Date: 2024 - 2025] [Category: All] [Region: All] [Segment: All]
├───────────────┬──────────────────────┬────────────────────────────────┤
│ Page 1:       │ Page 2:              │ Page 3:                        │ Page 4:
│ Executive     │ Product Catalog &    │ Customer Intelligence &        │ Predictive 3-Month
│ Overview      │ Regional Performance │ Discount Sensitivity           │ Sales Forecast
└───────────────┴──────────────────────┴────────────────────────────────┴────────────────┘
```

---

## Page 1: Executive Performance & Financial KPIs

### Section A: Enterprise KPI Ribbon (Top Row)
Six standardized numeric KPI tiles with comparison sparklines:
1. **Total Revenue:** `$990,871.85` (Subtext: Realized gross sales)
2. **Total Net Profit:** `$388,117.85` (Color: `#00A896`)
3. **Net Profit Margin:** `39.17%` (Benchmark: >35% Target met)
4. **Distinct Orders:** `2,400` orders
5. **Distinct Customers:** `350` active accounts
6. **Average Order Value (AOV):** `$412.86` per order

### Section B: Monthly Revenue & Profit Trajectory (Full-Width Chart)
- **Chart Type:** Dual-Axis Line / Area Combination Chart
- **Primary Measure (Left Axis):** `Revenue ($)` (Line color `#0070F3`, thickness 3px)
- **Secondary Measure (Right Axis):** `Profit ($)` (Shaded Area `#00A896`, alpha 0.2)
- **Dimension:** `Date` (Drill level: Month)
- **Interactivity:** Linked analysis active; clicking on a month filters downstream charts.

---

## Page 2: Product Catalog & Regional Analytics

### Left Column: Category & Product Performance
1. **Category Revenue Contribution:**
   - **Chart Type:** Horizontal Bar Chart
   - **Dimension:** `Category` (Sorted by Revenue descending)
   - **Measure:** `Revenue ($)`
   - **Color:** `#0070F3`
   - **Data Labels:** Formatted as `$K` with percentage of total share.

2. **Top 5 and Bottom 5 Products by Profitability:**
   - **Chart Type:** Ranked Comparison Bar Chart
   - **Leaders:** Monitors, Standing Desks, Executive Chairs.
   - **Laggards / Optimization:** Low-margin clearance supplies with negative margin alerts.

### Right Column: Regional Geographic Intelligence
1. **Regional Sales & Profit Comparison:**
   - **Chart Type:** Clustered Column Chart
   - **Dimension:** `Region` (North America, EMEA, Asia Pacific, Latin America)
   - **Measures:** `Revenue ($)` and `Profit ($)`
   - **Threshold:** Regional margin benchmark line set at `38%`.

2. **Geographical Bubble / Tree Map:**
   - **Hierarchy:** `Region` > `Country`
   - **Size:** `Revenue`
   - **Color Intensity:** `Profit Margin %`

---

## Page 3: Customer Segments & Discount Elasticity

### Left Column: Customer Segment Breakdown
1. **Segment Revenue & Volume Contribution:**
   - **Chart Type:** Donut Chart
   - **Dimension:** `Customer_Segment` (Consumer: 50.1%, Corporate: 32.2%, Home Office: 17.7%)
   - **Measure:** `Revenue`

2. **Average Order Value by Segment:**
   - **Chart Type:** Column Chart
   - **Highlight:** Corporate accounts deliver higher AOV ($485+) compared to Consumer ($365+).

### Right Column: Discount Impact & Margin Sensitivity
1. **Margin Degradation by Discount Tier:**
   - **Chart Type:** Waterfall / Variance Chart
   - **Dimension:** `Discount_Tier` (0%, 1-10%, 11-20%, >20%)
   - **Insight Callout:** Shows margin shrinking from 43.8% at full price to 4.2% at discounts >20%.

---

## Page 4: Predictive 3-Month Sales Forecasting

### Chart: Short-Term Revenue Horizon (2024 to Q1 2026)
- **Chart Type:** Time Series Line Chart with Version Comparison
- **Historical Horizon (Jan 2024 – Dec 2025):** Solid blue line (`#0070F3`)
- **Forecast Horizon (Jan 2026 – Mar 2026):** Dotted red line (`#E63946`) with diamonds
- **Prediction Bounds:** 80% Confidence Interval envelope (Lower: ~$41.6K, Upper: ~$64.8K)
- **Summary Forecast Metric Cards:**
  - **Jan 2026 Estimate:** `$49,178.45`
  - **Feb 2026 Estimate:** `$52,979.03`
  - **Mar 2026 Estimate:** `$51,776.76`
  - **Model Type:** Ridge Autoregressive Regressor (MAE: $8,754.37, MAPE: 15.12%)

---

## Interactivity & Filter Governance
1. **Story Filters:**
   - `Date Range Slider` (2024 - 2025)
   - `Category Dropdown` (Multi-select)
   - `Region Dropdown` (Multi-select)
   - `Customer Segment Radio`
2. **Linked Analysis:**
   - Selecting a Category filters all Product and Regional charts.
   - Selecting a Region updates customer segment statistics.
