from celery import shared_task
from .scraper import ProthomAloScraper
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60) # Added bind=True and retry options
def run_prothomalo_scraper_task(self, max_pages=None):
    """
    Celery task to run the ProthomAlo news scraper.
    """
    logger.info(f"Starting ProthomAlo scraper task with max_pages: {max_pages}")
    try:
        scraper = ProthomAloScraper()
        success = scraper.run_scraping_pipeline(max_pages=max_pages)
        if success:
            logger.info("ProthomAlo scraper task completed successfully.")
            return "Scraping pipeline completed successfully."
        else:
            logger.warning("ProthomAlo scraper task completed with issues.")
            # Optionally, raise an exception to trigger retry if appropriate
            # For now, just logging a warning.
            return "Scraping pipeline completed with issues."
    except Exception as e:
        logger.error(f"Exception in ProthomAlo scraper task: {e}", exc_info=True)
        # Retry the task if it's a potentially transient issue
        # self.retry(exc=e) # Uncomment if you want celery to retry on any exception
        raise # Re-raise the exception to mark the task as failed and potentially retry by Celery settings
