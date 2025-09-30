import subprocess
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Charger le .env depuis backend/
PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
SCRAPY_DIR = BACKEND_DIR / "scrapy_books"
DOCKER_COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"

load_dotenv(BACKEND_DIR / ".env")

# 1️⃣ Lancer PostgreSQL via Docker Compose
print("[INFO] Starting PostgreSQL container via Docker Compose...")
subprocess.run(["docker-compose", "-f", str(DOCKER_COMPOSE_FILE), "up", "-d"], check=True)

# Attente que PostgreSQL soit prêt
print("[INFO] Waiting for PostgreSQL to start...")
time.sleep(10)  # TODO: améliorer avec un vrai check

# 2️⃣ Initialiser la base de données
print("[INFO] Initializing database...")
subprocess.run([sys.executable, "-m", "db.init_db"], cwd=BACKEND_DIR, check=True)

# 3️⃣ Lancer Scrapy crawl
print("[INFO] Running Scrapy crawl...")
subprocess.run(["scrapy", "crawl", "books"], cwd=SCRAPY_DIR, check=True)

# 4️⃣ Lancer FastAPI
print("[INFO] Starting FastAPI server...")
subprocess.run([
    sys.executable, "-m", "uvicorn",
    "api.main:app",
    "--host", "127.0.0.1",
    "--port", "8000",
    "--reload"
], cwd=BACKEND_DIR)
