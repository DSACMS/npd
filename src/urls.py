from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("fhir/", include("npdfhir.urls")),
    path("admin/", admin.site.urls),
]
