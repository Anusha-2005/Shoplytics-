"""
Shoplytics API Pydantic Schemas
Defines request and response models for all API endpoints.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

# =============================================================================
# Health & Status Schemas
# =============================================================================

class HealthResponse(BaseModel):
    status: str = Field(..., description="System operational health status")
    database_type: str = Field(..., description="Database engine type (sqlite / mysql)")
    timestamp: str = Field(..., description="UTC ISO timestamp of health check")
    table_row_counts: Dict[str, int] = Field(..., description="Row counts per table in the star schema")


# =============================================================================
# Sales Domain Schemas
# =============================================================================

class SalesKPIOverview(BaseModel):
    total_orders: int
    total_order_entities: int
    total_item_revenue: float
    total_freight_revenue: float
    total_gross_merchandise_value: float
    average_item_price: float
    average_order_value_aov: float
    freight_to_revenue_pct: float

class MonthlyTrendItem(BaseModel):
    purchase_year_month: str
    monthly_orders: int
    monthly_revenue: float
    monthly_freight: float
    prev_month_revenue: Optional[float] = None
    mom_revenue_growth_pct: Optional[float] = None

class PaymentMethodItem(BaseModel):
    payment_type: str
    total_orders: int
    total_payment_value: float
    average_ticket_size: float
    avg_installments: float
    max_installments: int
    pct_of_total_volume: float

class HourlyPatternItem(BaseModel):
    purchase_day_name: str
    purchase_hour: int
    orders_count: int
    total_revenue: float


# =============================================================================
# Logistics Domain Schemas
# =============================================================================

class DeliverySLAOverview(BaseModel):
    total_delivered_orders: int
    on_time_orders: int
    delayed_orders: int
    on_time_delivery_rate_pct: float
    delay_rate_pct: float
    avg_actual_delivery_days: float
    avg_estimated_delivery_days: float
    avg_days_late_when_delayed: Optional[float] = None

class StateLogisticsItem(BaseModel):
    customer_state: str
    delivered_orders: int
    avg_delivery_days: float
    avg_estimated_days: float
    delayed_shipments: int
    state_delay_rate_pct: float
    avg_freight_cost: float

class RouteTypeItem(BaseModel):
    route_type: str
    total_orders: int
    avg_delivery_days: float
    avg_freight_cost: float
    delay_rate_pct: float


# =============================================================================
# Customer & RFM Domain Schemas
# =============================================================================

class RFMSegmentSummaryItem(BaseModel):
    customer_segment: str
    total_customers: int
    pct_of_customers: float
    segment_total_spend: float
    avg_monetary_spend: float
    avg_recency_days: float
    avg_frequency: float

class BuyerCohortItem(BaseModel):
    buyer_cohort: str
    customer_count: int
    pct_customers: float
    cohort_revenue: float
    avg_customer_lifetime_value: float

class CustomerStateItem(BaseModel):
    customer_state: str
    unique_customers: int
    orders_count: int
    state_merchandise_revenue: float
    avg_item_price: float
    avg_state_delivery_days: Optional[float] = None

class CustomerRFMProfile(BaseModel):
    customer_unique_id: str
    recency_days: int
    frequency: int
    monetary_value: float
    r_score: int
    f_score: int
    m_score: int
    rfm_score: Union[int, str]
    customer_segment: str

class CustomerOrderDetail(BaseModel):
    order_id: str
    order_status: str
    order_purchase_timestamp: str
    order_delivered_customer_date: Optional[str] = None
    is_delayed: Optional[int] = None
    total_order_value: Optional[float] = None
    review_score: Optional[int] = None

class CustomerDetailResponse(BaseModel):
    profile: CustomerRFMProfile
    orders: List[CustomerOrderDetail]


# =============================================================================
# Products & Categories Schemas
# =============================================================================

class CategoryRevenueItem(BaseModel):
    category: str
    total_orders: int
    units_sold: int
    total_revenue: float
    total_freight: float
    avg_unit_price: float
    revenue_market_share_pct: float

class CategoryParetoItem(BaseModel):
    category: str
    category_revenue: float
    cumulative_revenue: float
    cumulative_percentage: float

class WeightTierItem(BaseModel):
    weight_tier: str
    items_shipped: int
    avg_item_price: float
    avg_freight_charge: float
    avg_freight_to_price_ratio_pct: float


# =============================================================================
# Customer Reviews Schemas
# =============================================================================

class ReviewDistributionItem(BaseModel):
    review_score: int
    total_reviews: int
    pct_of_reviews: float
    comments_with_text: int
    avg_response_hours: Optional[float] = None

class ReviewDelayImpactItem(BaseModel):
    delivery_performance: str
    total_reviews: int
    average_review_score: float
    pct_1_star_reviews: float
    pct_5_star_reviews: float

class CategoryRatingItem(BaseModel):
    category: str
    review_count: int
    average_score: float
    pct_negative_reviews: Optional[float] = None
    pct_positive_reviews: Optional[float] = None
    avg_delivery_days: Optional[float] = None


# =============================================================================
# Executive KPI Summary Schema
# =============================================================================

class ExecutiveKPISummary(BaseModel):
    gross_merchandise_value: float
    total_merchandise_revenue: float
    total_freight_revenue: float
    delivered_orders_count: int
    average_order_value: float
    freight_to_revenue_pct: float
    on_time_delivery_rate_pct: float
    avg_actual_delivery_lead_time_days: float
    avg_estimated_delivery_sla_days: float
    average_customer_satisfaction_rating: float
    repeat_customer_loyalty_rate_pct: float
    top_payment_method: str
    top_revenue_category: str
