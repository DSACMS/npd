import structlog
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import LoginView as ContribLoginView
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
