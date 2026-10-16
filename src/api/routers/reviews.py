"""
Shoplytics Customer Reviews & Sentiment Router
Serves CSAT scores, review sentiment distributions, delivery delay impact diagnostics,
and lead time vs customer rating correlation buckets.
"""

from typing import List, Optional
from fastapi import APIRouter, Query
from src.api.database import execute_query, build_filter_conditions
from src.api.schemas import (
    ReviewDistributionItem,
    ReviewDelayImpactItem,
    CategoryRatingItem,
    LeadTimeReviewItem
)

router = APIRouter(prefix="/reviews", tags=["Customer Reviews & Sentiment"])

@router.get("/overview", response_model=List[ReviewDistributionItem])
def get_review_distribution(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    """Retrieve ratings distribution (1 to 5 stars), review percentage shares, and seller response times."""
    clauses, params = build_filter_conditions(start_date, end_date, state, category, "delivered")
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    sql = f"""
    WITH filtered_reviews AS (
        SELECT r.*
        FROM fact_order_reviews r
        JOIN fact_orders o ON r.order_id = o.order_id
        JOIN dim_customers c ON o.customer_id = c.customer_id
        LEFT JOIN fact_order_items oi ON o.order_id = oi.order_id
        LEFT JOIN dim_products p ON oi.product_id = p.product_id
        {where_sql}
    ),
    totals AS (
        SELECT COUNT(*) AS grand_count FROM filtered_reviews
    )
    SELECT 
        r.review_score,
        COUNT(r.review_id) AS total_reviews,
        COALESCE(ROUND((COUNT(r.review_id) * 100.0 / NULLIF((SELECT grand_count FROM totals), 0)), 2), 0.0) AS pct_of_reviews,
        SUM(r.has_review_comment) AS comments_with_text,
        ROUND(AVG(r.review_response_hours), 1) AS avg_response_hours
    FROM filtered_reviews r
    GROUP BY r.review_score
    ORDER BY r.review_score DESC;
    """
    rows = execute_query(sql, params)
    return [ReviewDistributionItem(**r) for r in rows]

@router.get("/delay-impact", response_model=List[ReviewDelayImpactItem])
def get_delay_impact(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    state: Optional[str] = Query(None)
):
    """Diagnose the empirical relationship between on-time vs delayed delivery and CSAT rating collapses."""
    clauses, params = build_filter_conditions(start_date, end_date, state, None, "delivered")
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    sql = f"""
    SELECT 
        CASE 
            WHEN o.is_delayed = 1 THEN 'Delayed Delivery (Past SLA)'
            ELSE 'On-Time / Early Delivery'
        END AS delivery_performance,
        COUNT(r.review_id) AS total_reviews,
        ROUND(AVG(r.review_score), 2) AS average_review_score,
        ROUND((SUM(CASE WHEN r.review_score = 1 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(r.review_id), 0)), 2) AS pct_1_star_reviews,
        ROUND((SUM(CASE WHEN r.review_score = 5 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(r.review_id), 0)), 2) AS pct_5_star_reviews
    FROM fact_order_reviews r
    JOIN fact_orders o ON r.order_id = o.order_id
    JOIN dim_customers c ON o.customer_id = c.customer_id
    {where_sql}
    GROUP BY o.is_delayed
    ORDER BY o.is_delayed ASC;
    """
    rows = execute_query(sql, params)
    return [ReviewDelayImpactItem(**r) for r in rows]

@router.get("/score-vs-leadtime", response_model=List[LeadTimeReviewItem])
def get_score_vs_leadtime():
    """Analyze customer review scores across delivery lead time duration tiers."""
    sql = """
    SELECT 
        CASE 
            WHEN o.actual_delivery_days <= 7 THEN '1. Under 7 Days'
            WHEN o.actual_delivery_days BETWEEN 8 AND 14 THEN '2. 8 to 14 Days'
            WHEN o.actual_delivery_days BETWEEN 15 AND 21 THEN '3. 15 to 21 Days'
            WHEN o.actual_delivery_days BETWEEN 22 AND 30 THEN '4. 22 to 30 Days'
            ELSE '5. Over 30 Days'
        END AS lead_time_bucket,
        COUNT(r.review_id) AS order_count,
        ROUND(AVG(r.review_score), 2) AS avg_review_score,
        ROUND((SUM(CASE WHEN r.review_score = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(r.review_id)), 2) AS pct_1_star,
        ROUND((SUM(CASE WHEN r.review_score = 5 THEN 1 ELSE 0 END) * 100.0 / COUNT(r.review_id)), 2) AS pct_5_star
    FROM fact_order_reviews r
    JOIN fact_orders o ON r.order_id = o.order_id
    WHERE o.order_status = 'delivered'
      AND o.actual_delivery_days IS NOT NULL
    GROUP BY lead_time_bucket
    ORDER BY lead_time_bucket;
    """
    rows = execute_query(sql)
    return [LeadTimeReviewItem(**r) for r in rows]

@router.get("/category-ratings", response_model=List[CategoryRatingItem])
def get_category_ratings(
    order: str = Query("asc", pattern="^(asc|desc)$", description="'asc' for lowest rated categories, 'desc' for highest rated"),
    min_reviews: int = Query(100, ge=10, description="Minimum review sample threshold"),
    limit: int = Query(10, ge=1, le=50, description="Number of categories to return")
):
    """Retrieve categories with the lowest or highest customer satisfaction ratings."""
    sql = f"""
    SELECT 
        p.product_category_formatted AS category,
        COUNT(r.review_id) AS review_count,
        ROUND(AVG(r.review_score), 2) AS average_score,
        ROUND((SUM(CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(r.review_id)), 2) AS pct_negative_reviews,
        ROUND((SUM(CASE WHEN r.review_score >= 4 THEN 1 ELSE 0 END) * 100.0 / COUNT(r.review_id)), 2) AS pct_positive_reviews,
        ROUND(AVG(o.actual_delivery_days), 1) AS avg_delivery_days
    FROM fact_order_reviews r
    JOIN fact_orders o ON r.order_id = o.order_id
    JOIN fact_order_items oi ON o.order_id = oi.order_id
    JOIN dim_products p ON oi.product_id = p.product_id
    WHERE o.order_status = 'delivered'
    GROUP BY p.product_category_formatted
    HAVING COUNT(r.review_id) >= :min_reviews
    ORDER BY average_score {order.upper()}
    LIMIT :limit;
    """
    rows = execute_query(sql, {"min_reviews": min_reviews, "limit": limit})
    return [CategoryRatingItem(**r) for r in rows]
