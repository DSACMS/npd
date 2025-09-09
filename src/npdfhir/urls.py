from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from debug_toolbar.toolbar import debug_toolbar_urls

router = DefaultRouter()
router.register(r'Practitioner', views.FHIRPractitionerViewSet,
                basename='fhir-practitioner')

urlpatterns = [
    path("", views.index, name="index"),
    path("healthCheck", views.health, name="healthCheck"),
    # path('metadata', views.fhir_metadata, name='fhir-metadata'),

    # Router URLs
    path('', include(router.urls)),
] + debug_toolbar_urls()
