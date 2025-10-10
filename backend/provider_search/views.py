import logging
from django.shortcuts import render

logger = logging.getLogger(__name__)

def landing(request, path: str | None = None):
    logger.info(f'[landing] GET {path}')
    context = {}
    return render(request, "landing.html", context)
