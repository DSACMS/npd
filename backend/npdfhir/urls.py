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
        default_version="v1",
        description="The National Provider Directory FHIR API exposes public information on all Providers and Organizations that have registered through the National Provider and Payer Enumeration System NPPES. This is a limited beta release; coverage and data quality will increase iteratively.",
        terms_of_service="TBD",
        contact=openapi.Contact(email="opensource@cms.hhs.gov"),
        license=openapi.License(name="CC0-1.0 License"),
    ),
    public=True,
)


urlpatterns = [
    path("docs<format>", schema_view.without_ui(cache_timeout=0),
         name="schema-json"),
    re_path("docs/redoc/?", schema_view.with_ui("redoc",
            cache_timeout=0), name="schema-swagger-ui"),
    re_path("docs/?", schema_view.with_ui("swagger",
            cache_timeout=0), name="schema-swagger-ui"),
    path("healthCheck", views.health, name="healthCheck"),
    # path('metadata', views.fhir_metadata, name='fhir-metadata'),
    # everything else is passed to the rest_framework router to manage
    path("", include(router.urls), name="index"),
] + debug_toolbar_urls()
