"""
Main entry point for the project.
- Starts PostgreSQL via Docker if enabled
- Waits for the DB to be ready
- Initializes tables via SQLModel
- Runs Scrapy spider via scheduler
- Starts FastAPI server
"""

import subprocess
import sys
from pathlib import Path
from db.database import init_db, wait_for_postgres
from config.settings import settings
from scrapy_books.scheduler import start_scheduler

# -----------------------------
# Project paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
DOCKER_COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"
BACKEND_DIR = PROJECT_ROOT / "api"

# -----------------------------
# Optional: Load secrets from Azure Key Vault
# -----------------------------
# settings.load_from_key_vault()

# -----------------------------
# Start PostgreSQL via Docker if enabled
# -----------------------------
if settings.docker_on:
    print("[INFO] Starting PostgreSQL container via Docker Compose...")
    subprocess.run(
        ["docker-compose", "-f", str(DOCKER_COMPOSE_FILE), "up", "-d"],
        check=True
    )

# -----------------------------
# Wait for PostgreSQL to be ready
# -----------------------------
print("[INFO] Waiting for PostgreSQL to be ready...")
wait_for_postgres()

# -----------------------------
# Initialize database
# -----------------------------
print("[INFO] Initializing database...")
init_db(drop_existing=False)
print("✅ Database tables created successfully!")

# -----------------------------
# Run Scrapy crawl via scheduler if enabled
# -----------------------------
if settings.run_scrapy:
    print("[INFO] Starting Scrapy scheduler...")
    start_scheduler()
else:
    print("[INFO] Skipping Scrapy crawl.")

# -----------------------------
# Start FastAPI server if enabled
# -----------------------------
if settings.run_api:
    print("[INFO] Starting FastAPI server...")
    subprocess.run(
        [
            sys.executable, "-m", "uvicorn",
            "api.main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload"
        ],
        cwd=PROJECT_ROOT,
        check=True
    )
else:
    print("[INFO] Skipping FastAPI server.")
