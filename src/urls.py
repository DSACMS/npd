from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("fhir/", include("ndhfhir.urls")),
    path("admin/", admin.site.urls),
]