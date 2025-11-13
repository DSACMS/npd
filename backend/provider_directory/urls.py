from django.urls import path
from django.contrib.auth import views as contrib_auth_views
from provider_directory.views import index, authentication

app_name = "provider_directory"
urlpatterns = [
    # we're only going to provide login / logout functionality, for now
    path("frontend_settings", authentication.frontend_settings, name="authentication_settings"),
    path("accounts/login/", authentication.LoginView.as_view(), name="login"),
    path("accounts/logout/", contrib_auth_views.LogoutView.as_view(), name="logout"),

    path(r"", index.index, name="index"),
    path(r"<path:path>", index.index, name="index_with_path"),
]
