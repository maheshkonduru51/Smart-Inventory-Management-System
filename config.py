"""Application configuration for Smart Inventory Management System."""

from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

DATABASE_PATH = DATA_DIR / "inventory.db"
LOG_FILE_PATH = LOGS_DIR / "app.log"

LOW_STOCK_THRESHOLD = 10
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "Admin@123"


def ensure_directories() -> None:
    """Create runtime directories required by the application."""
    for directory in (DATA_DIR, EXPORTS_DIR, REPORTS_DIR, LOGS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
