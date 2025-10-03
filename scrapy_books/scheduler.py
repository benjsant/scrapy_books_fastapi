"""
Scheduler module to run the Scrapy books spider periodically
using APScheduler.
"""

import logging
import subprocess
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler

# Logging setup
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "scheduler.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent
SCRAPY_DIR = PROJECT_ROOT

# Spider runner
def run_spider():
    """Launch the Scrapy 'books' spider via subprocess."""
    try:
        logger.info("Running Scrapy spider...")
        subprocess.run(["scrapy", "crawl", "books"], cwd=SCRAPY_DIR, check=True)
        logger.info("Scrapy spider finished successfully.")
    except subprocess.CalledProcessError as e:
        logger.error("Scrapy spider failed: %s", e)  # lazy formatting for Pylint

# Scheduler setup
def run_spider_job():
    """Job wrapper for scheduler to run the spider."""
    logger.info("Scheduler triggered: starting spider job...")
    run_spider()
    logger.info("Spider job finished.")

def start_scheduler(test_interval_minutes: int = 15):
    """Start APScheduler to run the spider periodically.
    For testing, the interval is set to every `test_interval_minutes` minutes.
    In production, consider setting this to every few hours or daily.
    """
    scheduler = BackgroundScheduler()

    # First run immediately
    run_spider_job()

    # Schedule periodic runs
    scheduler.add_job(
        run_spider_job,
        trigger='interval',
        minutes=test_interval_minutes,
        id='books_spider'
    )
    logger.info("Scheduler set to run every %d minutes for testing.", test_interval_minutes)

    scheduler.start()
    logger.info("APScheduler started. Spider will run automatically in the background.")
