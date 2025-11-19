from django.conf import settings
from django.contrib.auth.decorators import login_not_required
from django.http import JsonResponse
from django.middleware.csrf import get_token
from flags.state import flag_enabled
from pydantic import BaseModel

from .authentication import UserData

API_FLAGS = settings.FLAGS.keys()


class FrontendSettingsPayload(BaseModel):
    require_authentication: bool = settings.REQUIRE_AUTHENTICATION
    user: UserData = UserData()
    feature_flags: dict = {}

    def populate_user_data(self, request):
        if request.user and not request.user.is_anonymous:
            self.user.username = request.user.username
            self.user.is_anonymous = False

    def populate_feature_flags(self, request):
        self.feature_flags = {
            flag_name: flag_enabled(flag_name, request=request) for flag_name in API_FLAGS
        }


@login_not_required
def frontend_settings(request):
    get_token(request)  # always set the CSRF token cookie
    payload = FrontendSettingsPayload()
    payload.populate_user_data(request)
    payload.populate_feature_flags(request)
    return JsonResponse(payload.model_dump())
