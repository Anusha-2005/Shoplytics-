"""
Shoplytics Sales & Revenue Router
Serves GMV metrics, monthly & daily trends, payment method dynamics, and order status breakdowns.
"""

from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from src.api.database import execute_query, execute_query_one, build_filter_conditions
from src.api.schemas import (
    SalesKPIOverview,
    MonthlyTrendItem,
    DailyTrendItem,
    OrderStatusItem,
    PaymentMethodItem,
    HourlyPatternItem
)

router = APIRouter(prefix="/sales", tags=["Sales & Revenue"])

@router.get("/overview", response_model=SalesKPIOverview)
def get_sales_overview(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    state: Optional[str] = Query(None, description="Customer state code"),
    category: Optional[str] = Query(None, description="Product category"),
    order_status: Optional[str] = Query("delivered", description="Order status filter")
):
    """Retrieve macro sales KPIs with dynamic filter parameters."""
    clauses, params = build_filter_conditions(start_date, end_date, state, category, order_status)
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    sql = f"""
    SELECT 
        COUNT(DISTINCT o.order_id) AS total_orders,
        COUNT(DISTINCT o.customer_id) AS total_order_entities,
        COALESCE(ROUND(SUM(oi.price), 2), 0.0) AS total_item_revenue,
        COALESCE(ROUND(SUM(oi.freight_value), 2), 0.0) AS total_freight_revenue,
        COALESCE(ROUND(SUM(oi.price + oi.freight_value), 2), 0.0) AS total_gross_merchandise_value,
        COALESCE(ROUND(AVG(oi.price), 2), 0.0) AS average_item_price,
        COALESCE(ROUND(SUM(oi.price) / NULLIF(COUNT(DISTINCT o.order_id), 0), 2), 0.0) AS average_order_value_aov,
        COALESCE(ROUND((SUM(oi.freight_value) / NULLIF(SUM(oi.price), 0)) * 100, 2), 0.0) AS freight_to_revenue_pct
    FROM fact_orders o
    JOIN fact_order_items oi ON o.order_id = oi.order_id
    JOIN dim_products p ON oi.product_id = p.product_id
    JOIN dim_customers c ON o.customer_id = c.customer_id
    {where_sql};
    """
    row = execute_query_one(sql, params)
    if not row or row.get("total_orders", 0) == 0:
        return SalesKPIOverview(
            total_orders=0,
            total_order_entities=0,
            total_item_revenue=0.0,
            total_freight_revenue=0.0,
            total_gross_merchandise_value=0.0,
            average_item_price=0.0,
            average_order_value_aov=0.0,
            freight_to_revenue_pct=0.0
        )
    return SalesKPIOverview(**row)

@router.get("/monthly-trends", response_model=List[MonthlyTrendItem])
def get_monthly_trends(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    order_status: Optional[str] = Query("delivered")
):
    """Retrieve monthly revenue, order volume, and Month-over-Month (MoM) growth rates."""
    clauses, params = build_filter_conditions(start_date, end_date, state, category, order_status)
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    sql = f"""
    WITH monthly_metrics AS (
        SELECT 
            o.purchase_year_month,
            COUNT(DISTINCT o.order_id) AS monthly_orders,
            ROUND(SUM(oi.price), 2) AS monthly_revenue,
            ROUND(SUM(oi.freight_value), 2) AS monthly_freight
        FROM fact_orders o
        JOIN fact_order_items oi ON o.order_id = oi.order_id
        JOIN dim_products p ON oi.product_id = p.product_id
        JOIN dim_customers c ON o.customer_id = c.customer_id
        {where_sql}
        GROUP BY o.purchase_year_month
    )
    SELECT 
        purchase_year_month,
        monthly_orders,
        monthly_revenue,
        monthly_freight,
        LAG(monthly_revenue, 1) OVER (ORDER BY purchase_year_month) AS prev_month_revenue,
        ROUND(
            ((monthly_revenue - LAG(monthly_revenue, 1) OVER (ORDER BY purchase_year_month)) / 
            NULLIF(LAG(monthly_revenue, 1) OVER (ORDER BY purchase_year_month), 0)) * 100, 2
        ) AS mom_revenue_growth_pct
    FROM monthly_metrics
    ORDER BY purchase_year_month;
    """
    rows = execute_query(sql, params)
    return [MonthlyTrendItem(**r) for r in rows]

@router.get("/daily-trends", response_model=List[DailyTrendItem])
def get_daily_trends(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    order_status: Optional[str] = Query("delivered"),
    limit: int = Query(60, ge=7, le=365)
):
    """Retrieve daily sales and order trends over time."""
    clauses, params = build_filter_conditions(start_date, end_date, state, category, order_status)
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    sql = f"""
    SELECT 
        SUBSTR(o.order_purchase_timestamp, 1, 10) AS date,
        COUNT(DISTINCT o.order_id) AS daily_orders,
        COALESCE(ROUND(SUM(oi.price), 2), 0.0) AS daily_revenue,
        COALESCE(ROUND(SUM(oi.freight_value), 2), 0.0) AS daily_freight
    FROM fact_orders o
    JOIN fact_order_items oi ON o.order_id = oi.order_id
    JOIN dim_products p ON oi.product_id = p.product_id
    JOIN dim_customers c ON o.customer_id = c.customer_id
    {where_sql}
    GROUP BY SUBSTR(o.order_purchase_timestamp, 1, 10)
    ORDER BY date DESC
    LIMIT :limit;
    """
    params["limit"] = limit
    rows = execute_query(sql, params)
    return [DailyTrendItem(**r) for r in reversed(rows)]

@router.get("/status-breakdown", response_model=List[OrderStatusItem])
def get_order_status_breakdown(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    state: Optional[str] = Query(None)
):
    """Retrieve order counts and proportions by fulfillment status."""
    clauses, params = build_filter_conditions(start_date, end_date, state, None, None)
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    sql = f"""
    WITH totals AS (
        SELECT COUNT(*) AS grand_total FROM fact_orders o
        JOIN dim_customers c ON o.customer_id = c.customer_id
        {where_sql}
    )
    SELECT 
        o.order_status,
        COUNT(o.order_id) AS order_count,
        ROUND((COUNT(o.order_id) * 100.0 / NULLIF((SELECT grand_total FROM totals), 0)), 2) AS percentage
    FROM fact_orders o
    JOIN dim_customers c ON o.customer_id = c.customer_id
    {where_sql}
    GROUP BY o.order_status
    ORDER BY order_count DESC;
    """
    rows = execute_query(sql, params)
    return [OrderStatusItem(**r) for r in rows]

@router.get("/payment-methods", response_model=List[PaymentMethodItem])
def get_payment_methods(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    order_status: Optional[str] = Query("delivered")
):
    """Retrieve payment instrument distributions, installment adoption, and ticket sizes."""
    clauses, params = build_filter_conditions(start_date, end_date, state, None, order_status)
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    sql = f"""
    WITH pay_agg AS (
        SELECT 
            p.payment_type,
            COUNT(DISTINCT p.order_id) AS total_orders,
            ROUND(SUM(p.payment_value), 2) AS total_payment_value,
            ROUND(AVG(p.payment_value), 2) AS average_ticket_size,
            ROUND(AVG(p.payment_installments), 1) AS avg_installments,
            MAX(p.payment_installments) AS max_installments
        FROM fact_order_payments p
        JOIN fact_orders o ON p.order_id = o.order_id
        JOIN dim_customers c ON o.customer_id = c.customer_id
        {where_sql}
        GROUP BY p.payment_type
    ),
    grand_total AS (
        SELECT SUM(total_payment_value) AS sum_all FROM pay_agg
    )
    SELECT 
        p.payment_type,
        p.total_orders,
        p.total_payment_value,
        p.average_ticket_size,
        p.avg_installments,
        p.max_installments,
        COALESCE(ROUND((p.total_payment_value / NULLIF((SELECT sum_all FROM grand_total), 0)) * 100, 2), 0.0) AS pct_of_total_volume
    FROM pay_agg p
    ORDER BY p.total_payment_value DESC;
    """
    rows = execute_query(sql, params)
    return [PaymentMethodItem(**r) for r in rows]

@router.get("/hourly-patterns", response_model=List[HourlyPatternItem])
def get_hourly_patterns(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    limit: int = Query(24, ge=1, le=168)
):
    """Analyze purchasing behavior grouped by day of week and order hour."""
    clauses, params = build_filter_conditions(start_date, end_date, state, None, "delivered")
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    sql = f"""
    SELECT 
        o.purchase_day_name,
        o.purchase_hour,
        COUNT(DISTINCT o.order_id) AS orders_count,
        ROUND(SUM(oi.price), 2) AS total_revenue
    FROM fact_orders o
    JOIN fact_order_items oi ON o.order_id = oi.order_id
    JOIN dim_customers c ON o.customer_id = c.customer_id
    {where_sql}
    GROUP BY o.purchase_day_name, o.purchase_hour
    ORDER BY total_revenue DESC
    LIMIT :limit;
    """
    params["limit"] = limit
    rows = execute_query(sql, params)
    return [HourlyPatternItem(**r) for r in rows]
