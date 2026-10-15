"""
Shoplytics REST API Integration Tests
Tests all FastAPI endpoints for status codes, schema validation, data accuracy, and query guards.
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.api.main import app

@pytest.fixture(scope="module")
def client():
    """Create a test client instance for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client

def test_root_endpoint(client):
    """Verify root endpoint returns metadata and documentation links."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "/docs" in data["documentation"]["swagger_ui"]
    assert "health" in data["endpoints"]

def test_health_endpoint(client):
    """Verify health endpoint checks database and returns row counts."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["table_row_counts"]["fact_orders"] == 99441
    assert data["table_row_counts"]["analytics_customer_rfm"] > 90000

def test_executive_kpis(client):
    """Verify executive KPI summary returns expected macro numbers."""
    response = client.get("/api/v1/analytics/kpi-summary")
    assert response.status_code == 200
    data = response.json()
    assert data["delivered_orders_count"] == 96478
    assert data["gross_merchandise_value"] > 15000000
    assert 90.0 < data["on_time_delivery_rate_pct"] < 95.0
    assert 4.0 < data["average_customer_satisfaction_rating"] < 4.3

def test_sales_overview(client):
    """Verify sales overview endpoint metrics."""
    response = client.get("/api/v1/sales/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_orders"] == 96478
    assert data["average_order_value_aov"] > 130
    assert data["freight_to_revenue_pct"] > 15

def test_sales_monthly_trends(client):
    """Verify monthly trends longitudinal series."""
    response = client.get("/api/v1/sales/monthly-trends")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 20
    # Peak month Nov 2017
    months = [item["purchase_year_month"] for item in data]
    assert "2017-11" in months

def test_payment_methods(client):
    """Verify payment methods breakdown."""
    response = client.get("/api/v1/sales/payment-methods")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4
    # Credit Card has highest volume
    assert data[0]["payment_type"] == "Credit Card"
    assert data[0]["pct_of_total_volume"] > 70.0

def test_logistics_overview(client):
    """Verify logistics SLA KPIs."""
    response = client.get("/api/v1/logistics/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_delivered_orders"] == 96470
    assert data["on_time_orders"] > data["delayed_orders"]
    assert 90.0 < data["on_time_delivery_rate_pct"] < 93.0

def test_state_logistics(client):
    """Verify state logistics rankings."""
    response = client.get("/api/v1/logistics/state-performance?sort_by=delivered_orders&sort_desc=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 27
    # SP has largest delivered volume
    assert data[0]["customer_state"] == "SP"

def test_customer_rfm_summary(client):
    """Verify customer RFM cluster summary."""
    response = client.get("/api/v1/customers/rfm-summary")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    segments = [s["customer_segment"] for s in data]
    assert "Champions & Loyal" in segments

def test_customer_repeat_cohorts(client):
    """Verify customer loyalty cohorts."""
    response = client.get("/api/v1/customers/repeat-behavior")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    # 1. One-Time Buyer should represent ~96.9%
    one_time = next(c for c in data if "One-Time" in c["buyer_cohort"])
    assert one_time["pct_customers"] > 95.0

def test_customer_segment_pagination(client):
    """Verify pagination on segment customers list."""
    response = client.get("/api/v1/customers/segment/Champions%20%26%20Loyal?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    assert data[0]["customer_segment"] == "Champions & Loyal"
    assert "rfm_score" in data[0]

def test_customer_lookup(client):
    """Verify single customer profile and order history lookup."""
    sample_res = client.get("/api/v1/customers/segment/Champions%20%26%20Loyal?limit=1")
    assert sample_res.status_code == 200
    sample_id = sample_res.json()[0]["customer_unique_id"]

    lookup_res = client.get(f"/api/v1/customers/lookup/{sample_id}")
    assert lookup_res.status_code == 200
    data = lookup_res.json()
    assert data["profile"]["customer_unique_id"] == sample_id
    assert len(data["orders"]) >= 1

def test_customer_lookup_not_found(client):
    """Verify 404 for unknown customer ID."""
    response = client.get("/api/v1/customers/lookup/non_existent_customer_id_12345")
    assert response.status_code == 404

def test_products_top_categories(client):
    """Verify top product categories."""
    response = client.get("/api/v1/products/top-categories?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert data[0]["total_revenue"] > data[1]["total_revenue"]

def test_reviews_overview(client):
    """Verify customer reviews distribution."""
    response = client.get("/api/v1/reviews/overview")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    # 5-star is highest
    five_star = next(r for r in data if r["review_score"] == 5)
    assert five_star["pct_of_reviews"] > 50.0

def test_reviews_delay_impact(client):
    """Verify proof that late delivery crashes CSAT."""
    response = client.get("/api/v1/reviews/delay-impact")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    on_time = next(r for r in data if "On-Time" in r["delivery_performance"])
    delayed = next(r for r in data if "Delayed" in r["delivery_performance"])
    assert on_time["average_review_score"] > 4.0
    assert delayed["average_review_score"] < 3.0
    assert delayed["pct_1_star_reviews"] > 40.0

def test_custom_query_allowed(client):
    """Verify read-only analytical query execution."""
    payload = {"query": "SELECT customer_state, COUNT(*) AS count FROM dim_customers GROUP BY customer_state ORDER BY count DESC LIMIT 5;"}
    response = client.post("/api/v1/analytics/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["row_count"] == 5
    assert "customer_state" in data["columns"]

def test_custom_query_forbidden_statements(client):
    """Verify DDL and destructive DML queries are blocked."""
    forbidden = [
        {"query": "DROP TABLE fact_orders;"},
        {"query": "DELETE FROM dim_customers;"},
        {"query": "UPDATE fact_orders SET order_status = 'cancelled';"},
        {"query": "INSERT INTO dim_sellers VALUES ('abc', 'xyz', 'sp', 'br');"}
    ]
    for req in forbidden:
        res = client.post("/api/v1/analytics/query", json=req)
        assert res.status_code == 400
