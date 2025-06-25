# Prothom Alo Scraper Project

This Django project scrapes news articles from Prothom Alo's politics section,
indexes them into Elasticsearch, and provides APIs to trigger scraping and search articles.
It uses Celery for asynchronous task management and Redis as a message broker.

## Prerequisites

1.  **Python 3.8+**
2.  **Pip** (Python package installer)
3.  **Redis Server**: Ensure you have a Redis server running.
    -   Default connection: `redis://localhost:6379/0`
4.  **Elasticsearch Server**: Ensure you have an Elasticsearch server running.
    -   Default connection: `http://localhost:9200` (user: `elastic`, pass: `JvQhvZYl`)
    -   These can be configured in `prothomalo_scraper_project/settings.py` or via environment variables.

## Setup Instructions

1.  **Clone the Repository (or ensure you have the project files):**
    ```bash
    # git clone <repository_url> # If applicable
    cd prothomalo_scraper_project
    ```

2.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    Due to potential issues with automated package installation during generation,
    ensure you have `pip` working and then run:
    ```bash
    pip install -r requirements.txt
    ```
    If `requirements.txt` is missing or incomplete, you may need to install the following manually:
    ```bash
    pip install django elasticsearch celery redis djangorestframework requests beautifulsoup4
    ```

4.  **Configure Settings (Optional):**
    -   Elasticsearch connection details (`ES_HOST`, `ES_USER`, `ES_PASSWORD`, `ES_INDEX_NAME`, `ES_VERIFY_CERTS`) are in `prothomalo_scraper_project/settings.py`.
    -   Redis connection details (`CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`) are also in `prothomalo_scraper_project/settings.py`.
    -   You can override these using environment variables or a `local_settings.py` file (not provided, but a common Django pattern).

5.  **Run Django Migrations:**
    (Although this project doesn't heavily use the Django DB for scraper data, it's good practice for Django admin and other potential features).
    ```bash
    python manage.py migrate
    ```

6.  **Create a Django Superuser (Optional, for Admin Interface):**
    ```bash
    python manage.py createsuperuser
    ```

## Running the Project

You'll need to run three main components: the Django development server, the Celery worker, and ensure Redis & Elasticsearch are running.

1.  **Start Redis and Elasticsearch:**
    Ensure your Redis and Elasticsearch instances are running and accessible as per the configuration.

2.  **Start the Celery Worker:**
    Open a new terminal, navigate to the `prothomalo_scraper_project` directory, and activate your virtual environment. Then run:
    ```bash
    celery -A prothomalo_scraper_project worker -l info
    ```
    You should see the worker connect and discover the `run_prothomalo_scraper_task`.

3.  **Start the Django Development Server:**
    Open another new terminal, navigate to the `prothomalo_scraper_project` directory, and activate your virtual environment. Then run:
    ```bash
    python manage.py runserver
    ```
    The Django development server will typically start on `http://127.0.0.1:8000/`.

## API Endpoints

The API endpoints are available under the `/api/v1/` prefix.

*   **Start Scraping:**
    -   `POST /api/v1/scrape/start/`
    -   Description: Initiates the scraping process.
    -   Body (optional JSON): `{"max_pages": 5}` (If not provided, defaults to `Config.DEFAULT_MAX_PAGES` which is 2)
    -   Response:
        ```json
        {
            "task_id": "some-celery-task-id",
            "status": "PENDING", // or current status
            "message": "Scraping task initiated."
        }
        ```

*   **Check Scraping Task Status:**
    -   `GET /api/v1/scrape/status/<task_id>/`
    -   Description: Checks the status of a previously initiated scraping task.
    -   Response (Example for a completed task):
        ```json
        {
            "task_id": "some-celery-task-id",
            "status": "SUCCESS",
            "result": "Scraping pipeline completed successfully.",
            "error": null,
            "traceback": null
        }
        ```

*   **Search Articles:**
    -   `GET /api/v1/articles/search/`
    -   Description: Searches the indexed articles in Elasticsearch.
    -   Query Parameters:
        -   `q`: The search query string (e.g., `q=最新新闻`). Searches headline, content, author, location.
        -   `size`: Number of results per page (default: 10).
        -   `from`: Offset for pagination (default: 0).
    -   Response (Example):
        ```json
        {
            "total_hits": 150, // Total matching documents in Elasticsearch
            "articles": [
                {
                    "url": "https://www.prothomalo.com/politics/article/slug1",
                    "headline": "Sample Headline 1",
                    "author": "Author Name",
                    "location": "Dhaka",
                    "published_at": "2023-10-26T10:00:00Z", // Or the parsed date-time string
                    "content": "Article content snippet...",
                    "scraped_at": "2023-10-27T12:30:00Z",
                    "word_count": 300
                }
                // ... more articles
            ]
        }
        ```

## Notes

*   **Elasticsearch Index:** The scraper will attempt to create the Elasticsearch index (`prothomalo_politics` by default) with the required mapping if it doesn't already exist when a scraping task is run.
*   **Error Handling:** Check the logs from the Django server and Celery worker for detailed error information. The scraper script (`scraper_app/scraper.py`) also produces its own log file (`prothomalo_scraper.log` by default, though this might be superseded by Django/Celery logging).
*   **Initial Scraping:** After setting up, you'll need to trigger the scraping task via the API to populate Elasticsearch with articles.
```
