"""
Shoplytics REST API Main Application
Configures FastAPI app, CORS middleware, API router aggregation, and documentation metadata.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routers import health, sales, logistics, customers, products, reviews, analytics, geo

app = FastAPI(
    title="Shoplytics — E-Commerce Analytics & Business Intelligence API",
    description="""
# Shoplytics Analytics API 🚀

High-performance REST API engineered to serve real-time e-commerce analytics, automated KPI scorecards, customer RFM segmentation, logistics diagnostics, and ad-hoc analytical queries over 1.45M Brazilian e-commerce transactions.

## Analytical Domains Covered:
- 📊 **Executive Analytics**: Consolidated KPIs across sales, delivery, satisfaction, and retention.
- 💰 **Sales & Revenue**: GMV, item revenue, freight margins, AOV, monthly trends, and payment instruments.
- 🚚 **Logistics & SLAs**: Carrier on-time delivery rates, lead times by state, and delay duration metrics.
- 👥 **Customer & RFM**: 11-segment RFM cluster analysis, buyer loyalty cohorts, and individual customer lookups.
- 📦 **Products & Catalog**: Top revenue categories, 80/20 Pareto distribution, and dimensional weight tiers.
- ⭐ **Reviews & Sentiment**: Rating distributions, seller response times, and late delivery root-cause impact.
- 🗺️ **Geographic Analysis**: State and regional level rollup of revenue, order density, and customer distribution.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontends, web apps, and BI tools
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers under /api/v1
app.include_router(health.router, prefix="/api/v1")
app.include_router(sales.router, prefix="/api/v1")
app.include_router(logistics.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(reviews.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(geo.router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def root_metadata():
    """Welcome endpoint providing platform metadata and navigation links."""
    return JSONResponse({
        "platform": "Shoplytics E-Commerce Analytics Platform",
        "version": "1.0.0",
        "status": "online",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "health": "/api/v1/health",
            "executive_kpis": "/api/v1/analytics/kpi-summary",
            "sales_overview": "/api/v1/sales/overview",
            "monthly_trends": "/api/v1/sales/monthly-trends",
            "payment_methods": "/api/v1/sales/payment-methods",
            "logistics_overview": "/api/v1/logistics/overview",
            "state_logistics": "/api/v1/logistics/state-performance",
            "customer_rfm_summary": "/api/v1/customers/rfm-summary",
            "customer_repeat_cohorts": "/api/v1/customers/repeat-behavior",
            "top_categories": "/api/v1/products/top-categories",
            "pareto_analysis": "/api/v1/products/pareto-analysis",
            "reviews_overview": "/api/v1/reviews/overview",
            "delivery_delay_impact": "/api/v1/reviews/delay-impact"
        }
    })
