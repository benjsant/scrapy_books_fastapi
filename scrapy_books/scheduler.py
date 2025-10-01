# scrapy_books/scheduler.py
import subprocess
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, select
from db.models import Book, BookSnapshot
from db.database import engine
import logging

# -----------------------------
# Logging setup
# -----------------------------
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "scheduler.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()  # pour voir aussi dans la console
    ]
)
logger = logging.getLogger(__name__)

# -----------------------------
# Paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
SCRAPY_DIR = PROJECT_ROOT  # scrapy.cfg est dans ce dossier

# -----------------------------
# Function to run Scrapy spider
# -----------------------------
def run_spider():
    """
    Launch the Scrapy 'books' spider via subprocess.
    """
    try:
        logger.info("Running Scrapy spider...")
        subprocess.run(["scrapy", "crawl", "books"], cwd=SCRAPY_DIR, check=True)
        logger.info("Scrapy spider finished successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Scrapy spider failed: {e}")

# -----------------------------
# Function to cleanup old snapshots
# -----------------------------
def cleanup_old_snapshots():
    """
    Keep a maximum of 6 snapshots for each book.
    If there are more than 6, delete the 2 oldest snapshots.
    """
    MAX_SNAPSHOTS = 6
    SNAPSHOTS_TO_DELETE = 2

    with Session(engine) as session:
        books = session.exec(select(Book)).all()
        for book in books:
            snapshots = session.exec(
                select(BookSnapshot)
                .where(BookSnapshot.book_id == book.id)
                .order_by(BookSnapshot.scraped_at.desc())
            ).all()
            if len(snapshots) > MAX_SNAPSHOTS:
                to_delete = snapshots[-SNAPSHOTS_TO_DELETE:]  # 2 oldest
                for snap in to_delete:
                    session.delete(snap)
        session.commit()
    logger.info("Old snapshots purged successfully.")

# -----------------------------
# Run Spider + Cleanup
# -----------------------------
def run_spider_and_cleanup():
    run_spider()
    cleanup_old_snapshots()

# -----------------------------
# Setup APScheduler
# -----------------------------
def start_scheduler():
    """
    Start the scheduler to run the Scrapy spider periodically.
    """
    scheduler = BackgroundScheduler()

    # --- First run immediately ---
    run_spider_and_cleanup()

    # --- Schedule every 24 hours (default) ---
    #scheduler.add_job(run_spider_and_cleanup, 'interval', hours=24, id='books_spider')
    #logger.info("Scheduler set to run every 24 hours.")

    # --- Optional: Uncomment for testing every 5 minutes ---
    scheduler.add_job(run_spider_and_cleanup, 'interval', minutes=3, id='books_spider_test')
    logger.info("Scheduler set to run every 5 minutes for testing.")

    scheduler.start()
    logger.info("APScheduler started. Spider will run automatically in the background.")
