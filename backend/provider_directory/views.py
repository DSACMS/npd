import logging
from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.core.files.storage import default_storage
from django.shortcuts import redirect, render

logger = logging.getLogger(__name__)

def index(request, path: str | None = None):
    """
    This is the default route for the Provider Directory single-page
    application.

    When deployed with the frontend assets, all routes not handled by other apps
    will end up here and will be handled by the React application built from the
    npd/frontend/ project.
    """
    context = {
        "title": "National Provider Directory"
    }

    if (settings.DEBUG or settings.TESTING) and not find('index.html'):
        return redirect('http://localhost:3000/')

    # NOTE: (@abachman-dsac) to test this path in development requires that
    # `static/index.html` is present. You can build it locally by running
    # `npm run build` or `npm run watch` in the frontend project.
    return render(request, "index.html", context)
