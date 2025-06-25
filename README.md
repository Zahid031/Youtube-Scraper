# YouTube Scraper

This project scrapes YouTube channel metadata and video information using `yt-dlp`, Django, Celery, and Redis.

## ✨ Features

- Scrape YouTube channel metadata (name, description, subscriber count, etc.).
- Scrape video details from a channel (title, views, likes, comments, publication date, etc.).
- Asynchronous task processing using Celery and Redis for efficient scraping of multiple videos or channels.
- Dockerized setup for easy deployment and consistent environments.
- RESTful API for initiating scraping tasks and retrieving results.
- Frontend UI (Vite + React) for interacting with the API.

## 🏗️ Project Structure

The project is composed of the following main components:

- **Backend (Django & Django REST Framework):**
  - `youtube_scraper/`: Main Django project directory.
  - `scraper/`: Django app handling the scraping logic, API views, models, and serializers.
  - **API Endpoints:** Exposes RESTful APIs for initiating scraping tasks and retrieving data.
- **Task Queue (Celery & Redis):**
  - **Celery (`youtube_scraper/celery.py`, `scraper/tasks.py`):** Manages asynchronous tasks for scraping YouTube data in the background, preventing API requests from timing out.
  - **Redis:** Acts as the message broker for Celery, queueing tasks and storing results.
- **Frontend (Vite + React):**
  - `Scraper-UI/`: Contains the user interface built with Vite and React.
  - Allows users to input channel URLs, start scraping tasks, and view scraped data.
- **Scraping Tool (`yt-dlp`):**
  - A powerful command-line program to download videos and extract metadata from YouTube and other sites. It's used internally by the Celery tasks.
- **Containerization (Docker & Docker Compose):**
  - `Dockerfile` (in root and `Scraper-UI/`): Defines the images for the backend and frontend services.
  - `docker-compose.yml`: Orchestrates the deployment of the Django application, Celery workers, Redis, and the frontend.

## 🐳 Run the application using Docker Compose

Make sure Docker and Docker Compose are installed on your machine.

### 📦 1. Clone the repository

```bash
git clone https://github.com/Zahid031/Youtube-Scraper.git
cd Youtube-Scraper
```

### 🛠️ 2. Build and run the containers

```bash
docker-compose up --build
```

### 🚀 3. Access the application

- Backend API: [http://localhost:8000/api/](http://localhost:8000/api/)
- API Documentation (Swagger UI): [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)
- Frontend (Vite): [http://localhost:5173](http://localhost:5173)

### 📬 API Usage

The API allows you to initiate scraping tasks and retrieve channel and video data.

**Explore the API interactively using Swagger UI:**

[http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)

This is the recommended way to understand the available endpoints, request parameters, and response structures.

**Example: Start a scraping task for a channel**

This example uses `curl` to send a POST request to the `/api/tasks/scrape_channel/` endpoint.

```bash
curl -X POST http://localhost:8000/api/tasks/scrape_channel/ \
  -H "Content-Type: application/json" \
  -d '{"channel_url": "https://www.youtube.com/@MrBeast", "max_videos": 5}'
```

**Parameters:**

*   `channel_url` (string, required): The URL of the YouTube channel to scrape.
*   `max_videos` (integer, optional): The maximum number of recent videos to scrape from the channel. If not provided, it might default to a system-defined limit or scrape all videos.

**Other Key Endpoints (explore via Swagger UI for details):**

*   `/api/channels/`: Lists all scraped channels or retrieves a specific channel.
*   `/api/videos/`: Lists all scraped videos or retrieves a specific video. Can be filtered by channel.
*   `/api/tasks/{task_id}/`: Retrieves the status and results of a specific scraping task.

## 🔧 Troubleshooting

- **`docker-compose up` fails with errors related to port conflicts:**
  - *Solution:* Ensure that ports 8000 (backend), 5173 (frontend), and 6379 (Redis) are not already in use by other applications on your system. You can either stop the conflicting application or change the port mappings in the `docker-compose.yml` file. For example, to change the backend port from 8000 to 8001, modify the `ports` section for the `backend` service:
    ```yaml
    services:
      backend:
        ports:
          - "8001:8000" # Host:Container
    ```

- **Scraping tasks seem to get stuck or fail silently:**
  - *Solution:* Check the logs of the Celery worker and backend containers:
    ```bash
    docker-compose logs backend
    docker-compose logs worker
    ```
  - Look for error messages or stack traces that might indicate the cause (e.g., network issues, problems with `yt-dlp`, errors in task processing).
  - Ensure Redis is running correctly: `docker-compose logs redis`.

- **`yt-dlp` errors (e.g., "Unable to extract video data"):**
  - *Solution:* `yt-dlp` relies on being up-to-date to handle changes on YouTube. The Docker image build process should fetch a recent version. If you suspect it's outdated or encounter persistent extraction issues:
    1. Try to update `yt-dlp` locally to see if it resolves the issue for a specific URL.
    2. Consider rebuilding the Docker image with the `--no-cache` option to ensure fresh dependencies are pulled: `docker-compose up --build --no-cache backend worker`.
    3. The specific channel or video might have restrictions or use formats that `yt-dlp` currently struggles with.

- **Frontend shows errors or doesn't connect to the backend:**
  - *Solution:*
    1. Verify the backend is running and accessible at `http://localhost:8000/api/`.
    2. Check the browser's developer console (usually F12) for error messages on the frontend.
    3. Ensure the `VITE_API_BASE_URL` in `Scraper-UI/.env.development` or `Scraper-UI/.env.production` (if applicable) is correctly pointing to your backend API URL. By default, it's usually `/api` which relies on proxying through Vite's dev server or a similar setup in production.
    4. Check `docker-compose logs frontend` for any build or runtime errors.

## 🤝 Contributing

Contributions are welcome! If you'd like to contribute, please follow these general guidelines:

1.  **Fork the repository** and create your branch from `main`.
2.  **Make your changes.**
    - Ensure your code follows the existing style and conventions.
    - Add tests for any new features or bug fixes.
    - Update documentation if necessary.
3.  **Test your changes thoroughly.**
4.  **Create a pull request** to the `main` branch of the original repository.
    - Provide a clear description of your changes and why they are needed.
    - Reference any relevant issues.

If you're planning to add a major feature, it's a good idea to open an issue first to discuss your ideas.

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details (if a LICENSE file is present).
