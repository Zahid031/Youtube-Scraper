# YouTube Scraper

This project scrapes YouTube channel metadata and video information using `yt-dlp`, Django, Celery, and Redis.

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

- Backend API: [http://localhost:8000](http://localhost:8000)
- Frontend (Vite): [http://localhost:5173](http://localhost:5173)

### 📬 Example API usage

```bash
curl -X POST http://localhost:8000/api/tasks/scrape_channel/ \
  -H "Content-Type: application/json" \
  -d '{"channel_url": "https://www.youtube.com/@MrBeast", "max_videos": 5}'
```