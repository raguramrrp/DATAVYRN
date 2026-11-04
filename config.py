import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
DB_DIR = STORAGE_DIR / "database"
DATASETS_DIR = STORAGE_DIR / "datasets"
IMAGES_DIR = STORAGE_DIR / "images"
ANNOTATIONS_DIR = STORAGE_DIR / "annotations"
MODELS_DIR = STORAGE_DIR / "models"
REPORTS_DIR = STORAGE_DIR / "reports"
EXPORTS_DIR = STORAGE_DIR / "exports"
ASSETS_DIR = BASE_DIR / "assets"
CSS_DIR = ASSETS_DIR / "css"

# Ensure all directories exist
for d in [STORAGE_DIR, DB_DIR, DATASETS_DIR, IMAGES_DIR, ANNOTATIONS_DIR, MODELS_DIR, REPORTS_DIR, EXPORTS_DIR, ASSETS_DIR, CSS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Database URI
DB_PATH = DB_DIR / "datavyrn.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Enterprise Design Tokens (Pure Light Theme)
THEME_TOKENS = {
    "surface": "#f8fafc",
    "sidebar": "#ffffff",
    "card": "#ffffff",
    "card_hover": "#f1f5f9",
    "border": "#e2e8f0",
    "border_muted": "#f1f5f9",
    "text_primary": "#0f172a",
    "text_muted": "#64748b",
    "text_secondary": "#475569",
    "accent": "#2563eb",
    "accent_hover": "#1d4ed8",
    "success": "#059669",
    "warning": "#d97706",
    "danger": "#dc2626"
}

# Supported File Formats
TABULAR_FORMATS = [".csv", ".xlsx", ".json"]
IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".webp"]

# Application Metadata
APP_NAME = "DATAVYRN"
APP_SUBTITLE = "DATA INTELLIGENCE WORKSPACE"
APP_VERSION = "2.0.0"
