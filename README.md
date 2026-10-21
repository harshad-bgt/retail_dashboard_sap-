# Retail Sales & Profitability Analysis (Streamlit App & EDA)

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458.svg)](https://pandas.pydata.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.7%2B-11557c.svg)](https://matplotlib.org/)
[![Seaborn](https://img.shields.io/badge/Seaborn-0.12%2B-4c72b0.svg)](https://seaborn.pydata.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An interactive retail sales and profitability analysis web application built with **Streamlit, Python, Pandas, Matplotlib, and Seaborn**, analyzing 4 years of retail transaction data from the **Tableau Sample Superstore** dataset.

The project evaluates sales trends, profitability drivers, product catalog margins, regional performance, and the direct financial impact of discounting on business margins.

---

## 1. Project Structure

```text
retail-sales-analysis/
├── app.py                          # Main Streamlit web application
├── requirements.txt                # Minimal Python package dependencies
├── README.md                       # Project documentation and findings
├── LICENSE                         # MIT License
├── data/
│   ├── Sample - Superstore.csv     # Primary retail dataset (Tableau Sample Superstore)
│   └── retail_sales.csv            # Clean UTF-8 dataset copy
├── notebooks/
│   └── retail_sales_analysis.ipynb # Companion exploratory Jupyter Notebook
├── sql/
│   └── sales_analysis.sql          # 10 core analytical SQL business queries
└── outputs/
    ├── figures/                    # Exported high-resolution analytical figures
    └── charts/                     # Final chart images generated from the analysis
        ├── 01_monthly_sales_trend.png
        ├── 02_sales_profit_by_category.png
        ├── 03_sub_category_profitability.png
        ├── 04_discount_vs_profit_margin.png
        └── 05_regional_performance.png
```

---

## 2. Dataset Overview

- **Source:** [Tableau Public Sample Superstore Dataset](https://www.tableau.com/learn/sample-data)
- **Time Horizon:** January 3, 2015 – December 30, 2018 (4 Full Calendar Years)
- **Granularity:** Line-item retail transactions across the United States
- **Cleaned Records:** 9,994 transactions (cleaned from 10,800 rows after removing 806 non-transaction reference rows)
- **Core Fields:**
  - `Order ID`, `Order Date`, `Ship Date`, `Ship Mode`
  - `Customer ID`, `Customer Name`, `Segment` (Consumer, Corporate, Home Office)
  - `Country`, `City`, `State`, `Postal Code`, `Region` (West, East, Central, South)
  - `Product ID`, `Category` (Furniture, Office Supplies, Technology), `Sub-Category`, `Product Name`
  - `Sales`, `Quantity`, `Discount`, `Profit`

---

## 3. Executive KPI Summary

Every metric is dynamically calculated from the loaded dataset:

| Business Metric | Value | Meaning |
| :--- | :---: | :--- |
| **Total Sales** | **$2,297,200.86** | Gross revenue net of promotional discounts over 4 years |
| **Total Net Profit** | **$286,397.02** | Total operating net return generated across all catalog items |
| **Overall Profit Margin** | **12.47%** | Calculated as `(Total Profit / Total Sales) * 100` |
| **Total Orders** | **5,009** | Distinct order transactions (`Order ID` count) |
| **Distinct Customers** | **793** | Unique customer accounts |
| **Total Units Sold** | **37,873** | Total items fulfilled |
| **Average Order Value (AOV)** | **$458.61** | Average revenue per distinct customer order |

---

## 4. Main Analytical Questions & Findings

1. **Which product category generates the highest sales and profit?**  
   - **Technology** is the primary profit engine, generating **$836,154.03** in sales and **$145,454.95** in profit (**17.40% margin**).  
   - **Office Supplies** generates **$719,047.03** in sales and **$122,490.80** in profit (**17.04% margin**).  
   - **Furniture** generates **$741,999.80** in sales but achieves an anemic profit margin of only **2.49%** ($18,451.27 profit), indicating severe margin leakage.

2. **Which sub-categories generate the greatest profits or losses?**  
   - **Top Drivers:** Copiers (+$55.6K), Phones (+$44.5K), and Accessories (+$41.9K) drive enterprise profitability.  
   - **Severe Loss-Makers:** **Tables (-$17,725.48)**, **Bookcases (-$3,472.56)**, and **Supplies (-$1,189.10)** operate at substantial net losses due to unconstrained promotional discounting.

3. **How does discounting impact profitability? (The 20% Discount Cliff)**  
   - **0% Discount:** Yields a healthy **30.1%** profit margin.  
   - **1–20% Discount:** Sustains positive returns with a **14.8%** margin.  
   - **>20% Discount:** Collapses into an average net loss of **-34.9%**. Deep markdowns directly turn profitable orders into cash losses.

4. **How do sales vary by geography?**  
   - **West ($725.5K Sales, 14.9% Margin)** and **East ($678.8K Sales, 13.5% Margin)** represent the most lucrative markets.  
   - **Central ($501.2K Sales, 7.9% Margin)** experiences the lowest profit margin due to heavy furniture markdowns.

5. **Are there seasonal patterns?**  
   - Sales exhibit consistent long-term growth and predictably spike in **November and December (Q4)** due to holiday purchasing.

---

## 5. Visualizations Included in the App

1. **Monthly Sales and Profit Trends:** Dual line/area chart displaying monthly sales and profits from 2015 to 2018.
2. **Sales by Category and Profit Margin:** Side-by-side bar plots comparing top-line revenue against bottom-line margin percentages.
3. **Sub-Category Profitability:** Horizontal bar chart highlighting profit leaders (green) vs loss-makers (red).
4. **Discount vs. Profitability:** Distribution boxplot and aggregate margin bar chart evaluating the margin collapse above 20% discount.
5. **Regional Sales and Profit:** Clustered bar chart showing geographic sales, profits, and regional margins.

---

## 6. How to Run the Project Locally

### Prerequisites
- Python 3.10+ (tested on Python 3.12)

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/retail-sales-analysis.git
cd retail-sales-analysis
```

### Step 2: Install Required Dependencies
```bash
python -m pip install -r requirements.txt
```

### Step 3: Launch the Streamlit Web Application
```bash
python -m streamlit run app.py
```

The application will launch and open in your default browser at:  
👉 **`http://localhost:8501`**

### Step 4: (Optional) Open the Jupyter Notebook
```bash
jupyter notebook
```
Navigate to `notebooks/retail_sales_analysis.ipynb` to view the step-by-step exploratory analysis.

---

## 7. Limitations & Recommendations

- **Dataset Limitations:** The dataset covers US retail orders from 2015 to 2018. Modern e-commerce trends and inflation may alter consumer behavior. Operating overhead (marketing, warehouse storage) is not itemized beyond unit profit.
- **Recommendations:**
  - Cap sales rep discretionary discounts on Furniture at 20%.
  - Bundle low-margin Tables with high-margin Accessories.
  - Pre-position inventory in West and East fulfillment hubs in early Q3 before the holiday surge.

---

## 8. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
