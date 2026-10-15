# Shoplytics — Power BI Business Intelligence Module

This directory contains complete documentation, data modeling blueprints, DAX calculations, and report wireframes for the Shoplytics Power BI analytics dashboard.

## File Contents
- [data_model_guide.md](file:///power_bi/data_model_guide.md): Star Schema entity relationships, cardinalities, continuous calendar dimension, and import instructions.
- [DAX_Measures.md](file:///power_bi/DAX_Measures.md): 25+ production-grade DAX measures covering Financial KPIs, Delivery SLAs, RFM Customer Metrics, and Customer Satisfaction.
- [dashboard_wireframes.md](file:///power_bi/dashboard_wireframes.md): Detailed visual specs, 4-page dashboard layouts, slicers, and chart recommendations.

## Quick Start
1. Ensure the data pipeline has run: `python src/data_cleaning.py`.
2. Open **Power BI Desktop**.
3. Import the clean tables from `data/processed/`.
4. Create the Star Schema model as documented in `data_model_guide.md`.
5. Copy the measures from `DAX_Measures.md` into your model.
6. Assemble the 4 report pages following `dashboard_wireframes.md`.
