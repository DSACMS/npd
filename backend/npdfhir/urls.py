from django.urls import path, include, re_path
from rest_framework.schemas import get_schema_view
from debug_toolbar.toolbar import debug_toolbar_urls
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path

from . import views
from .router import router

schema_view = get_schema_view(
    openapi.Info(
        title="NPD FHIR API",
        default_version="beta",
        description="Developers can query and retrieve National Provider Directory data via a REST API. The API structure conforms to the HL7 Fast Healthcare Interoperability Resources (FHIR) standard and it returns JSON responses following the FHIR specification.",
        contact=openapi.Contact(email="npd@cms.hhs.gov"),
        license=openapi.License(name="CC0-1.0 License"),
    ),
    public=True,
)


urlpatterns = [
    path("docs<format>", schema_view.without_ui(cache_timeout=0),
         name="schema-json"),
    re_path("docs/redoc/?", schema_view.with_ui("redoc",
            cache_timeout=0), name="schema-redoc-ui"),
    re_path("docs/?", schema_view.with_ui("swagger",
            cache_timeout=0), name="schema-swagger-ui"),
    path("healthCheck", views.health, name="healthCheck"),
    path('metadata', views.FHIRCapabilityStatementView.as_view(),
         name='fhir-metadata'),

    # Router URLs
    # everything else is passed to the rest_framework router to manage
    path("", include(router.urls), name="index"),
] + debug_toolbar_urls()
