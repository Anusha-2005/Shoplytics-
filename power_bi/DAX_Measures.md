# Shoplytics — Power BI DAX Measures Library
Comprehensive repository of 25+ production-grade DAX measures for the Shoplytics E-Commerce Analytics Platform.

---

## 1. Core Financial & Sales Measures

### 1.1 Total Merchandise Revenue
```dax
Total Merchandise Revenue = 
SUM(fact_order_items[price])
```
- **Description**: Gross revenue generated strictly from item prices excluding freight.
- **Format**: Currency `R$ #,##0.00`

### 1.2 Total Freight Revenue
```dax
Total Freight Revenue = 
SUM(fact_order_items[freight_value])
```
- **Description**: Total shipping fees charged to buyers.
- **Format**: Currency `R$ #,##0.00`

### 1.3 Total Gross Merchandise Value (GMV)
```dax
Total GMV = 
[Total Merchandise Revenue] + [Total Freight Revenue]
```
- **Description**: Complete transaction volume processed across the platform.
- **Format**: Currency `R$ #,##0.00`

### 1.4 Total Orders
```dax
Total Orders = 
DISTINCTCOUNT(fact_orders[order_id])
```
- **Description**: Total count of unique orders placed.
- **Format**: Whole number `#,##0`

### 1.5 Delivered Orders
```dax
Delivered Orders = 
CALCULATE(
    [Total Orders],
    fact_orders[order_status] = "delivered"
)
```
- **Description**: Total orders successfully delivered to customers.
- **Format**: Whole number `#,##0`

### 1.6 Average Order Value (AOV)
```dax
Average Order Value (AOV) = 
DIVIDE([Total Merchandise Revenue], [Delivered Orders], 0)
```
- **Description**: Average merchandise spend per delivered order entity.
- **Format**: Currency `R$ #,##0.00`

### 1.7 Freight-to-Revenue Ratio (%)
```dax
Freight Ratio % = 
DIVIDE([Total Freight Revenue], [Total Merchandise Revenue], 0)
```
- **Description**: Proportion of freight burden relative to merchandise revenue.
- **Format**: Percentage `0.0%`

### 1.8 Prior Month Revenue (MoM Baseline)
```dax
Prior Month Revenue = 
CALCULATE(
    [Total Merchandise Revenue],
    DATEADD(dim_date[Date], -1, MONTH)
)
```
- **Description**: Merchandise revenue from previous month for comparative trend tracking.
- **Format**: Currency `R$ #,##0.00`

### 1.9 MoM Revenue Growth (%)
```dax
MoM Revenue Growth % = 
DIVIDE(
    [Total Merchandise Revenue] - [Prior Month Revenue],
    [Prior Month Revenue],
    0
)
```
- **Description**: Month-over-month revenue growth rate.
- **Format**: Percentage `+0.0%;-0.0%;0.0%`

### 1.10 Year-to-Date (YTD) Revenue
```dax
YTD Revenue = 
TOTALYTD(
    [Total Merchandise Revenue],
    dim_date[Date]
)
```
- **Description**: Cumulative revenue from January 1st to the selected date.
- **Format**: Currency `R$ #,##0.00`

---

## 2. Logistics & Delivery SLA Measures

### 2.1 On-Time Delivery Rate (%)
```dax
On-Time Delivery Rate % = 
VAR TotalDelivered = CALCULATE([Total Orders], fact_orders[order_status] = "delivered", NOT(ISBLANK(fact_orders[order_delivered_customer_date])))
VAR OnTimeOrders = CALCULATE([Total Orders], fact_orders[order_status] = "delivered", fact_orders[is_delayed] = 0)
RETURN
DIVIDE(OnTimeOrders, TotalDelivered, 0)
```
- **Description**: Percentage of orders delivered on or before the promised estimated delivery date.
- **Format**: Percentage `0.0%`

### 2.2 Late Delivery Rate (%)
```dax
Late Delivery Rate % = 
1 - [On-Time Delivery Rate %]
```
- **Description**: Percentage of orders delivered past the estimated SLA date.
- **Format**: Percentage `0.0%`

### 2.3 Average Delivery Lead Time (Days)
```dax
Avg Delivery Lead Time Days = 
AVERAGEX(
    FILTER(fact_orders, fact_orders[order_status] = "delivered" && NOT(ISBLANK(fact_orders[actual_delivery_days]))),
    fact_orders[actual_delivery_days]
)
```
- **Description**: Average duration from purchase timestamp to customer doorstep.
- **Format**: Decimal `0.0 Days`

### 2.4 Average Estimated Delivery Time (Days)
```dax
Avg Estimated Delivery Days = 
AVERAGEX(
    FILTER(fact_orders, NOT(ISBLANK(fact_orders[estimated_delivery_days]))),
    fact_orders[estimated_delivery_days]
)
```
- **Description**: Average estimated SLA delivery promise communicated at checkout.
- **Format**: Decimal `0.0 Days`

### 2.5 Average Delay Duration When Late (Days)
```dax
Avg Delay Days When Late = 
AVERAGEX(
    FILTER(fact_orders, fact_orders[is_delayed] = 1),
    fact_orders[delivery_delay_days]
)
```
- **Description**: Average overdue delay length specifically for breached shipments.
- **Format**: Decimal `0.0 Days`

---

## 3. Customer & Segmentation Measures

### 3.1 Unique Customers (Order Entities)
```dax
Unique Order Customers = 
DISTINCTCOUNT(fact_orders[customer_id])
```
- **Description**: Count of distinct order-level customer profiles.
- **Format**: Whole number `#,##0`

### 3.2 Real Unique Individuals
```dax
Real Unique Customers = 
DISTINCTCOUNT(dim_customers[customer_unique_id])
```
- **Description**: True count of unique human beings purchasing on the platform.
- **Format**: Whole number `#,##0`

### 3.3 Repeat Customer Count
```dax
Repeat Customers Count = 
COUNTROWS(
    FILTER(
        VALUES(dim_customers[customer_unique_id]),
        CALCULATE([Total Orders]) > 1
    )
)
```
- **Description**: Count of distinct consumers who placed 2 or more orders.
- **Format**: Whole number `#,##0`

### 3.4 Repeat Customer Rate (%)
```dax
Repeat Customer Rate % = 
DIVIDE([Repeat Customers Count], [Real Unique Customers], 0)
```
- **Description**: Loyalty penetration rate across the customer base.
- **Format**: Percentage `0.0%`

### 3.5 Average Customer Lifetime Value (CLV)
```dax
Average Customer LTV = 
DIVIDE([Total Merchandise Revenue], [Real Unique Customers], 0)
```
- **Description**: Average platform spend per unique customer lifetime.
- **Format**: Currency `R$ #,##0.00`

---

## 4. Customer Review & Satisfaction Measures

### 4.1 Average Review Score
```dax
Average Review Score = 
AVERAGE(fact_order_reviews[review_score])
```
- **Description**: Mean rating given across all reviewed orders (1 to 5 scale).
- **Format**: Decimal `0.00`

### 4.2 Total Reviews Count
```dax
Total Reviews = 
COUNT(fact_order_reviews[review_id])
```
- **Description**: Total customer reviews submitted.
- **Format**: Whole number `#,##0`

### 4.3 Positive Reviews % (4-5 Stars)
```dax
Positive Reviews % = 
VAR HighScore = CALCULATE([Total Reviews], fact_order_reviews[review_score] >= 4)
RETURN
DIVIDE(HighScore, [Total Reviews], 0)
```
- **Description**: Percentage of reviews scoring 4 or 5 stars.
- **Format**: Percentage `0.0%`

### 4.4 Negative Reviews % (1-2 Stars)
```dax
Negative Reviews % = 
VAR LowScore = CALCULATE([Total Reviews], fact_order_reviews[review_score] <= 2)
RETURN
DIVIDE(LowScore, [Total Reviews], 0)
```
- **Description**: Percentage of reviews indicating severe dissatisfaction (1 or 2 stars).
- **Format**: Percentage `0.0%`

### 4.5 Net Promoter Proxy Score (NPS Proxy)
```dax
NPS Proxy Score = 
([Positive Reviews %] - [Negative Reviews %]) * 100
```
- **Description**: Proxy Net Promoter Score computed as (% Promoters - % Detractors).
- **Format**: Number `+0.0;-0.0;0.0`

### 4.6 Review Rating for Delayed Orders
```dax
Rating - Delayed Orders = 
CALCULATE(
    [Average Review Score],
    fact_orders[is_delayed] = 1
)
```
- **Description**: Average customer satisfaction score when delivery arrives late.
- **Format**: Decimal `0.00`

### 4.7 Review Rating for On-Time Orders
```dax
Rating - On-Time Orders = 
CALCULATE(
    [Average Review Score],
    fact_orders[is_delayed] = 0
)
```
- **Description**: Average customer satisfaction score when SLA is fulfilled.
- **Format**: Decimal `0.00`
