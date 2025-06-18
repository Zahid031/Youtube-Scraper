from django.db import models
from datetime import timezone


class Channel(models.Model):
    channel_id = models.CharField(max_length=100, unique=True)
    channel_url = models.URLField()
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    subscriber_count = models.BigIntegerField(null=True, blank=True)
    video_count = models.IntegerField(null=True, blank=True)
    view_count = models.BigIntegerField(null=True, blank=True)
    thumbnail_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class Video(models.Model):
    video_id = models.CharField(max_length=100, unique=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    duration = models.CharField(max_length=20, blank=True)
    view_count = models.BigIntegerField(null=True, blank=True)
    like_count = models.BigIntegerField(null=True, blank=True)
    comment_count = models.BigIntegerField(null=True, blank=True)
    upload_date = models.DateTimeField(null=True, blank=True)
    thumbnail_url = models.URLField(blank=True)
    video_url = models.URLField()
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class ScrapingTask(models.Model):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    ]
    
    task_id = models.CharField(max_length=100, unique=True)
    channel_url = models.URLField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, null=True, blank=True)
    error_message = models.TextField(blank=True)
    videos_scraped = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Task {self.task_id} - {self.status}"
