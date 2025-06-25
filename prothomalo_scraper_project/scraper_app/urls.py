from django.urls import path
from .views import StartScrapingView, ScrapingTaskStatusView, ArticleSearchView

urlpatterns = [
    path('scrape/start/', StartScrapingView.as_view(), name='start_scraping'),
    path('scrape/status/<str:task_id>/', ScrapingTaskStatusView.as_view(), name='scraping_task_status'),
    path('articles/search/', ArticleSearchView.as_view(), name='article_search'),
]
