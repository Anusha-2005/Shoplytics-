"""
Shoplytics Master Pipeline Orchestrator
Executes the full end-to-end workflow:
1. Data Quality Inspection
2. Data Cleaning & Feature Engineering
3. Database Ingestion (MySQL / SQLite)
4. Analytical SQL Queries Execution
5. Executive Excel Report Generation
6. Automated Tests & Data Reconciliation
"""

import sys
import logging
from pathlib import Path
import subprocess

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.data_inspection import inspect_dataset_files
from src.data_cleaning import run_cleaning_pipeline
from src.database_loader import load_tables
from src.run_sql_queries import run_all_queries
from src.excel_report_generator import build_executive_workbook

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ShoplyticsOrchestrator")

def execute_pipeline():
    logger.info("="*70)
    logger.info("STARTING SHOPLYTICS END-TO-END ANALYTICS PIPELINE")
    logger.info("="*70)

    # Step 1: Data Inspection
    logger.info("\n>>> Step 1/6: Running Data Quality Inspection...")
    inspect_dataset_files()

    # Step 2: Data Cleaning & Feature Engineering
    logger.info("\n>>> Step 2/6: Running Data Cleaning & Feature Engineering Pipeline...")
    run_cleaning_pipeline()

    # Step 3: Database Loading
    logger.info("\n>>> Step 3/6: Loading Data into Database (Star Schema)...")
    load_tables()

    # Step 4: Analytical SQL Queries
    logger.info("\n>>> Step 4/6: Executing Analytical SQL Queries...")
    run_all_queries()

    # Step 5: Executive Excel Workbook Generation
    logger.info("\n>>> Step 5/6: Generating Executive Excel Report...")
    excel_path = build_executive_workbook()

    # Step 6: Automated Test Verification
    logger.info("\n>>> Step 6/6: Running Automated Quality & Reconciliation Tests...")
    test_result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], capture_output=False)
    
    logger.info("="*70)
    if test_result.returncode == 0:
        logger.info("SHOPLYTICS PIPELINE COMPLETED SUCCESSFULLY! ALL TESTS PASSED.")
    else:
        logger.warning("SHOPLYTICS PIPELINE COMPLETED WITH TEST WARNINGS.")
    logger.info(f"Generated Reports Location: {Path('reports').resolve()}")
    logger.info(f"Excel Dashboard: {excel_path}")
    logger.info("="*70)

if __name__ == "__main__":
    execute_pipeline()
