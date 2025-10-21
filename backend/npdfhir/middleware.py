from django.http import HttpResponse

class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/fhir/healthCheck':
            return HttpResponse('healthy')
        return self.get_response(request)