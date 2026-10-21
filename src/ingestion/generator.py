"""
Retail Sales Intelligence & Forecasting Platform
Synthetic Dataset Generator
==============================================================================
Generates a realistic, deterministic retail transaction dataset spanning 24
consecutive calendar months (2024-01-01 to 2025-12-31).

Data Source Label: Synthetic Demonstration Data
Random Seed: 42 (Reproducible)
Documented Financial Rules:
  - Revenue = round(Quantity * Unit_Price * (1.0 - Discount), 2)
  - Cost    = round(Quantity * Unit_Cost, 2)
  - Profit  = round(Revenue - Cost, 2)
  - Margin  = round((Profit / Revenue) * 100, 2) if Revenue > 0 else 0.0
==============================================================================
"""

import math
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd

from src.config import RAW_DATA_FILE, RANDOM_SEED, START_DATE, END_DATE


PRODUCT_CATALOG = [
    # Electronics
    {"product_id": "PRD-TEC-001", "product_name": "Ultra HD 4K Pro Monitor 27in", "category": "Electronics", "unit_price": 380.00, "unit_cost": 240.00},
    {"product_id": "PRD-TEC-002", "product_name": "Ergonomic Mechanical Keyboard", "category": "Electronics", "unit_price": 130.00, "unit_cost": 70.00},
    {"product_id": "PRD-TEC-003", "product_name": "Noise-Cancelling Wireless Headset", "category": "Electronics", "unit_price": 199.00, "unit_cost": 110.00},
    {"product_id": "PRD-TEC-004", "product_name": "Thunderbolt 4 Docking Station", "category": "Electronics", "unit_price": 220.00, "unit_cost": 135.00},
    {"product_id": "PRD-TEC-005", "product_name": "External Rugged NVMe SSD 1TB", "category": "Electronics", "unit_price": 150.00, "unit_cost": 85.00},

    # Furniture
    {"product_id": "PRD-FUR-001", "product_name": "Executive Ergonomic Mesh Chair", "category": "Furniture", "unit_price": 320.00, "unit_cost": 190.00},
    {"product_id": "PRD-FUR-002", "product_name": "Dual-Motor Electric Standing Desk", "category": "Furniture", "unit_price": 520.00, "unit_cost": 330.00},
    {"product_id": "PRD-FUR-003", "product_name": "Solid Wood 4-Shelf Bookcase", "category": "Furniture", "unit_price": 240.00, "unit_cost": 140.00},
    {"product_id": "PRD-FUR-004", "product_name": "Mobile Lockable File Pedestal", "category": "Furniture", "unit_price": 160.00, "unit_cost": 95.00},
    {"product_id": "PRD-FUR-005", "product_name": "Articulated Dual Monitor Arm", "category": "Furniture", "unit_price": 95.00, "unit_cost": 48.00},

    # Office Supplies
    {"product_id": "PRD-OFF-001", "product_name": "High-Yield Laser Toner Multi-Pack", "category": "Office Supplies", "unit_price": 115.00, "unit_cost": 55.00},
    {"product_id": "PRD-OFF-002", "product_name": "Heavy-Duty Cross-Cut Shredder", "category": "Office Supplies", "unit_price": 175.00, "unit_cost": 98.00},
    {"product_id": "PRD-OFF-003", "product_name": "Premium Heavy-Duty Desktop Stapler", "category": "Office Supplies", "unit_price": 32.00, "unit_cost": 14.00},
    {"product_id": "PRD-OFF-004", "product_name": "Recycled Acid-Free Copy Paper (5 Reams)", "category": "Office Supplies", "unit_price": 42.00, "unit_cost": 26.00},
    {"product_id": "PRD-OFF-005", "product_name": "Ergonomic Gel Palm & Wrist Rest", "category": "Office Supplies", "unit_price": 24.00, "unit_cost": 9.00},

    # Apparel & Gear
    {"product_id": "PRD-APP-001", "product_name": "Waterproof Commuter Laptop Backpack", "category": "Apparel & Accessories", "unit_price": 110.00, "unit_cost": 52.00},
    {"product_id": "PRD-APP-002", "product_name": "Breathable Softshell Corporate Jacket", "category": "Apparel & Accessories", "unit_price": 145.00, "unit_cost": 72.00},
    {"product_id": "PRD-APP-003", "product_name": "Quick-Dry Moisture-Wicking Polo", "category": "Apparel & Accessories", "unit_price": 48.00, "unit_cost": 21.00},
    {"product_id": "PRD-APP-004", "product_name": "RFID-Blocking Travel Organizer Wallet", "category": "Apparel & Accessories", "unit_price": 36.00, "unit_cost": 15.00},
    {"product_id": "PRD-APP-005", "product_name": "Packable Weatherproof Rain Parka", "category": "Apparel & Accessories", "unit_price": 125.00, "unit_cost": 60.00},
]

REGIONS = [
    {"region": "North America", "countries": ["United States", "Canada"], "weight": 0.42},
    {"region": "EMEA", "countries": ["United Kingdom", "Germany", "France"], "weight": 0.28},
    {"region": "Asia Pacific", "countries": ["Japan", "Australia", "Singapore"], "weight": 0.20},
    {"region": "Latin America", "countries": ["Brazil", "Mexico"], "weight": 0.10},
]

SEGMENTS = [
    {"segment": "Consumer", "weight": 0.50},
    {"segment": "Corporate", "weight": 0.32},
    {"segment": "Home Office", "weight": 0.18},
]

DISCOUNT_OPTIONS = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
DISCOUNT_WEIGHTS = [0.35, 0.22, 0.18, 0.12, 0.07, 0.04, 0.02]


def _build_customer_pool(num_customers: int = 350) -> list[dict]:
    """Generates a stable customer base with realistic segment and regional affinity."""
    customers = []
    region_names = [r["region"] for r in REGIONS]
    region_weights = [r["weight"] for r in REGIONS]
    segment_names = [s["segment"] for s in SEGMENTS]
    segment_weights = [s["weight"] for s in SEGMENTS]

    first_names = ["James", "Emma", "Liam", "Olivia", "Noah", "Ava", "Sophia", "Jackson",
                   "Mia", "Lucas", "Elena", "Marcus", "Chloe", "Mateo", "Aria", "Julian",
                   "Zara", "Priya", "Hiroshi", "Freja", "Oliver", "Amara", "Carlos", "Sven"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
                  "Davis", "Rodriguez", "Martinez", "Tanaka", "Muller", "Dubois", "Silva",
                  "Patel", "Schneider", "Andersson", "O'Connor", "Kowalski", "Kim"]

    for i in range(1, num_customers + 1):
        cust_id = f"CUST-{i:04d}"
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        cust_name = f"{fn} {ln}"
        segment = random.choices(segment_names, weights=segment_weights, k=1)[0]
        region_info = random.choices(REGIONS, weights=region_weights, k=1)[0]
        region = region_info["region"]
        country = random.choice(region_info["countries"])

        customers.append({
            "customer_id": cust_id,
            "customer_name": cust_name,
            "customer_segment": segment,
            "region": region,
            "country": country,
        })
    return customers


def generate_retail_dataset(
    output_path: Optional[Path] = None,
    seed: int = RANDOM_SEED,
    num_orders: int = 2400,
    inject_anomalies: bool = True
) -> pd.DataFrame:
    """
    Generates a full synthetic retail sales dataset spanning 2024-01-01 to 2025-12-31.
    
    Returns:
        pd.DataFrame of raw transactions
    """
    random.seed(seed)
    np.random.seed(seed)

    start = datetime.strptime(START_DATE, "%Y-%m-%d")
    end = datetime.strptime(END_DATE, "%Y-%m-%d")
    total_days = (end - start).days + 1

    customers = _build_customer_pool(num_customers=350)
    records = []

    order_counter = 1
    
    # Generate orders distributed over the 24 months with seasonal weighting
    for _ in range(num_orders):
        # Sample order date with seasonal curve
        day_offset = random.randint(0, total_days - 1)
        order_date = start + timedelta(days=day_offset)
        
        # Seasonality multiplier: November & December holiday peak, slight March bump
        month = order_date.month
        year = order_date.year
        
        # Upward growth trend: ~20% higher probability in 2025 than 2024
        trend_weight = 1.0 + (0.22 if year == 2025 else 0.0)
        seasonal_weight = 1.0
        if month in [11, 12]:
            seasonal_weight = 1.65  # Holiday peak
        elif month in [3, 9]:
            seasonal_weight = 1.25  # Corporate fiscal cycles
        elif month in [1, 2]:
            seasonal_weight = 0.85  # Post-holiday slump

        # Acceptance check based on seasonal intensity
        if random.random() > (seasonal_weight * trend_weight / 2.05):
            # Roll again for date to achieve natural seasonal distribution
            day_offset = random.randint(0, total_days - 1)
            order_date = start + timedelta(days=day_offset)

        order_id = f"ORD-{order_date.year}-{order_counter:05d}"
        order_counter += 1

        customer = random.choice(customers)

        # 1 to 4 line items per order
        num_items = random.choices([1, 2, 3, 4], weights=[0.55, 0.28, 0.12, 0.05], k=1)[0]
        selected_products = random.sample(PRODUCT_CATALOG, k=num_items)

        for line_num, product in enumerate(selected_products, start=1):
            order_line_id = f"{order_id}-{line_num}"
            
            # Quantity determined by product category
            if product["category"] == "Office Supplies":
                qty = random.choices([1, 2, 3, 4, 5, 8, 10], weights=[0.25, 0.25, 0.20, 0.12, 0.08, 0.06, 0.04], k=1)[0]
            elif product["category"] == "Furniture":
                qty = random.choices([1, 2, 3], weights=[0.75, 0.20, 0.05], k=1)[0]
            elif product["category"] == "Electronics":
                qty = random.choices([1, 2, 3, 4], weights=[0.65, 0.25, 0.07, 0.03], k=1)[0]
            else:
                qty = random.choices([1, 2, 3, 5], weights=[0.50, 0.30, 0.15, 0.05], k=1)[0]

            unit_price = float(product["unit_price"])
            unit_cost = float(product["unit_cost"])
            
            # Select discount rate
            discount_rate = random.choices(DISCOUNT_OPTIONS, weights=DISCOUNT_WEIGHTS, k=1)[0]

            # Consistent financial calculation
            revenue = round(qty * unit_price * (1.0 - discount_rate), 2)
            cost = round(qty * unit_cost, 2)
            profit = round(revenue - cost, 2)
            profit_margin = round((profit / revenue) * 100.0, 2) if revenue > 0 else 0.0

            records.append({
                "Order ID": order_id,
                "Order Line ID": order_line_id,
                "Order Date": order_date.strftime("%Y-%m-%d"),
                "Product ID": product["product_id"],
                "Product Name": product["product_name"],
                "Category": product["category"],
                "Customer ID": customer["customer_id"],
                "Customer Name": customer["customer_name"],
                "Customer Segment": customer["customer_segment"],
                "Region": customer["region"],
                "Country": customer["country"],
                "Quantity": qty,
                "Unit Price": unit_price,
                "Unit Cost": unit_cost,
                "Discount": discount_rate,
                "Revenue": revenue,
                "Cost": cost,
                "Profit": profit,
                "Profit Margin": profit_margin,
                "Data Source": "Synthetic Retail Demonstration Data (Seed=42)"
            })

    df = pd.DataFrame(records)

    # Sort deterministically by Date and Order ID
    df.sort_values(by=["Order Date", "Order ID", "Order Line ID"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Inject minor raw data anomalies for ETL validation verification
    if inject_anomalies:
        # 1. Duplicate 3 random records at the end
        dups = df.sample(n=3, random_state=seed).copy()
        # 2. Add trailing whitespace to a couple customer names
        df.loc[df.index[5], "Customer Name"] = df.loc[df.index[5], "Customer Name"] + "  "
        # 3. Add an empty note field or slight casing inconsistency in a region
        df.loc[df.index[12], "Region"] = "north america"  # Test casing normalization
        # Append duplicates to raw file
        df = pd.concat([df, dups], ignore_index=True)

    dest = output_path or RAW_DATA_FILE
    dest.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dest, index=False)
    print(f"[Generator] Generated {len(df)} raw records across {df['Order ID'].nunique()} distinct orders.")
    print(f"[Generator] Output saved to: {dest}")

    return df


if __name__ == "__main__":
    generate_retail_dataset()
