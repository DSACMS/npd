from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from rest_framework.renderers import JSONOpenAPIRenderer
from . import views
from debug_toolbar.toolbar import debug_toolbar_urls

router = DefaultRouter()
router.register(r'Practitioner', views.FHIRPractitionerViewSet,
                basename='fhir-practitioner')
router.register(r'Organization', views.FHIROrganizationViewSet,
                basename='fhir-organization')

urlpatterns = [
    path("healthCheck", views.health, name="healthCheck"),
    # path('metadata', views.fhir_metadata, name='fhir-metadata'),

    # Router URLs
    path('', include(router.urls), name='index'),
] + debug_toolbar_urls()
