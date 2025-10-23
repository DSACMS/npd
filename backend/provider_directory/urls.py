from django.urls import path, include
from . import views
from debug_toolbar.toolbar import debug_toolbar_urls

app_name = "provider_directory"
urlpatterns = [
    path(r"", views.index, name="index"),
    path(r"<path:path>", views.index, name="index_with_path"),
]
