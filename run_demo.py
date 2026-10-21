"""
Retail Sales Intelligence & Forecasting Platform
One-Command Local Startup & Demonstration Orchestrator
==============================================================================
Command: python run_demo.py

Performs:
  1. Configuration & environment verification
  2. Database connectivity & Star Schema integrity check
  3. Preprocessing, EDA, and Forecasting artifact validation
  4. Real-time KPI reconciliation check (Python vs SQL)
  5. Local presentation dashboard server startup
  6. Automated browser launch at http://127.0.0.1:8501
==============================================================================
"""

import http.server
import json
import logging
import os
import socketserver
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import (
    CLEAN_DATA_FILE, RAW_DATA_FILE, FORECASTS_DIR, FIGURES_DIR,
    DASHBOARD_HOST, DASHBOARD_PORT, DB_TYPE
)
from src.database.connection import get_db_engine
from src.database.star_schema_loader import load_star_schema
from src.preprocessing import run_preprocessing_pipeline
from src.forecasting.model import evaluate_and_forecast
from src.analytics.eda import generate_eda_figures, generate_eda_report
from src.analytics.reconciliation import reconcile_kpis
from src.analytics.export_dashboard_data import export_dashboard_payload

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RetailDemo")


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler serving dashboard assets and /api/data endpoint."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR / "dashboard"), **kwargs)

    def do_GET(self):
        if self.path == "/api/data":
            data_json_path = BASE_DIR / "dashboard" / "data.json"
            if data_json_path.exists():
                content = data_json_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content)
                return
            else:
                self.send_error(404, "data.json not found")
                return

        return super().do_GET()

    def log_message(self, format, *args):
        # Silence routine static asset HTTP GET logs for clean recording terminal
        if "GET /api/data" in args[0] or "200" in args[1]:
            return
        super().log_message(format, *args)


def run_preflight_checks() -> None:
    """Verifies all components and prepares artifacts if needed."""
    print("=" * 80)
    print("  RETAIL SALES INTELLIGENCE & FORECASTING PLATFORM")
    print("  Preflight Verification & Startup Sequence")
    print("=" * 80)

    # 1. Pipeline & Preprocessing Check
    if not CLEAN_DATA_FILE.exists():
        print("[Preflight] Cleaned dataset missing; running Python ETL pipeline...")
        run_preprocessing_pipeline()
    else:
        print(f"[Preflight] Cleaned dataset verified: {CLEAN_DATA_FILE}")

    # 2. Database Connection Check
    engine, engine_name = get_db_engine()
    print(f"[Preflight] Active Database Engine: {engine_name.upper()}")

    # Check if Fact_Sales has data
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            cnt = conn.execute(text("SELECT COUNT(*) FROM Fact_Sales")).scalar()
            print(f"[Preflight] Fact_Sales verified with {cnt:,} analytical records.")
    except Exception as e:
        print(f"[Preflight] Fact_Sales unpopulated ({e}); initializing Star Schema...")
        load_star_schema(engine=engine, dialect=engine_name)

    # 3. Forecast Check
    fc_file = FORECASTS_DIR / "forecast_results.csv"
    if not fc_file.exists():
        print("[Preflight] Short-term forecast missing; generating model projections...")
        evaluate_and_forecast()
    else:
        print(f"[Preflight] Forecast artifacts verified: {fc_file}")

    # 4. EDA Check
    fig_check = FIGURES_DIR / "01_monthly_sales_trend.png"
    if not fig_check.exists():
        print("[Preflight] Generating EDA figures...")
        generate_eda_figures()
        generate_eda_report()
    else:
        print(f"[Preflight] Publication figures verified in {FIGURES_DIR}")

    # 5. Export Dashboard Payload
    export_dashboard_payload()

    # 6. Run Fast Reconciliation Check
    reconcile_kpis()


def start_server_and_open_browser(host: str = DASHBOARD_HOST, port: int = DASHBOARD_PORT) -> None:
    """Launches the HTTP presentation server and opens the browser."""
    # Find available port if default is occupied
    actual_port = port
    server = None
    for attempt in range(5):
        try:
            socketserver.TCPServer.allow_reuse_address = True
            server = socketserver.TCPServer((host, actual_port), DashboardHandler)
            break
        except OSError:
            actual_port += 1

    if server is None:
        print(f"[ERROR] Could not bind HTTP server to {host}:{port} or adjacent ports.")
        sys.exit(1)

    url = f"http://{host}:{actual_port}"
    print("\n" + "=" * 80)
    print(f"  DEMONSTRATION DASHBOARD IS RUNNING")
    print(f"  URL: {url}")
    print("=" * 80)
    print("  Controls:")
    print("    - Open in browser: Click the URL or browser will launch automatically")
    print("    - Presentation Mode: Click 'Presentation Mode' button in top right")
    print("    - Data Model & Star Schema: Click 'Data Model & Architecture' button")
    print("    - Press Ctrl+C in this terminal to stop the server")
    print("=" * 80 + "\n")

    # Launch browser after a short delay
    def _open():
        time.sleep(1.0)
        webbrowser.open(url)

    threading.Thread(target=_open, daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Shutdown] Stopping demonstration server... Done.")
        server.server_close()


if __name__ == "__main__":
    run_preflight_checks()
    start_server_and_open_browser()
