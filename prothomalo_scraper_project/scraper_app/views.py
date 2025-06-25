from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from elasticsearch import Elasticsearch, exceptions as es_exceptions
from celery.result import AsyncResult

from .tasks import run_prothomalo_scraper_task
from .serializers import ArticleSerializer, ScraperStatusSerializer, ScraperRunSerializer
from .scraper import Config as ScraperConfig # To get ES connection details

# Standard Django logging
import logging
logger = logging.getLogger(__name__)

class StartScrapingView(APIView):
    """
    API view to trigger the Prothom Alo scraping task.
    Accepts an optional 'max_pages' parameter.
    """
    def post(self, request, *args, **kwargs):
        serializer = ScraperRunSerializer(data=request.data)
        if serializer.is_valid():
            max_pages = serializer.validated_data.get('max_pages')
            try:
                # Use .delay() to send the task to Celery
                task = run_prothomalo_scraper_task.delay(max_pages=max_pages)
                status_serializer = ScraperStatusSerializer({
                    'task_id': task.id,
                    'status': task.status,
                    'message': 'Scraping task initiated.'
                })
                return Response(status_serializer.data, status=status.HTTP_202_ACCEPTED)
            except Exception as e:
                logger.error(f"Failed to initiate scraping task: {e}", exc_info=True)
                return Response(
                    {"error": "Failed to initiate scraping task.", "details": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ScrapingTaskStatusView(APIView):
    """
    API view to check the status of a Celery scraping task.
    """
    def get(self, request, task_id, *args, **kwargs):
        try:
            task_result = AsyncResult(task_id)
            response_data = {
                'task_id': task_id,
                'status': task_result.status,
                'result': task_result.result if task_result.successful() else None,
                'error': str(task_result.result) if task_result.failed() else None,
                'traceback': task_result.traceback if task_result.failed() else None
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving task status for {task_id}: {e}", exc_info=True)
            return Response(
                {"error": "Failed to retrieve task status.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ArticleSearchView(APIView):
    """
    API view to search for articles in Elasticsearch.
    Supports a 'q' query parameter for full-text search and 'size'/'from' for pagination.
    """
    def get(self, request, *args, **kwargs):
        query_param = request.query_params.get('q', None)
        size = int(request.query_params.get('size', 10))
        from_offset = int(request.query_params.get('from', 0))

        es_config = ScraperConfig() # Get ES connection details from scraper config

        try:
            # It's better to get ES client from a central place if possible,
            # e.g., from Django settings or a utility function.
            # For now, creating a new client based on config.
            from django.conf import settings as django_settings
            es_client = Elasticsearch(
                hosts=[es_config.ES_HOST],
                basic_auth=(es_config.ES_USER, es_config.ES_PASSWORD),
                verify_certs=getattr(django_settings, 'ES_VERIFY_CERTS', False)
            )

            if not es_client.ping():
                logger.error("Elasticsearch connection failed for search.")
                return Response({"error": "Elasticsearch connection failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            if query_param:
                # More sophisticated query using query_string for flexibility
                search_body = {
                    "query": {
                        "query_string": {
                            "query": query_param,
                            "fields": ["headline", "content", "author", "location"],
                            "default_operator": "AND"
                        }
                    },
                    "from": from_offset,
                    "size": size,
                    "_source": True # Ensure we get the source documents
                }
            else:
                # Match all if no query parameter
                search_body = {
                    "query": {"match_all": {}},
                    "from": from_offset,
                    "size": size,
                    "_source": True
                }

            logger.info(f"Elasticsearch query: {search_body}")

            response = es_client.search(
                index=es_config.ES_INDEX,
                body=search_body
            )

            hits = response.get('hits', {}).get('hits', [])
            articles = [hit['_source'] for hit in hits]

            serializer = ArticleSerializer(articles, many=True)

            return Response({
                "total_hits": response.get('hits', {}).get('total', {}).get('value', 0),
                "articles": serializer.data
            }, status=status.HTTP_200_OK)

        except es_exceptions.NotFoundError:
            logger.warning(f"Search index {es_config.ES_INDEX} not found.")
            return Response({"error": f"Search index '{es_config.ES_INDEX}' not found."}, status=status.HTTP_404_NOT_FOUND)
        except es_exceptions.ConnectionError:
            logger.error("Could not connect to Elasticsearch for search.")
            return Response({"error": "Could not connect to Elasticsearch."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            logger.error(f"Error during article search: {e}", exc_info=True)
            return Response(
                {"error": "An error occurred during search.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
