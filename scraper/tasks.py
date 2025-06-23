from celery import shared_task, group
from celery.utils.log import get_task_logger
import yt_dlp
from django.utils import timezone
from datetime import datetime
import re
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.db import transaction
from .models import Channel, Video, ScrapingTask
from django.utils.timezone import make_aware
from datetime import datetime
from django.utils.timezone import is_naive


# Configure logger
logger = get_task_logger(__name__)

# User agents pool for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
]

def get_ydl_opts(use_proxy=False, proxy_url=None):
    opts = {
        'quiet': True,
        'no_warnings': True,
        'extractaudio': False,
        'extractvideo': False,
        'cookiefile': None,  # You can add cookie file path here
        'user_agent': random.choice(USER_AGENTS),
        'sleep_interval': random.uniform(1, 3),
        'max_sleep_interval': random.uniform(1, 2),
        'sleep_interval_requests': random.uniform(0.5, 1.5),
        'sleep_interval_subtitles': random.uniform(1, 2),
        'retries': 3,
        'fragment_retries': 3,
        'extractor_retries': 3,
        'file_access_retries': 3,
        'http_chunk_size': 10485760,  # 10MB chunks
        'concurrent_fragment_downloads': 4,
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    }
    
    if use_proxy and proxy_url:
        opts['proxy'] = proxy_url
    
    return opts

@shared_task(bind=True, max_retries=3)
def scrape_youtube_channel(self, task_id, channel_url, max_videos=20, use_parallel=True, batch_size=10):
    """
    Optimized YouTube channel scraper with parallel processing
    """
    start_time = time.time()
    logger.info(f"Starting YouTube scraping task {task_id} for channel: {channel_url}")
    
    try:
        task = ScrapingTask.objects.get(task_id=task_id)
        task.status = ScrapingTask.PROCESSING
        task.started_at = timezone.now()
        task.save()
        
        # Phase 1: Extract channel information
        logger.info(f"Task {task_id}: Extracting channel information...")
        channel_start = time.time()
        
        channel = extract_channel_info(task_id, channel_url)
        if not channel:
            raise Exception("Failed to extract channel information")
        
        task.channel = channel
        task.save()
        
        channel_end = time.time()
        logger.info(f"Task {task_id}: Channel info extracted in {channel_end - channel_start:.2f}s")
        
        # Phase 2: Get video list
        logger.info(f"Task {task_id}: Getting video list...")
        video_list_start = time.time()
        
        video_urls = get_channel_video_urls(channel.channel_id, max_videos)
        total_videos = len(video_urls)
        
        video_list_end = time.time()
        logger.info(f"Task {task_id}: Found {total_videos} videos in {video_list_end - video_list_start:.2f}s")
        
        if not video_urls:
            logger.warning(f"Task {task_id}: No videos found for channel")
            task.status = ScrapingTask.COMPLETED
            task.videos_scraped = 0
            task.completed_at = timezone.now()
            task.save()
            return {'status': 'success', 'channel_id': channel.id, 'videos_scraped': 0}
        
        # Phase 3: Scrape videos
        videos_scraped = 0
        if use_parallel:
            videos_scraped = scrape_videos_parallel(task_id, channel, video_urls, batch_size)
        else:
            videos_scraped = scrape_videos_sequential(task_id, channel, video_urls)
        
        # Update task completion
        task.status = ScrapingTask.COMPLETED
        task.videos_scraped = videos_scraped
        task.completed_at = timezone.now()
        task.save()
        
        end_time = time.time()
        total_time = end_time - start_time
        logger.info(f"Task {task_id}: Completed successfully in {total_time:.2f}s. Videos scraped: {videos_scraped}/{total_videos}")
        
        return {
            'status': 'success',
            'channel_id': channel.id,
            'videos_scraped': videos_scraped,
            'total_videos': total_videos,
            'execution_time': total_time
        }
        
    except Exception as e:
        logger.error(f"Task {task_id}: Failed with error: {str(e)}")
        
        try:
            task = ScrapingTask.objects.get(task_id=task_id)
            task.status = ScrapingTask.FAILED
            task.error_message = str(e)
            task.completed_at = timezone.now()
            task.save()
        except:
            pass
        
        # Retry logic
        if self.request.retries < self.max_retries:
            retry_delay = (2 ** self.request.retries) * 60  # Exponential backoff
            logger.info(f"Task {task_id}: Retrying in {retry_delay} seconds...")
            raise self.retry(countdown=retry_delay, exc=e)
        
        return {'status': 'error', 'error': str(e)}

def extract_channel_info(task_id, channel_url):
    """Extract channel information with error handling"""
    try:
        ydl_opts = get_ydl_opts()
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Add random delay to avoid detection
            time.sleep(random.uniform(1, 3))
            
            channel_info = ydl.extract_info(channel_url, download=False, process=False)
            
            # Get channel ID
            if 'channel_id' in channel_info:
                channel_id = channel_info['channel_id']
            else:
                channel_id = extract_channel_id_from_url(channel_url)
            
            # Create or update channel with transaction
            with transaction.atomic():
                channel, created = Channel.objects.get_or_create(
                    channel_id=channel_id,
                    defaults={
                        'channel_url': channel_url,
                        'title': channel_info.get('title', ''),
                        'description': channel_info.get('description', '')[:5000],  # Limit description length
                        'subscriber_count': channel_info.get('channel_follower_count'),
                        'thumbnail_url': get_best_thumbnail(channel_info.get('thumbnails', []))
                    }
                )
                
                # Update existing channel if not created
                if not created:
                    channel.title = channel_info.get('title', channel.title)
                    channel.subscriber_count = channel_info.get('channel_follower_count', channel.subscriber_count)
                    # channel.video_count = channel_info.get('video_count', channel.video_count)
                    # channel.view_count = channel_info.get('view_count', channel.view_count)
                    channel.save()
            
            logger.info(f"Task {task_id}: Channel {'created' if created else 'updated'}: {channel.title}")
            return channel
            
    except Exception as e:
        logger.error(f"Task {task_id}: Error extracting channel info: {str(e)}")
        return None

def get_channel_video_urls(channel_id, max_videos):
    """Get video URLs from channel efficiently"""
    try:
        ydl_opts = get_ydl_opts()
        ydl_opts.update({
            'extract_flat': True,  # Don't extract full video info, just metadata
            'playlistend': max_videos,
        })
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_url = f"https://www.youtube.com/channel/{channel_id}/videos"
            
            # Add random delay
            time.sleep(random.uniform(1, 2))
            
            playlist_info = ydl.extract_info(playlist_url, download=False)
            
            video_urls = []
            if 'entries' in playlist_info:
                for entry in playlist_info['entries'][:max_videos]:
                    if entry and entry.get('id'):
                        video_urls.append(f"https://www.youtube.com/watch?v={entry['id']}")
            
            return video_urls
            
    except Exception as e:
        logger.error(f"Error getting video URLs: {str(e)}")
        return []

def scrape_videos_parallel(task_id, channel, video_urls, batch_size=10):
    """Scrape videos using parallel processing with batching"""
    logger.info(f"Task {task_id}: Starting parallel video scraping with {len(video_urls)} videos, batch size: {batch_size}")
    
    videos_scraped = 0
    total_batches = (len(video_urls) + batch_size - 1) // batch_size
    
    # Process videos in batches to avoid overwhelming the server
    for batch_num, i in enumerate(range(0, len(video_urls), batch_size), 1):
        batch_start = time.time()
        batch_urls = video_urls[i:i + batch_size]
        
        logger.info(f"Task {task_id}: Processing batch {batch_num}/{total_batches} ({len(batch_urls)} videos)")
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=min(5, len(batch_urls))) as executor:
            # Submit all video scraping tasks
            future_to_url = {
                executor.submit(scrape_single_video, task_id, channel, url): url 
                for url in batch_urls
            }
            
            # Process completed tasks
            batch_scraped = 0
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    if result:
                        batch_scraped += 1
                        videos_scraped += 1
                except Exception as e:
                    logger.error(f"Task {task_id}: Error scraping video {url}: {str(e)}")
        
        batch_end = time.time()
        logger.info(f"Task {task_id}: Batch {batch_num} completed in {batch_end - batch_start:.2f}s. Scraped: {batch_scraped}/{len(batch_urls)}")
        
        # Add delay between batches to avoid rate limiting
        if batch_num < total_batches:
            delay = random.uniform(2, 5)
            logger.info(f"Task {task_id}: Waiting {delay:.1f}s before next batch...")
            time.sleep(delay)
    
    return videos_scraped

def scrape_videos_sequential(task_id, channel, video_urls):
    """Scrape videos sequentially (fallback method)"""
    logger.info(f"Task {task_id}: Starting sequential video scraping with {len(video_urls)} videos")
    
    videos_scraped = 0
    for i, url in enumerate(video_urls, 1):
        try:
            if scrape_single_video(task_id, channel, url):
                videos_scraped += 1
            
            if i % 10 == 0:
                logger.info(f"Task {task_id}: Progress: {i}/{len(video_urls)} videos processed")
                
            # Add random delay between requests
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            logger.error(f"Task {task_id}: Error scraping video {url}: {str(e)}")
            continue
    
    return videos_scraped

def scrape_single_video(task_id, channel, video_url):
    try:
        video_id = extract_video_id_from_url(video_url)
        if not video_id:
            return False
        
        # Check if video already exists
        if Video.objects.filter(video_id=video_id).exists():
            return False
        
        ydl_opts = get_ydl_opts()
        ydl_opts.update({
            'writesubtitles': False,
            'writeautomaticsub': False,
            'skip_download': True,
        })
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Add small random delay
            time.sleep(random.uniform(0.5, 1.5))
            
            video_info = ydl.extract_info(video_url, download=False)
            
            if not video_info:
                return False
            
            # Create video with transaction - REMOVED TAGS
            with transaction.atomic():
                video, created = Video.objects.get_or_create(
                    video_id=video_id,
                    defaults={
                        'channel': channel,
                        'title': video_info.get('title', '')[:500],  # Limit title length
                        'description': video_info.get('description', '')[:5000],  # Limit description
                        'duration': str(video_info.get('duration', '')),
                        'view_count': video_info.get('view_count'),
                        'like_count': video_info.get('like_count'),
                        'comment_count': video_info.get('comment_count'),
                        'upload_date': parse_upload_date(video_info.get('upload_date')),
                        'thumbnail_url': get_best_thumbnail(video_info.get('thumbnails', [])),
                        'video_url': video_url,
                        # REMOVED: 'tags': video_info.get('tags', [])[:50]
                    }
                )
            
            return created
            
    except Exception as e:
        logger.error(f"Task {task_id}: Error in scrape_single_video for {video_url}: {str(e)}")
        return False

def extract_video_id_from_url(url):
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def extract_channel_id_from_url(url):
    """Extract channel ID from various YouTube URL formats"""
    patterns = [
        r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
        r'youtube\.com/c/([a-zA-Z0-9_-]+)',
        r'youtube\.com/user/([a-zA-Z0-9_-]+)',
        r'youtube\.com/@([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return url.split('/')[-1]

def get_best_thumbnail(thumbnails):
    """Get the best quality thumbnail URL"""
    if not thumbnails:
        return ''
    
    # Prefer high resolution thumbnails
    sorted_thumbnails = sorted(
        thumbnails, 
        key=lambda x: (x.get('width', 0) * x.get('height', 0)), 
        reverse=True
    )
    
    return sorted_thumbnails[0]['url'] if sorted_thumbnails else ''

def parse_upload_date(date_str):
    """Parse upload date string to datetime"""
    if not date_str:
        return None
    try:
        dt = datetime.strptime(str(date_str), '%Y%m%d')  # Naive
        if is_naive(dt):
            dt = make_aware(dt)  # Convert to timezone-aware
        return dt
    except (ValueError, TypeError):
        return None


# Batch processing task for multiple channels
@shared_task
def scrape_multiple_channels(channel_urls, max_videos_per_channel=20):
    """Scrape multiple channels in parallel"""
    logger.info(f"Starting batch scraping for {len(channel_urls)} channels")
    
    # Create individual tasks for each channel
    job = group(
        scrape_youtube_channel.s(
            f"batch_{i}_{int(time.time())}", 
            url, 
            max_videos_per_channel
        ) for i, url in enumerate(channel_urls)
    )
    
    result = job.apply_async()
    return result.id








