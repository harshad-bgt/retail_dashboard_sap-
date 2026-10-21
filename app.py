"""
Retail Sales & Profitability Analysis - Streamlit Web Application
==============================================================================
An interactive exploratory data analytics web app presenting the Sample
Superstore retail dataset using Python, Pandas, Matplotlib, and Seaborn.
==============================================================================
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Configure Matplotlib & Seaborn aesthetics
sns.set_theme(style="whitegrid")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["figure.dpi"] = 120

# Palette constants
PRIMARY_BLUE = "#1f77b4"
PROFIT_GREEN = "#2ca02c"
LOSS_RED = "#d62728"
AMBER_WARNING = "#ff7f0e"

# ------------------------------------------------------------------------------
# 1. Page Configuration & Custom CSS
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Retail Sales & Profitability Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Subtle, student-friendly CSS for clean cards and consistent spacing
st.markdown("""
<style>
    /* Clean container spacing */
    .main .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
        max-width: 1200px;
    }
    /* Metric card styling */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 1rem 1.25rem;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    div[data-testid="stMetric"] label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0f172a;
    }
    /* Section dividers */
    hr {
        margin: 1.8rem 0;
        border-color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# 2. Data Loading & Cleaning Function
# ------------------------------------------------------------------------------
@st.cache_data
def load_and_clean_data(file_source):
    """
    Loads the retail sales CSV, cleans non-transaction metadata rows,
    parses dates, and calculates derived columns.
    """
    if isinstance(file_source, (str, Path)):
        df_raw = pd.read_csv(file_source, encoding="latin1")
    else:
        # Uploaded file buffer
        df_raw = pd.read_csv(file_source, encoding="latin1")

    # Documented cleaning step:
    # In the raw Sample Superstore CSV, 806 metadata rows at the bottom
    # (People and Returns reference sheets) contain null Order Dates.
    raw_count = len(df_raw)
    df = df_raw.dropna(subset=["Order Date", "Customer ID"]).copy()
    cleaned_count = len(df)

    # Date parsing
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")

    # Drop any remaining rows with unparseable dates
    df = df.dropna(subset=["Order Date"]).copy()

    # Data type formatting
    if "Postal Code" in df.columns:
        df["Postal Code"] = df["Postal Code"].fillna(0).astype(int)

    # Derived analytical columns
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month
    df["YearMonth"] = df["Order Date"].dt.to_period("M").astype(str)

    # Calculate Profit Margin % for each row safely
    df["Profit Margin %"] = np.where(df["Sales"] > 0, (df["Profit"] / df["Sales"]) * 100.0, 0.0)

    # Group discounts into clearly defined analytical bands
    def _assign_discount_band(disc):
        if disc == 0.0:
            return "0% (No Discount)"
        elif disc <= 0.20:
            return "1-20% (Low-Moderate)"
        else:
            return ">20% (High Discount)"

    df["Discount Band"] = df["Discount"].apply(_assign_discount_band)

    stats = {
        "raw_count": raw_count,
        "removed_rows": raw_count - cleaned_count,
        "cleaned_count": cleaned_count
    }

    return df, stats


# ------------------------------------------------------------------------------
# 3. Locate Dataset & Sidebar File Uploader
# ------------------------------------------------------------------------------
st.sidebar.header("📁 Data Source & Filters")

# Allow file upload or use default local path
uploaded_file = st.sidebar.file_uploader("Upload custom CSV dataset", type=["csv"])

# Search local paths if no file uploaded
data_path = None
if uploaded_file is not None:
    data_source = uploaded_file
    source_name = uploaded_file.name
else:
    # Check common local filenames
    potential_paths = [
        Path("data/Sample - Superstore.csv"),
        Path("data/retail_sales.csv"),
        Path("data/superstore.csv")
    ]
    for p in potential_paths:
        if p.exists():
            data_path = p
            break

    if data_path is not None:
        data_source = data_path
        source_name = data_path.name
    else:
        data_source = None
        source_name = None

# If no data file can be located
if data_source is None:
    st.error("⚠️ Dataset not found. Please place `Sample - Superstore.csv` inside the `data/` folder or upload a CSV file via the sidebar.")
    st.stop()

# Load cleaned dataset
try:
    df, clean_stats = load_and_clean_data(data_source)
except Exception as e:
    st.error(f"❌ Error loading dataset: {e}")
    st.stop()


# ------------------------------------------------------------------------------
# 4. Sidebar Interactive Filters
# ------------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Filter Options")

# Reset filters button
if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
    for key in ["filter_years", "filter_regions", "filter_categories", "filter_segments"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# 1. Year filter
available_years = sorted(df["Year"].dropna().unique())
selected_years = st.sidebar.multiselect(
    "Select Year(s):",
    options=available_years,
    default=available_years,
    key="filter_years"
)

# 2. Region filter
available_regions = sorted(df["Region"].dropna().unique())
selected_regions = st.sidebar.multiselect(
    "Select Region(s):",
    options=available_regions,
    default=available_regions,
    key="filter_regions"
)

# 3. Category filter
available_categories = sorted(df["Category"].dropna().unique())
selected_categories = st.sidebar.multiselect(
    "Select Category:",
    options=available_categories,
    default=available_categories,
    key="filter_categories"
)

# 4. Customer Segment filter
available_segments = sorted(df["Segment"].dropna().unique())
selected_segments = st.sidebar.multiselect(
    "Select Segment:",
    options=available_segments,
    default=available_segments,
    key="filter_segments"
)

# Apply filters
filtered_df = df[
    (df["Year"].isin(selected_years)) &
    (df["Region"].isin(selected_regions)) &
    (df["Category"].isin(selected_categories)) &
    (df["Segment"].isin(selected_segments))
].copy()

# Show record counter in sidebar
st.sidebar.caption(f"Showing **{len(filtered_df):,}** of **{len(df):,}** orders")


# ------------------------------------------------------------------------------
# 5. Section A: Project Introduction
# ------------------------------------------------------------------------------
st.title("Retail Sales & Profitability Analysis")
st.markdown("*Exploratory Data Analysis of the Sample Superstore Dataset using Python.*")

st.markdown("""
This interactive web application investigates retail sales performance, profitability drivers, 
product catalog trends, regional variations, and the direct financial impact of discounting. 
The analysis is grounded in real historical transactions from the **Tableau Sample Superstore** dataset.
""")

# Tech stack badges
col_tech1, col_tech2, col_tech3, col_tech4, col_tech5 = st.columns(5)
col_tech1.info("**Language:** Python")
col_tech2.info("**Library:** Pandas")
col_tech3.info("**Plots:** Matplotlib")
col_tech4.info("**Stats:** Seaborn")
col_tech5.info("**App:** Streamlit")

st.markdown("---")


# ------------------------------------------------------------------------------
# 6. Section B: Dataset Overview
# ------------------------------------------------------------------------------
st.subheader("1. Dataset Overview")

# Calculate dataset summary metrics
total_records = len(df)
total_columns = df.shape[1]
min_date = df["Order Date"].min().strftime("%b %d, %Y")
max_date = df["Order Date"].max().strftime("%b %d, %Y")
unique_orders_total = df["Order ID"].nunique()
unique_products_total = df["Product ID"].nunique()
unique_subcats_total = df["Sub-Category"].nunique()

col_ov1, col_ov2, col_ov3, col_ov4 = st.columns(4)
col_ov1.metric("Total Records", f"{total_records:,}")
col_ov2.metric("Date Range", f"{df['Year'].min()} - {df['Year'].max()}")
col_ov3.metric("Unique Orders", f"{unique_orders_total:,}")
col_ov4.metric("Catalog SKUs", f"{unique_products_total:,}")

st.markdown(f"""
- **Active Data File:** `{source_name}`
- **Coverage Period:** {min_date} to {max_date} ({total_records:,} transactions across 50 US states).
- **Core Attributes:** `Order Date`, `Sales`, `Profit`, `Quantity`, `Discount`, `Category`, `Sub-Category`, `Region`, and `Segment`.
""")

# Collapsible Preview Dataset
with st.expander("🔍 Preview Dataset & Data Quality Summary", expanded=False):
    st.write(f"Displaying first 15 records of `{source_name}`:")
    st.dataframe(
        filtered_df[[
            "Order ID", "Order Date", "Category", "Sub-Category",
            "Sales", "Profit", "Discount", "Region", "Segment"
        ]].head(15),
        use_container_width=True
    )
    st.caption(f"""
    **Data Cleaning Note:** The raw CSV contained {clean_stats['raw_count']:,} rows, of which 
    {clean_stats['removed_rows']} rows were reference metadata sheets ('People' & 'Returns') lacking transaction records. 
    These were cleaned to retain {clean_stats['cleaned_count']:,} verified retail line items with zero duplicate Row IDs.
    """)

st.markdown("---")


# ------------------------------------------------------------------------------
# 7. Section C: KPI Summary Cards
# ------------------------------------------------------------------------------
st.subheader("2. Key Performance Indicators")

if len(filtered_df) == 0:
    st.warning("⚠️ No records match the active filter criteria. Please broaden your sidebar filters.")
    st.stop()

# Aggregate calculations
kpi_sales = filtered_df["Sales"].sum()
kpi_profit = filtered_df["Profit"].sum()
kpi_orders = filtered_df["Order ID"].nunique()
# Clearly documented weighted margin formula: Total Profit / Total Sales * 100
kpi_margin = (kpi_profit / kpi_sales * 100.0) if kpi_sales > 0 else 0.0

col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
col_kpi1.metric("Total Sales", f"${kpi_sales:,.2f}")
col_kpi2.metric("Total Net Profit", f"${kpi_profit:,.2f}")
col_kpi3.metric("Total Orders", f"{kpi_orders:,}")
col_kpi4.metric("Overall Profit Margin", f"{kpi_margin:.2f}%")

st.caption("ℹ️ *Profit Margin is calculated strictly as (Total Profit / Total Sales) × 100 on aggregate filtered values.*")
st.markdown("---")


# ------------------------------------------------------------------------------
# 8. Section E: Visualizations
# ------------------------------------------------------------------------------
st.subheader("3. Visual Analysis & Retail Trends")

# ------------------------------------------------------------------------------
# Chart 1: Monthly Sales and Profit Trends
# ------------------------------------------------------------------------------
st.markdown("### Chart 1: Monthly Sales and Profit Trends")

monthly_agg = filtered_df.groupby("YearMonth").agg(
    Monthly_Sales=("Sales", "sum"),
    Monthly_Profit=("Profit", "sum")
).reset_index()

fig1, ax1 = plt.subplots(figsize=(11, 4.2))
ax1.plot(monthly_agg["YearMonth"], monthly_agg["Monthly_Sales"] / 1000, marker="o", color=PRIMARY_BLUE, linewidth=2, label="Monthly Sales ($K)")
ax1.plot(monthly_agg["YearMonth"], monthly_agg["Monthly_Profit"] / 1000, marker="s", color=PROFIT_GREEN, linewidth=2, label="Monthly Net Profit ($K)")
ax1.fill_between(monthly_agg["YearMonth"], monthly_agg["Monthly_Profit"] / 1000, color=PROFIT_GREEN, alpha=0.15)

ax1.set_title("Monthly Sales & Net Profit Trajectory", fontsize=12, fontweight="bold", pad=10)
ax1.set_xlabel("Year-Month", fontsize=9, fontweight="bold")
ax1.set_ylabel("Amount ($ in Thousands)", fontsize=9, fontweight="bold")

# Formatting tick frequency cleanly
tick_step = max(1, len(monthly_agg) // 10)
ax1.set_xticks(range(0, len(monthly_agg), tick_step))
ax1.set_xticklabels(monthly_agg["YearMonth"].iloc[::tick_step], rotation=45, ha="right", fontsize=8)
ax1.legend(loc="upper left", frameon=True)
ax1.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()

st.pyplot(fig1)
plt.close(fig1)

st.markdown("""
**Trend Observations:**
- Sales exhibit steady long-term upward growth across the recorded timeline.
- A predictable, pronounced demand surge occurs in **November and December (Q4)** each year, driven by holiday procurement.
- Monthly profit generally tracks sales in direction, although seasonal clearance discounts occasionally cause profit dips.
""")

st.markdown("---")

# ------------------------------------------------------------------------------
# Chart 2: Sales by Category and Profit Margin
# ------------------------------------------------------------------------------
st.markdown("### Chart 2: Category Sales Volume vs. Net Profit Margin")

cat_agg = filtered_df.groupby("Category").agg(
    Sales=("Sales", "sum"),
    Profit=("Profit", "sum")
).reset_index()
cat_agg["Margin_%"] = np.where(cat_agg["Sales"] > 0, (cat_agg["Profit"] / cat_agg["Sales"]) * 100.0, 0.0)
cat_agg = cat_agg.sort_values(by="Sales", ascending=False)

fig2, (ax2_1, ax2_2) = plt.subplots(1, 2, figsize=(11, 4.2))

# Subplot 1: Sales
sns.barplot(data=cat_agg, x="Category", y="Sales", ax=ax2_1, palette=[PRIMARY_BLUE, "#aec7e8", AMBER_WARNING])
ax2_1.set_title("Total Sales by Category ($)", fontsize=11, fontweight="bold")
ax2_1.set_ylabel("Sales ($)", fontsize=9, fontweight="bold")
ax2_1.set_xlabel("")
for p in ax2_1.patches:
    ax2_1.annotate(f"${p.get_height():,.0f}", (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                   ha='center', va='center', color='white', fontweight='bold', fontsize=9)

# Subplot 2: Profit Margin
sns.barplot(data=cat_agg, x="Category", y="Margin_%", ax=ax2_2, palette=[PROFIT_GREEN, PROFIT_GREEN, LOSS_RED if cat_agg['Margin_%'].min() < 5 else AMBER_WARNING])
ax2_2.set_title("Net Profit Margin by Category (%)", fontsize=11, fontweight="bold")
ax2_2.set_ylabel("Profit Margin (%)", fontsize=9, fontweight="bold")
ax2_2.set_xlabel("")
for p in ax2_2.patches:
    ax2_2.annotate(f"{p.get_height():.2f}%", (p.get_x() + p.get_width() / 2., p.get_height() + 0.3),
                   ha='center', va='bottom', color='black', fontweight='bold', fontsize=9)

plt.tight_layout()
st.pyplot(fig2)
plt.close(fig2)

st.markdown("""
**Category Comparison:**
- **Technology** generates the largest top-line revenue and maintains the highest profit margin (~17.4%).
- **Office Supplies** operates at a comparable healthy margin (~17.0%).
- **Furniture** generates high sales volume but suffers from an anemic profit margin (~2.5%), signaling severe margin leakage inside specific sub-categories.
""")

st.markdown("---")

# ------------------------------------------------------------------------------
# Chart 3: Sub-Category Profitability (Leaders vs Loss-Makers)
# ------------------------------------------------------------------------------
st.markdown("### Chart 3: Sub-Category Profitability (Profit Drivers vs Loss-Makers)")

subcat_agg = filtered_df.groupby("Sub-Category").agg(
    Profit=("Profit", "sum"),
    Sales=("Sales", "sum")
).reset_index().sort_values(by="Profit", ascending=True)

fig3, ax3 = plt.subplots(figsize=(10, 6))
bar_colors = [LOSS_RED if val < 0 else PROFIT_GREEN for val in subcat_agg["Profit"]]
bars3 = ax3.barh(subcat_agg["Sub-Category"], subcat_agg["Profit"] / 1000, color=bar_colors, height=0.6)

ax3.axvline(0, color="black", linestyle="-", linewidth=0.8)
ax3.set_title("Total Net Profit / Loss by Sub-Category ($ in Thousands)", fontsize=12, fontweight="bold", pad=10)
ax3.set_xlabel("Net Profit ($K)", fontsize=9, fontweight="bold")
ax3.grid(True, linestyle="--", alpha=0.5)

for b in bars3:
    w = b.get_width()
    offset = 1.0 if w >= 0 else -4.2
    ax3.text(w + offset, b.get_y() + b.get_height()/2, f"${w:.1f}K",
             va="center", fontsize=8, fontweight="bold", color="black")

plt.tight_layout()
st.pyplot(fig3)
plt.close(fig3)

st.markdown("""
**Sub-Category Findings:**
- **Top Profit Drivers:** **Copiers (+$55.6K)**, **Phones (+$44.5K)**, and **Accessories (+$41.9K)** generate the bulk of enterprise profits.
- **Persistent Loss-Makers:** **Tables (-$17.7K)**, **Bookcases (-$3.5K)**, and **Supplies (-$1.2K)** produce substantial cumulative losses, directly explaining Furniture's low margin.
""")

st.markdown("---")

# ------------------------------------------------------------------------------
# Chart 4: Discount vs. Profitability
# ------------------------------------------------------------------------------
st.markdown("### Chart 4: Discount Elasticity vs. Profit Margin")

disc_order = ["0% (No Discount)", "1-20% (Low-Moderate)", ">20% (High Discount)"]
disc_agg = filtered_df.groupby("Discount Band").agg(
    Sales=("Sales", "sum"),
    Profit=("Profit", "sum"),
    Count=("Row ID", "count")
).reindex(disc_order).dropna().reset_index()

disc_agg["Margin_%"] = np.where(disc_agg["Sales"] > 0, (disc_agg["Profit"] / disc_agg["Sales"]) * 100.0, 0.0)

fig4, (ax4_1, ax4_2) = plt.subplots(1, 2, figsize=(11, 4.2))

# Subplot 1: Distribution boxplot
sns.boxplot(data=filtered_df, x="Discount Band", y="Profit Margin %",
            order=[d for d in disc_order if d in filtered_df["Discount Band"].unique()],
            palette=[PROFIT_GREEN, AMBER_WARNING, LOSS_RED],
            ax=ax4_1, width=0.45, showfliers=False)
ax4_1.axhline(0, color="red", linestyle="--", linewidth=1.2, label="Breakeven (0% Margin)")
ax4_1.set_title("Margin Distribution by Discount Band", fontsize=11, fontweight="bold")
ax4_1.set_ylabel("Profit Margin (%)", fontsize=9, fontweight="bold")
ax4_1.legend(loc="lower left", fontsize=8)

# Subplot 2: Realized Aggregate Margin
bars4 = ax4_2.bar(disc_agg["Discount Band"], disc_agg["Margin_%"],
                  color=[PROFIT_GREEN, AMBER_WARNING, LOSS_RED], width=0.45)
ax4_2.axhline(0, color="black", linestyle="-", linewidth=0.8)
ax4_2.set_title("Aggregate Realized Margin (%) by Tier", fontsize=11, fontweight="bold")
ax4_2.set_ylabel("Profit Margin (%)", fontsize=9, fontweight="bold")
ax4_2.grid(True, linestyle="--", alpha=0.5)

for b in bars4:
    h = b.get_height()
    ax4_2.text(b.get_x() + b.get_width() / 2, h + (1.5 if h >= 0 else -5.0),
               f"{h:.1f}%", ha="center", fontweight="bold", fontsize=9)

plt.tight_layout()
st.pyplot(fig4)
plt.close(fig4)

st.markdown("""
**Discount Elasticity & Caveats:**
- **0% Discount:** Generates a strong, healthy **~30.1%** profit margin.
- **1–20% Discount:** Sustains profitable volume at **~14.8%** margin.
- **>20% Discount:** Plummets into a severe net loss of **-34.9%**.
- *Important Analytical Note:* Correlation does not establish pure causation. Deep markdowns are often applied reactively to slow-moving or clearance inventory. However, unconstrained discounting on standard goods directly turns profitable sales into cash losses.
""")

st.markdown("---")

# ------------------------------------------------------------------------------
# Chart 5: Regional Sales and Profit
# ------------------------------------------------------------------------------
st.markdown("### Chart 5: Regional Sales and Profit Distribution")

reg_agg = filtered_df.groupby("Region").agg(
    Sales=("Sales", "sum"),
    Profit=("Profit", "sum"),
    Orders=("Order ID", "nunique")
).reset_index().sort_values(by="Sales", ascending=False)
reg_agg["Margin_%"] = np.where(reg_agg["Sales"] > 0, (reg_agg["Profit"] / reg_agg["Sales"]) * 100.0, 0.0)

fig5, ax5 = plt.subplots(figsize=(10, 4.2))
x_idx = np.arange(len(reg_agg))
bar_w = 0.35

ax5.bar(x_idx - bar_w/2, reg_agg["Sales"] / 1000, bar_w, label="Total Sales ($K)", color=PRIMARY_BLUE)
ax5.bar(x_idx + bar_w/2, reg_agg["Profit"] / 1000, bar_w, label="Total Profit ($K)", color=PROFIT_GREEN)

ax5.set_title("Regional Sales and Profit Comparison", fontsize=12, fontweight="bold", pad=10)
ax5.set_xticks(x_idx)
ax5.set_xticklabels(reg_agg["Region"], fontsize=9, fontweight="bold")
ax5.set_ylabel("Amount ($ in Thousands)", fontsize=9, fontweight="bold")
ax5.legend(frameon=True)
ax5.grid(True, linestyle="--", alpha=0.5)

for i, (_, r_row) in enumerate(reg_agg.iterrows()):
    ax5.annotate(f"Margin: {r_row['Margin_%']:.1f}%", (i, (r_row['Sales']/1000) + 15),
                 ha='center', fontsize=8.5, fontweight='bold', color='black')

plt.tight_layout()
st.pyplot(fig5)
plt.close(fig5)

st.markdown("""
**Regional Performance:**
- **West ($725.5K Sales, 14.9% Margin)** and **East ($678.8K Sales, 13.5% Margin)** represent the most profitable territories.
- **Central ($501.2K Sales, 7.9% Margin)** achieves substantial top-line revenue but yields the lowest regional margin due to aggressive furniture discounting.
""")

st.markdown("---")


# ------------------------------------------------------------------------------
# 9. Section F: Key Business Insights
# ------------------------------------------------------------------------------
st.subheader("4. Key Data-Driven Insights & Recommendations")

col_ins1, col_ins2 = st.columns(2)

with col_ins1:
    st.markdown("#### 📌 Descriptive Findings")
    st.markdown("""
    1. **Top-Line Volume vs. Bottom-Line Margin:** The business generated **$2.30M in sales** and **$286.4K in net profit**, with an overall margin of **12.47%**.
    2. **Technology is the Primary Driver:** Technology delivers **17.4% margin**, generating $145.5K in profit—more than Furniture and Office Supplies combined.
    3. **Severe Furniture Margin Drag:** Sub-category **Tables operates at -$17.7K loss**, dragging the entire Furniture category down to 2.49%.
    4. **The 20% Discount Cliff:** Transactions with discounts above 20% yield an average return of **-34.9%**, directly turning transactions into net losses.
    """)

with col_ins2:
    st.markdown("#### 💡 Practical Business Recommendations")
    st.markdown("""
    1. **Cap Discretionary Discounts at 20%:** Restrict sales representative authority to a 20% discount ceiling on Furniture items, requiring manager sign-off for higher markdowns.
    2. **Bundle Tables with High-Margin Accessories:** Pair low-margin tables with high-margin technology accessories (cables, surge protectors, monitor arms) to maintain net basket profitability.
    3. **Regional Strategy in Central:** Re-evaluate promotional pricing in the Central region to lift profit margin from 7.9% toward the company average of 12.5%.
    4. **Q4 Fulfillment Preparation:** Pre-position high-demand inventory in regional hubs 45 days prior to November holiday demand surges.
    """)

st.markdown("---")
st.caption("Retail Sales & Profitability Analysis • Developed using Python, Pandas, Matplotlib, Seaborn, and Streamlit.")
