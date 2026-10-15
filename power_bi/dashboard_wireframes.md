# Shoplytics — Power BI Dashboard Layout & Visual Specifications

This document outlines the visual structure, layout grid, slicers, and chart configurations for the 4 interactive report pages in Power BI.

---

## Page 1: Executive Sales Overview & Financial Performance

### Layout Grid (16:9 Canvas — 1920 x 1080)
- **Top Header Bar**: Project Title, Platform Logo, Last Refresh Date, Currency indicator (BRL).
- **Global Slicers**:
  - Date Range Slider (`dim_date[Date]`)
  - Order Status (`fact_orders[order_status]`)
  - Customer State Dropdown (`dim_customers[customer_state]`)
  - Payment Type Dropdown (`fact_order_payments[payment_type]`)

### Visuals
1. **KPI Scorecard Strip (Top)**:
   - Card 1: `Total GMV` (R$ 15.42M)
   - Card 2: `Total Merchandise Revenue` (R$ 13.22M)
   - Card 3: `Delivered Orders` (96,478)
   - Card 4: `Average Order Value (AOV)` (R$ 137.04)
   - Card 5: `On-Time Delivery Rate %` (91.9%)
   - Card 6: `Average Customer Rating` (4.15 ★)

2. **Monthly Revenue & Order Volume Trend (Area + Line Combo Chart)**:
   - X-Axis: `dim_date[Year-Month]`
   - Column Y-Axis: `Total Merchandise Revenue`
   - Line Y-Axis: `Delivered Orders`
   - Data labels enabled for peak month (Nov 2017 Black Friday surge).

3. **Payment Methods Breakdown (Donut Chart)**:
   - Legend: `payment_type` (Credit Card, Boleto, Voucher, Debit Card)
   - Values: `Total Payment Value`
   - Detail Labels: Category + Percentage of Total (78.3% Credit Card).

4. **Geographic State Revenue Heatmap (Choropleth Map / Filled Map)**:
   - Location: `customer_state`
   - Color Saturation: `Total Merchandise Revenue`
   - Tooltips: `Delivered Orders`, `Average Order Value`, `Avg Delivery Days`.

---

## Page 2: Logistics & Delivery SLA Performance

### Purpose
Monitor carrier efficiency, fulfillment bottlenecks, and SLA breach risks across regions.

### Visuals
1. **Logistics KPIs (Cards)**:
   - `On-Time Delivery Rate %` (Target: >95%, Actual: 91.9%)
   - `Avg Delivery Lead Time Days` (12.6 Days)
   - `Avg Estimated Delivery Days` (23.7 Days)
   - `Avg Delay Days When Late` (9.6 Days)

2. **Delivery Lead Time by Destination State (Horizontal Bar Chart)**:
   - Y-Axis: `customer_state` (Sorted descending by lead time)
   - X-Axis: `Avg Delivery Lead Time Days`
   - Highlights: Northern states (RR, AP, AM at 26-28 days) vs Southeast (SP at 8.3 days).

3. **Intra-State vs Inter-State Performance (Clustered Column Chart)**:
   - Categories: Intra-State vs Inter-State
   - Metric 1: `Avg Delivery Lead Time Days` (7.9 days vs 15.0 days)
   - Metric 2: `Avg Freight Value` (R$ 13.45 vs R$ 23.63)
   - Metric 3: `Late Delivery Rate %` (6.8% vs 10.2%)

4. **Monthly On-Time Delivery % SLA Trend (Line Chart with Reference Target)**:
   - X-Axis: `Year-Month`
   - Y-Axis: `On-Time Delivery Rate %`
   - Constant Line: 95.0% SLA Target.

---

## Page 3: Customer Intelligence & RFM Segmentation

### Purpose
Understand customer lifetime value, loyalty cohorts, and retention intervention opportunities.

### Visuals
1. **RFM Customer Segments Treemap**:
   - Group: `customer_segment`
   - Size: `Total Merchandise Revenue`
   - Details: `Customer Count`, `Avg Spend per Customer`.

2. **Buyer Loyalty Cohort (Donut Chart)**:
   - Values: `One-Time Buyers` (96.9%) vs `Repeat Buyers` (3.1%).
   - Callout: Retention opportunity to convert one-time buyers.

3. **Customer Recency vs Monetary Value (Scatter Plot)**:
   - X-Axis: `recency_days`
   - Y-Axis: `monetary_value`
   - Legend / Color: `customer_segment`
   - Size: `frequency`

4. **State-Level Customer Density Table (Matrix Visual)**:
   - Rows: `customer_state`
   - Columns: `Total Customers`, `Total Orders`, `Total Spend`, `Repeat Customer Rate %`.

---

## Page 4: Product Category & Review Diagnostics

### Purpose
Diagnose product catalog health and analyze the root causes of customer dissatisfaction.

### Visuals
1. **Top 15 Categories by Revenue (Pareto Chart / Column + Line)**:
   - Columns: `Total Revenue`
   - Line: `Cumulative Revenue %` (Pareto curve showing 80/20 distribution).

2. **Review Rating Breakdown (Horizontal Stacked Bar Chart)**:
   - Y-Axis: Star Rating (5 Stars down to 1 Star)
   - Bar Length: Number of Reviews
   - Value Labels: Percentage of total (57.8% 5-star, 11.5% 1-star).

3. **Delivery Delay Impact on Customer Ratings (Clustered Bar Chart)**:
   - Group 1: On-Time / Early Delivery
     - Avg Rating: 4.29 Stars | % 1-Star: 6.6% | % 5-Star: 62.4%
   - Group 2: Delayed Delivery
     - Avg Rating: 2.57 Stars | % 1-Star: 46.2% | % 5-Star: 22.2%

4. **Categories with Highest Discontent Rate (Table Visual)**:
   - Columns: `Category Name`, `Avg Rating`, `% Negative Reviews`, `Avg Delivery Days`, `Total Reviews`.
   - Conditional formatting on `% Negative Reviews` (red highlights for Office Furniture, Audio, Telephony).
