from django.http import JsonResponse
from django.db import connection
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/fhir/healthCheck':
            utc_now = datetime.now(timezone.utc).isoformat()

            health_status = {
                'status': 'healthy',
                'database': 'connected',
                'timestamp': utc_now
            }

            try:
                # Test database connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()

                return JsonResponse(health_status, status=200)

            except Exception as e:
                logger.error(f"Database health check failed: {str(e)}")
                health_status.update({
                    'status': 'unhealthy',
                    'database': 'disconnected',
                })
                return JsonResponse(health_status, status=502)

        return self.get_response(request)