from rest_framework import serializers
from .models import Channel, Video, ScrapingTask

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class ChannelSerializer(serializers.ModelSerializer):
    videos_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Channel
        fields = '__all__'
    
    def get_videos_count(self, obj):
        return obj.videos.count()

class ChannelDetailSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, read_only=True)
    videos_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Channel
        fields = '__all__'
    
    def get_videos_count(self, obj):
        return obj.videos.count()

class ScrapingTaskSerializer(serializers.ModelSerializer):
    channel = ChannelSerializer(read_only=True)
    
    class Meta:
        model = ScrapingTask
        fields = '__all__'

class ScrapeChannelRequestSerializer(serializers.Serializer):
    channel_url = serializers.URLField()
    max_videos = serializers.IntegerField(default=50, min_value=1, max_value=500)