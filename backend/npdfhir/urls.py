from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from rest_framework.renderers import JSONOpenAPIRenderer
from . import views
from debug_toolbar.toolbar import debug_toolbar_urls
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="NPD FHIR API",
        default_version='v1',
        description="The National Provider Directory FHIR API exposes public information on all Providers and Organizations that have registered through the National Provider and Payer Enumeration System NPPES. This is a limited beta release; coverage and data quality will increase iteratively.",
        terms_of_service="TBD",
        contact=openapi.Contact(email="opensource@cms.hhs.gov"),
        license=openapi.License(name="CC0-1.0 License"),
    ),
    public=True,
)

router = DefaultRouter()
router.register(r'Practitioner', views.FHIRPractitionerViewSet,
                basename='fhir-practitioner')
router.register(r'Organization', views.FHIROrganizationViewSet,
                basename='fhir-organization')
router.register(r'Endpoint', views.FHIREndpointViewSet,
                basename='fhir-endpoint')

urlpatterns = [
    path('docs.<format>/',
         schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('docs/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path("healthCheck", views.health, name="healthCheck"),
    path('metadata', views.FHIRCapabilityStatementView.as_view(), name='fhir-metadata'),

    # Router URLs
    path('', include(router.urls), name='index')
] + debug_toolbar_urls()
