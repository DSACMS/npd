import structlog
from django.conf import settings
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import LoginView as ContribLoginView
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from pydantic import BaseModel

logger = structlog.get_logger(__name__)


class UserData(BaseModel):
    username: str = ""
    is_anonymous: bool = True


class LoginContext(BaseModel):
    user_data: UserData = UserData()


# We override the django.contrib.auth LoginView, but only so we can point it at
# the compiled frontend application
@method_decorator(login_not_required, name="dispatch")
class LoginView(ContribLoginView):
    template_name = "index.html"
    redirect_authenticated_user = True


class FrontendSettingsPayload(BaseModel):
    require_authentication: bool = settings.REQUIRE_AUTHENTICATION
    user: UserData = UserData()

    def populate_user_data(self, request):
        if request.user and not request.user.is_anonymous:
            self.user.username = request.user.username
            self.user.is_anonymous = False


@login_not_required
def frontend_settings(request):
    get_token(request) # always set the CSRF token cookie
    payload = FrontendSettingsPayload()
    payload.populate_user_data(request)
    return JsonResponse(payload.model_dump())
