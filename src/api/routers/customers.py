"""
Shoplytics Customer & RFM Segmentation Router
Serves behavioral RFM segments, cohort retention metrics, customer geography, and granular profile lookups.
"""

from typing import List
from fastapi import APIRouter, Query, Path, HTTPException
from src.api.database import execute_query, execute_query_one
from src.api.schemas import (
    RFMSegmentSummaryItem,
    BuyerCohortItem,
    CustomerStateItem,
    CustomerRFMProfile,
    CustomerOrderDetail,
    CustomerDetailResponse
)

router = APIRouter(prefix="/customers", tags=["Customers & RFM Segmentation"])

@router.get("/rfm-summary", response_model=List[RFMSegmentSummaryItem])
def get_rfm_summary():
    """Retrieve RFM segment portfolio breakdown including customer counts, GMV contributions, and behavioral averages."""
    sql = """
    SELECT 
        customer_segment,
        COUNT(customer_unique_id) AS total_customers,
        ROUND((COUNT(customer_unique_id) * 100.0 / (SELECT COUNT(*) FROM analytics_customer_rfm)), 2) AS pct_of_customers,
        ROUND(SUM(monetary_value), 2) AS segment_total_spend,
        ROUND(AVG(monetary_value), 2) AS avg_monetary_spend,
        ROUND(AVG(recency_days), 1) AS avg_recency_days,
        ROUND(AVG(frequency), 2) AS avg_frequency
    FROM analytics_customer_rfm
    GROUP BY customer_segment
    ORDER BY segment_total_spend DESC;
    """
    rows = execute_query(sql)
    return [RFMSegmentSummaryItem(**r) for r in rows]

@router.get("/repeat-behavior", response_model=List[BuyerCohortItem])
def get_repeat_behavior():
    """Analyze customer loyalty cohorts (1-time buyers vs repeat/VIP customers) and lifetime spend."""
    sql = """
    WITH customer_order_frequencies AS (
        SELECT 
            c.customer_unique_id,
            COUNT(DISTINCT o.order_id) AS lifetime_orders,
            SUM(oi.price) AS lifetime_spend
        FROM fact_orders o
        JOIN dim_customers c ON o.customer_id = c.customer_id
        JOIN fact_order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY c.customer_unique_id
    )
    SELECT 
        CASE 
            WHEN lifetime_orders = 1 THEN '1. One-Time Buyer'
            WHEN lifetime_orders = 2 THEN '2. Repeat Buyer (2 Orders)'
            WHEN lifetime_orders BETWEEN 3 AND 5 THEN '3. Frequent Buyer (3-5 Orders)'
            ELSE '4. Power VIP Buyer (>5 Orders)'
        END AS buyer_cohort,
        COUNT(customer_unique_id) AS customer_count,
        ROUND((COUNT(customer_unique_id) * 100.0 / (SELECT COUNT(*) FROM customer_order_frequencies)), 2) AS pct_customers,
        ROUND(SUM(lifetime_spend), 2) AS cohort_revenue,
        ROUND(AVG(lifetime_spend), 2) AS avg_customer_lifetime_value
    FROM customer_order_frequencies
    GROUP BY buyer_cohort
    ORDER BY buyer_cohort;
    """
    rows = execute_query(sql)
    return [BuyerCohortItem(**r) for r in rows]

@router.get("/state-distribution", response_model=List[CustomerStateItem])
def get_state_distribution():
    """Retrieve customer geographic concentration and average item price by state."""
    sql = """
    SELECT 
        c.customer_state,
        COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
        COUNT(DISTINCT o.order_id) AS orders_count,
        ROUND(SUM(oi.price), 2) AS state_merchandise_revenue,
        ROUND(AVG(oi.price), 2) AS avg_item_price,
        ROUND(AVG(o.actual_delivery_days), 1) AS avg_state_delivery_days
    FROM fact_orders o
    JOIN dim_customers c ON o.customer_id = c.customer_id
    JOIN fact_order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_state
    ORDER BY state_merchandise_revenue DESC;
    """
    rows = execute_query(sql)
    return [CustomerStateItem(**r) for r in rows]

@router.get("/segment/{segment_name}", response_model=List[CustomerRFMProfile])
def get_customers_by_segment(
    segment_name: str = Path(..., description="Name of RFM segment, e.g. 'Champions & Loyal', 'Promising Recent'"),
    limit: int = Query(50, ge=1, le=200, description="Page limit"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Retrieve paginated customer profiles belonging to an RFM behavioral cluster."""
    sql = """
    SELECT 
        customer_unique_id,
        recency_days,
        frequency,
        ROUND(monetary_value, 2) AS monetary_value,
        r_score,
        f_score,
        m_score,
        rfm_score,
        customer_segment
    FROM analytics_customer_rfm
    WHERE LOWER(customer_segment) = LOWER(:seg)
    ORDER BY monetary_value DESC
    LIMIT :limit OFFSET :offset;
    """
    rows = execute_query(sql, {"seg": segment_name, "limit": limit, "offset": offset})
    if not rows and offset == 0:
        # Check if segment even exists
        check_sql = "SELECT DISTINCT customer_segment FROM analytics_customer_rfm;"
        valid_segs = [r["customer_segment"] for r in execute_query(check_sql)]
        raise HTTPException(
            status_code=404, 
            detail=f"No customers found for segment '{segment_name}'. Available segments: {valid_segs}"
        )
    return [CustomerRFMProfile(**r) for r in rows]

@router.get("/lookup/{customer_unique_id}", response_model=CustomerDetailResponse)
def lookup_customer(customer_unique_id: str = Path(..., description="Unique customer UUID hash")):
    """Lookup a single customer profile with RFM metrics and their historical orders."""
    # 1. Fetch RFM profile
    rfm_sql = """
    SELECT 
        customer_unique_id,
        recency_days,
        frequency,
        ROUND(monetary_value, 2) AS monetary_value,
        r_score,
        f_score,
        m_score,
        rfm_score,
        customer_segment
    FROM analytics_customer_rfm
    WHERE customer_unique_id = :cid;
    """
    rfm_row = execute_query_one(rfm_sql, {"cid": customer_unique_id})
    if not rfm_row:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_unique_id}' not found in RFM analytics.")

    # 2. Fetch order history
    orders_sql = """
    SELECT 
        o.order_id,
        o.order_status,
        o.order_purchase_timestamp,
        o.order_delivered_customer_date,
        o.is_delayed,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS total_order_value,
        MAX(r.review_score) AS review_score
    FROM fact_orders o
    JOIN dim_customers c ON o.customer_id = c.customer_id
    LEFT JOIN fact_order_items oi ON o.order_id = oi.order_id
    LEFT JOIN fact_order_reviews r ON o.order_id = r.order_id
    WHERE c.customer_unique_id = :cid
    GROUP BY o.order_id, o.order_status, o.order_purchase_timestamp, o.order_delivered_customer_date, o.is_delayed
    ORDER BY o.order_purchase_timestamp DESC;
    """
    order_rows = execute_query(orders_sql, {"cid": customer_unique_id})

    return CustomerDetailResponse(
        profile=CustomerRFMProfile(**rfm_row),
        orders=[CustomerOrderDetail(**o) for o in order_rows]
    )
