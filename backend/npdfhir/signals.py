import structlog
from django.dispatch import receiver
from django_structlog import signals
from django_structlog.middlewares.request import get_request_header


@receiver(signals.bind_extra_request_metadata)
def bind_trace_id(request, logger, **kwargs):
    trace_id = get_request_header(request, "x-amzn-trace-id", "HTTP_X_AMZN_TRACE_ID")
    if trace_id:
        structlog.contextvars.bind_contextvars(trace_id=trace_id)
