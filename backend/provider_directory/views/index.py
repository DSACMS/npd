import structlog
from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.shortcuts import redirect, render
from pydantic import BaseModel

logger = structlog.get_logger(__name__)


class IndexContext(BaseModel):
    title: str


def index(request, path: str | None = None):
    """
    This is the default route for the Provider Directory single-page
    application.

    When deployed with the frontend assets, all routes not handled by other apps
    will end up here and will be handled by the React application built from the
    npd/frontend/ project.
    """

    context = IndexContext.model_validate({"title": "National Provider Directory"})

    if (settings.DEBUG or settings.TESTING) and not find("index.html"):
        return redirect("http://localhost:3000/")

    # NOTE: (@abachman-dsac) to test this path in development requires that
    # `static/index.html` is present. You can build it locally by running
    # `npm run build` or `npm run watch` in the frontend project.
    return render(request, "index.html", context.model_dump())
