# Demonstration & Screen Recording Guide

**Project:** Retail Sales Intelligence & Forecasting Platform  
**Target Showcase:** LinkedIn Video Post &bull; GitHub Portfolio &bull; Technical Interview Walkthrough  
**Target Duration:** 90 – 120 Seconds  
**One-Command Startup:** `python run_demo.py`  

---

## 1. Pre-Recording Technical Setup

### Recommended Recording Configuration
- **Resolution:** 1080p Full HD (1920 &times; 1080)
- **Aspect Ratio:** 16:9 Landscape
- **Browser:** Google Chrome or Microsoft Edge
- **Browser Zoom:** 100% (Press `Ctrl + 0` to reset zoom)
- **Window State:** Clean window with bookmarks bar hidden (`Ctrl + Shift + B`)
- **Audio:** Crisp microphone input, noise suppression enabled (no keyboard clicks)
- **Recording Tool:** OBS Studio, Loom, Camtasia, or Windows Snipping Tool (Win + Shift + R)

---

## 2. One-Command Demonstration Startup

Open PowerShell or your command terminal in the project root:

```powershell
# Navigate to the repository
cd "d:\Linkedin Post\SAP\Project"

# Launch the unified demo orchestrator
python run_demo.py
```

### What Happens Automatically:
1. Validates the Python environment, dependencies, and file paths.
2. Connects to MySQL if configured, or seamlessly engages the local SQLite Star Schema warehouse.
3. Verifies that all 4,034 transactions are populated in `Fact_Sales` and all dimensions.
4. Confirms that the Ridge ML forecast model artifacts are up to date.
5. Runs an automated reconciliation check: verifies all 8 core metrics match between SQL and Python.
6. Starts the local presentation HTTP server.
7. Automatically launches your default web browser at `http://127.0.0.1:8501`.

---

## 3. Pre-Recording Readiness Checklist

Run through this 10-point checklist before hitting "Record":

- [ ] **1. Dashboard Running:** `http://127.0.0.1:8501` is loaded in your browser with zero console errors.
- [ ] **2. KPIs Displaying Correctly:**
  - Revenue: **$990,871.85**
  - Net Profit: **$388,117.85**
  - Profit Margin: **39.17%**
  - Orders: **2,400**
  - AOV: **$412.86**
- [ ] **3. Green Reconciliation Badge Visible:** "SQL & Python 100% Reconciled" badge displays in Section 1.
- [ ] **4. Chart Rendering:** Trends, Forecast, Category, Region, and Segment charts are rendered smoothly.
- [ ] **5. Presentation Mode Tested:** Click "Presentation Mode" button in the top right. Verify the floating navigation bar appears at the bottom.
- [ ] **6. Architecture Modal Tested:** Click "Data Model & Architecture" to confirm the Star Schema diagram pops up smoothly.
- [ ] **7. Filters Responsive:** Test toggling Year to "2025" and verify all KPIs update instantly. Reset filters before recording.
- [ ] **8. Clean Browser Viewport:** Address bar clean, developer console closed, tabs closed except the demo.
- [ ] **9. Audio Check:** Microphone levels tested (target -6dB to -12dB).
- [ ] **10. Script Ready:** Review the timing script below.

---

## 4. 90 – 120 Second Demonstration Script

| Time Elapsed | Segment Title | On-Screen Action | Spoken Narration Script |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:10** | **Introduction & Overview** | Show top of dashboard at Section 1. Move cursor smoothly across the title and green reconciliation badge. | *"Hello everyone! Today I'm showcasing an end-to-end Retail Sales Intelligence and Forecasting Platform built using Python ETL, a SQL Star Schema warehouse, and SAP Analytics Cloud."* |
| **0:10 – 0:25** | **Executive KPIs & Reconciliation** | Hover over the Revenue, Profit, Margin, and AOV cards. Point to the green reconciliation badge. | *"Starting with the Executive Overview: our enterprise generated $990.8K in realized revenue and $388.1K in net profit, yielding a healthy 39.2% profit margin and an Average Order Value of $412. Every single KPI shown here is mathematically reconciled with 100% precision between our relational Star Schema and independent Python analytics."* |
| **0:25 – 0:40** | **Monthly Sales & Profit Trends** | Scroll smoothly to Section 2 (Monthly Trends chart). Point out the November/December holiday peaks. | *"Moving to historical trends across 2024 and 2025: our business expanded by 21.4% year-over-year. You can clearly observe cyclical demand peaks during Q4 holiday shopping in November and December, along with a corporate purchasing bump in March."* |
| **0:40 – 0:55** | **Short-Term ML Forecast** | Scroll to Section 3 (3-Month Sales Forecast). Highlight the dotted forecast line and the 80% confidence interval. | *"Next is our short-term sales forecast for Q1 2026. We trained an autoregressive Ridge regression model with lag features, evaluated chronologically against a 3-month moving average baseline. The model projects $49.2K in January, expanding to $53K in February, with calculated 80% prediction bounds."* |
| **0:55 – 1:10** | **Category & Regional Analysis** | Scroll to Sections 4 & 5. Point to Electronics volume, Office Supplies margins, and regional bars. | *"In Category performance, Electronics and Furniture drive over 68% of gross sales volume, while Office Supplies delivers high, resilient margins of 48%. Regionally, North America is our anchor market, while APAC represents our fastest-growing expansion territory."* |
| **1:10 – 1:25** | **Interactive Filtering Demo** | Scroll up slightly, click the **Region** filter dropdown, select **'North America'**, and watch cards/charts recalculate. Click **Reset**. | *"The entire dashboard is dynamic. When I filter by North America, all underlying measures, product rankings, and segment distributions recalculate instantaneously. Resetting returns us to the enterprise view."* |
| **1:25 – 1:40** | **Discount Sensitivity & Business Insights** | Scroll down to Section 8 (Discount Impact Table) and Section 9 (Insights). Highlight the margin drop above 15%. | *"One crucial finding from our exploratory analysis: transactions with discounts above 20% experience severe margin degradation, falling from 43% to under 8%. Based on this, our management recommendation is to implement a strict 15% discount approval threshold to protect operating cash flow."* |
| **1:40 – 1:55** | **Star Schema & Architecture Modal** | Click **"Data Model & Architecture"** in the top header. Show the modal flow and Star Schema diagram. | *"Under the hood, raw transactions flow through a Python ETL cleaning pipeline into a normalized Star Schema featuring Fact_Sales joined with four dimensions: Date, Product, Customer, and Region, which also connects natively to SAP Analytics Cloud."* |
| **1:55 – 2:05** | **Conclusion & Call to Action** | Close modal, show executive header, click "Presentation Mode". | *"The full source code, SQL DDL scripts, SAC model specifications, and test suite are published on my GitHub. Thank you for watching!"* |

---

## 5. Troubleshooting Guide

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| **Browser doesn't open automatically** | System browser handler delay | Manually open your browser and navigate to `http://127.0.0.1:8501`. |
| **Port 8501 is already in use** | Another service occupies 8501 | `run_demo.py` automatically binds to `8502` or `8503`. Check the terminal output for the active URL. |
| **Charts look blank or unstyled** | JavaScript or browser cache | Press `Ctrl + F5` to force hard reload. Local Chart.js bundle is included in `dashboard/vendor/chart.umd.js`. |
| **Connecting to MySQL** | MySQL service stopped or password mismatch | Update credentials in `.env` (`DB_TYPE=mysql`, `DB_PASSWORD=...`). If MySQL is offline, the system safely falls back to the verified SQLite database. |
| **Resetting demo state** | Need fresh regeneration | Run `python -m src.preprocessing` followed by `python -m src.database` to re-initialize from scratch. |
