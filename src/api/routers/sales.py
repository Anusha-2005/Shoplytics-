"""
Shoplytics Sales & Revenue Router
Serves GMV metrics, monthly trends, payment method dynamics, and temporal order patterns.
"""

from typing import List
from fastapi import APIRouter, Query, HTTPException
from src.api.database import execute_query, execute_query_one
from src.api.schemas import (
    SalesKPIOverview,
    MonthlyTrendItem,
    PaymentMethodItem,
    HourlyPatternItem
)

router = APIRouter(prefix="/sales", tags=["Sales & Revenue"])

@router.get("/overview", response_model=SalesKPIOverview)
def get_sales_overview():
    """Retrieve macro sales KPIs across all delivered orders."""
    sql = """
    SELECT 
        COUNT(DISTINCT o.order_id) AS total_orders,
        COUNT(DISTINCT o.customer_id) AS total_order_entities,
        ROUND(SUM(oi.price), 2) AS total_item_revenue,
        ROUND(SUM(oi.freight_value), 2) AS total_freight_revenue,
        ROUND(SUM(oi.total_item_value), 2) AS total_gross_merchandise_value,
        ROUND(AVG(oi.price), 2) AS average_item_price,
        ROUND(SUM(oi.price) / COUNT(DISTINCT o.order_id), 2) AS average_order_value_aov,
        ROUND((SUM(oi.freight_value) / SUM(oi.price)) * 100, 2) AS freight_to_revenue_pct
    FROM fact_orders o
    JOIN fact_order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered';
    """
    row = execute_query_one(sql)
    if not row:
        raise HTTPException(status_code=404, detail="No sales data found.")
    return SalesKPIOverview(**row)

@router.get("/monthly-trends", response_model=List[MonthlyTrendItem])
def get_monthly_trends():
    """Retrieve longitudinal monthly revenue, order volume, and Month-over-Month (MoM) growth rates."""
    sql = """
    WITH monthly_metrics AS (
        SELECT 
            o.purchase_year_month,
            COUNT(DISTINCT o.order_id) AS monthly_orders,
            ROUND(SUM(oi.price), 2) AS monthly_revenue,
            ROUND(SUM(oi.freight_value), 2) AS monthly_freight
        FROM fact_orders o
        JOIN fact_order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'delivered'
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
            LAG(monthly_revenue, 1) OVER (ORDER BY purchase_year_month)) * 100, 2
        ) AS mom_revenue_growth_pct
    FROM monthly_metrics
    ORDER BY purchase_year_month;
    """
    rows = execute_query(sql)
    return [MonthlyTrendItem(**r) for r in rows]

@router.get("/payment-methods", response_model=List[PaymentMethodItem])
def get_payment_methods():
    """Retrieve transaction breakdown by payment instrument, average installments, and ticket sizes."""
    sql = """
    SELECT 
        p.payment_type,
        COUNT(DISTINCT p.order_id) AS total_orders,
        ROUND(SUM(p.payment_value), 2) AS total_payment_value,
        ROUND(AVG(p.payment_value), 2) AS average_ticket_size,
        ROUND(AVG(p.payment_installments), 1) AS avg_installments,
        MAX(p.payment_installments) AS max_installments,
        ROUND((SUM(p.payment_value) / (SELECT SUM(payment_value) FROM fact_order_payments)) * 100, 2) AS pct_of_total_volume
    FROM fact_order_payments p
    GROUP BY p.payment_type
    ORDER BY total_payment_value DESC;
    """
    rows = execute_query(sql)
    return [PaymentMethodItem(**r) for r in rows]

@router.get("/hourly-patterns", response_model=List[HourlyPatternItem])
def get_hourly_patterns(limit: int = Query(20, ge=1, le=168, description="Number of peak day-hour combinations to return")):
    """Analyze peak purchasing behavior grouped by day of week and order hour."""
    sql = f"""
    SELECT 
        o.purchase_day_name,
        o.purchase_hour,
        COUNT(DISTINCT o.order_id) AS orders_count,
        ROUND(SUM(oi.price), 2) AS total_revenue
    FROM fact_orders o
    JOIN fact_order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.purchase_day_name, o.purchase_hour
    ORDER BY total_revenue DESC
    LIMIT :limit;
    """
    rows = execute_query(sql, {"limit": limit})
    return [HourlyPatternItem(**r) for r in rows]
