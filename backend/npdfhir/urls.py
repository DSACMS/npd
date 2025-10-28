from django.urls import path, include, re_path
from rest_framework.schemas import get_schema_view
from debug_toolbar.toolbar import debug_toolbar_urls
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

from . import views
from .router import router

#TODO: fix docs.json
#TODO: fix the forward slash helper

urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'), 
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path("healthCheck", views.health, name="healthCheck"),
    path('metadata', views.FHIRCapabilityStatementView.as_view(),
         name='fhir-metadata'),

    # Router URLs
    # everything else is passed to the rest_framework router to manage
    path("", include(router.urls), name="index"),
] + debug_toolbar_urls()