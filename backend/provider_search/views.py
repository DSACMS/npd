import logging
from django.conf import settings
from django.shortcuts import render

logger = logging.getLogger(__name__)

def landing(request, path: str | None = None):
    context = {
        "title": "National Provider Directory"
    }

    # NOTE: (@abachman-dsac) you will have to run `npm run build` from the
    # frontend/ directory for this path to work in development.
    return render(request, "index.html", context)
