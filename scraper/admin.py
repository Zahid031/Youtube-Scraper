from django.contrib import admin
from .models import Channel, Video, ScrapingTask

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['title', 'subscriber_count', 'created_at']
    search_fields = ['title', 'channel_id']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'channel', 'view_count', 'upload_date']
    list_filter = ['channel', 'upload_date']
    search_fields = ['title', 'video_id']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ScrapingTask)
class ScrapingTaskAdmin(admin.ModelAdmin):
    list_display = ['task_id', 'status', 'channel', 'videos_scraped', 'created_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at', 'completed_at']
