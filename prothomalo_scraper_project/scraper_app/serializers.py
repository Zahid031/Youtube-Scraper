from rest_framework import serializers

class ArticleSerializer(serializers.Serializer):
    """
    Serializer for article data retrieved from Elasticsearch.
    """
    url = serializers.URLField()
    headline = serializers.CharField()
    author = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    published_at = serializers.DateTimeField(required=False, allow_null=True) # ES might have it as string
    content = serializers.CharField(required=False, allow_blank=True)
    scraped_at = serializers.DateTimeField()
    word_count = serializers.IntegerField(required=False)

    # Note: We don't define create() or update() methods here as this serializer
    # is primarily for read-only representation of data from Elasticsearch.
    # If we were to allow submitting data to create/update ES documents via an API,
    # we might add them.

class ScraperStatusSerializer(serializers.Serializer):
    """
    Serializer for the status of a scraping task.
    """
    task_id = serializers.CharField()
    status = serializers.CharField()
    message = serializers.CharField(allow_blank=True)

class ScraperRunSerializer(serializers.Serializer):
    """
    Serializer for triggering the scraper task.
    Accepts 'max_pages' an an optional parameter.
    """
    max_pages = serializers.IntegerField(required=False, min_value=1, default=None, allow_null=True)
