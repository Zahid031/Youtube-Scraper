from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import uuid
from .models import Channel, Video, ScrapingTask
from .serializers import (
    ChannelSerializer, 
    ChannelDetailSerializer, 
    VideoSerializer, 
    ScrapingTaskSerializer,
    ScrapeChannelRequestSerializer      
)
from .tasks import scrape_youtube_channel

class ChannelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChannelDetailSerializer
        return ChannelSerializer
    
    @action(detail=True, methods=['get'])
    def videos(self, request, pk=None):
        """Get all videos for a specific channel"""
        channel = self.get_object()
        videos = Video.objects.filter(channel=channel).order_by('-upload_date')
        
        page = self.paginate_queryset(videos)
        if page is not None:
            serializer = VideoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)

class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Video.objects.all().order_by('-upload_date')
    serializer_class = VideoSerializer

class ScrapingTaskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ScrapingTask.objects.all().order_by('-created_at')
    serializer_class = ScrapingTaskSerializer
    
    @action(detail=False, methods=['post'])
    def scrape_channel(self, request):
        """Start scraping a YouTube channel"""
        serializer = ScrapeChannelRequestSerializer(data=request.data)
        if serializer.is_valid():
            channel_url = serializer.validated_data['channel_url']
            max_videos = serializer.validated_data['max_videos']
            
            # Create task record
            task_id = str(uuid.uuid4())
            task = ScrapingTask.objects.create(
                task_id=task_id,
                channel_url=channel_url
            )
            
            # Start async task
            scrape_youtube_channel.delay(task_id, channel_url, max_videos)
            
            return Response({
                'task_id': task_id,
                'status': 'started',
                'message': 'Channel scraping started'
            }, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get status of a scraping task"""
        task = get_object_or_404(ScrapingTask, task_id=pk)
        serializer = self.get_serializer(task)
        return Response(serializer.data)


# from rest_framework import viewsets, status
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from django.shortcuts import get_object_or_404
# import uuid
# from .models import Channel, Video, ScrapingTask
# from .serializers import (
#     ChannelSerializer, 
#     ChannelDetailSerializer, 
#     VideoSerializer, 
#     ScrapingTaskSerializer,
#     ScrapeChannelRequestSerializer
# )
# from .tasks import scrape_youtube_channel

# class ChannelViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = Channel.objects.all()
#     serializer_class = ChannelSerializer
    
#     def get_serializer_class(self):
#         if self.action == 'retrieve':
#             return ChannelDetailSerializer
#         return ChannelSerializer
    
#     @action(detail=True, methods=['get'])
#     def videos(self, request, pk=None):
#         """Get all videos for a specific channel"""
#         channel = self.get_object()
#         videos = Video.objects.filter(channel=channel).order_by('-upload_date')
        
#         page = self.paginate_queryset(videos)
#         if page is not None:
#             serializer = VideoSerializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
        
#         serializer = VideoSerializer(videos, many=True)
#         return Response(serializer.data)

# class VideoViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = Video.objects.all().order_by('-upload_date')
#     serializer_class = VideoSerializer

# class ScrapingTaskViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = ScrapingTask.objects.all().order_by('-created_at')
#     serializer_class = ScrapingTaskSerializer
    
#     @action(detail=False, methods=['post'])
#     def scrape_channel(self, request):
#         """Start scraping a YouTube channel"""
#         serializer = ScrapeChannelRequestSerializer(data=request.data)
#         if serializer.is_valid():
#             channel_url = serializer.validated_data['channel_url']
#             max_videos = serializer.validated_data['max_videos']
            
#             # Create task record
#             task_id = str(uuid.uuid4())
#             task = ScrapingTask.objects.create(
#                 task_id=task_id,
#                 channel_url=channel_url
#             )
            
#             # Start async task
#             scrape_youtube_channel.delay(task_id, channel_url, max_videos)
            
#             return Response({
#                 'task_id': task_id,
#                 'status': 'started',
#                 'message': 'Channel scraping started'
#             }, status=status.HTTP_202_ACCEPTED)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     @action(detail=True, methods=['get'])
#     def status(self, request, pk=None):
#         """Get status of a scraping task"""
#         task = get_object_or_404(ScrapingTask, task_id=pk)
#         serializer = self.get_serializer(task)
#         return Response(serializer.data)