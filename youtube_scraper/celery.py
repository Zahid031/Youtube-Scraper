from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youtube_scraper.settings')

app = Celery('youtube_scraper')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# from __future__ import absolute_import, unicode_literals
# import os
# from celery import Celery

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youtube_scraper.settings')

# app = Celery('youtube_scraper')
# app.config_from_object('django.conf:settings', namespace='CELERY')

# # Performance optimizations
# app.conf.update(
#     task_serializer='json',
#     accept_content=['json'],
#     result_serializer='json',
#     timezone='UTC',
#     enable_utc=True,
    
#     # Connection pool settings
#     broker_pool_limit=10,
#     broker_connection_retry_on_startup=True,
    
#     # Task execution settings
#     task_acks_late=True,
#     worker_prefetch_multiplier=1,
#     worker_max_tasks_per_child=1000,
    
#     # Result backend settings
#     result_expires=3600,  # 1 hour
#     result_backend_transport_options={
#         'retry_policy': {
#             'timeout': 5.0
#         }
#     },
    
#     # Task routing (if you want to add more task types later)
#     task_routes={
#         'scraper.tasks.scrape_youtube_channel': {'queue': 'scraping'},
#     },
    
#     # Worker settings
#     worker_disable_rate_limits=True,
#     worker_concurrency=4,  # Adjust based on your system
# )

# app.autodiscover_tasks()

# # Performance monitoring task
# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')
