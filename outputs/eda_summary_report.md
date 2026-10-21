# Retail Sales Intelligence: Exploratory Data Analysis & Business Report

**Executive Summary & Statistical Overview**
- **Analysis Period:** January 1, 2024 to December 31, 2025 (24 Consecutive Calendar Months)
- **Total Validated Records:** 4,034 transaction line items
- **Total Distinct Orders:** 2,400
- **Total Distinct Customers:** 350
- **Total Realized Revenue:** $990,871.85
- **Total Cost of Goods Sold:** $602,754.00
- **Total Net Profit:** $388,117.85
- **Enterprise Profit Margin:** 39.17%
- **Average Order Value (AOV):** $412.86

---

## 1. Monthly Revenue & Profit Dynamics
![Monthly Sales Trend](figures/01_monthly_sales_trend.png)

### Key Observations:
- Revenue exhibits healthy year-over-year expansion (+21.4% growth from 2024 to 2025).
- Strong seasonal spikes materialize consistently in **November and December (Q4)** due to year-end holiday retail procurement.
- A secondary, corporate-driven bump is observed in **March (Q1)**, coinciding with fiscal year-end budget cycles.
- Net profit tracks revenue in direction, but exhibits margin compression during promotional periods.

---

## 2. Category Performance & Margin Profile
![Category Performance](figures/02_category_performance.png)

### Business Interpretation:
- **Electronics & Furniture** drive over 68% of enterprise gross sales volume, primarily due to higher average unit prices ($380+ for Monitors, $520 for Standing Desks).
- **Office Supplies & Apparel** provide smaller average transaction sizes but boast exceptionally resilient net profit margins (~48% to 52%), offsetting lower absolute top-line ticket sizes.

---

## 3. Regional Contribution & Profitability
![Regional Performance](figures/03_regional_performance.png)

### Business Interpretation:
- **North America** represents the primary regional revenue pillar (42.1% share), backed by the largest corporate customer base.
- **EMEA** stands as the second largest region with balanced consumer and corporate demand.
- **Asia Pacific** demonstrates the fastest monthly order growth rate (+24% YoY), indicating an expanding footprint.
- All four regions maintain healthy blended operating margins between 38% and 41%, demonstrating consistent regional pricing discipline.

---

## 4. Discount Sensitivity & Margin Erosion
![Discount vs Profitability](figures/04_discount_vs_profitability.png)

### Statistical & Financial Analysis:
- Transactions sold at **0% to 10% discount** deliver healthy net margins exceeding 42%.
- Beyond the **15% discount threshold**, profit margin drops precipitously to ~22%.
- For items discounted at **25% to 30%**, profit margins on lower-margin hardware drop below 5%, with some promotional lines entering breakeven or negative territory.
> **Note on Causation vs Correlation:** While heavy discounts strongly correlate with reduced profit margins (-0.46 correlation coefficient), the discounting policy itself is often applied deliberately to clearance items or loss-leaders to stimulate basket volume. Management should avoid reflexive discounting across premium product lines.

---

## 5. Correlation Heatmap & Numerical Findings
![Correlation Heatmap](figures/07_correlation_matrix.png)

### Key Metric Relationships:
1. **Revenue and Cost (r = +0.87):** Strong expected linear alignment driven by base product manufacturing expenses.
2. **Revenue and Quantity (r = +0.48):** Moderate positive relationship; order line dollar value is influenced more heavily by product tier (unit price) than pure item count.
3. **Discount Rate and Profit Margin (r = -0.46):** Clear negative correlation, substantiating the margin erosion observed in discount tier analysis.
4. **Profit and Revenue (r = +0.82):** High co-movement confirming top-line volume growth translates effectively to gross bottom-line dollars.

---

## 6. Actionable Management Recommendations
1. **Tiered Discount Governance:** Cap standard sales representative discount discretion at 15%. Require director approval for promotional markdowns exceeding 20%.
2. **Product Bundling Strategy:** Bundle high-margin Office Supplies (staplers, paper, organizers) with flagship Electronics (monitors, docking stations) to protect overall transaction margin.
3. **Regional Inventory Allocation:** Increase Q3 buffer stocks in North America and EMEA warehouses to prevent stockouts during the verified November–December demand surge.
