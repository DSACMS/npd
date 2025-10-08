from django.urls import path, include
from . import views
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path('', views.landing, name='index'),
    path('search', views.landing, name='search')
]