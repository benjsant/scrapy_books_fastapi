# scrapy_books/scheduler.py
import subprocess
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
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
        logging.StreamHandler()  # logs also to console
    ]
)
logger = logging.getLogger(__name__)

# -----------------------------
# Paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
SCRAPY_DIR = PROJECT_ROOT  # scrapy.cfg is here

# -----------------------------
# Spider runner
# -----------------------------
def run_spider():
    """
    Launch the Scrapy 'books' spider via subprocess.
    The pipeline handles snapshots and purge automatically.
    """
    try:
        logger.info("Running Scrapy spider...")
        subprocess.run(["scrapy", "crawl", "books"], cwd=SCRAPY_DIR, check=True)
        logger.info("Scrapy spider finished successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Scrapy spider failed: {e}")

# -----------------------------
# Scheduler setup
# -----------------------------
def run_spider_job():
    """
    Job wrapper for scheduler to run the spider.
    """
    logger.info("Scheduler triggered: starting spider job...")
    run_spider()
    logger.info("Spider job finished.")

def start_scheduler(test_interval_minutes: int = 2):
    """
    Start the APScheduler to run the Scrapy spider periodically.

    :param test_interval_minutes: interval in minutes for testing; can switch to hours in production
    """
    scheduler = BackgroundScheduler()

    # --- First run immediately ---
    run_spider_job()

    # --- Schedule periodic spider run ---
    scheduler.add_job(
        run_spider_job,
        trigger='interval',
        minutes=test_interval_minutes,
        id='books_spider'
    )
    logger.info(f"Scheduler set to run every {test_interval_minutes} minutes for testing.")

    scheduler.start()
    logger.info("APScheduler started. Spider will run automatically in the background.")
