from flags.conditions import register
from structlog import get_logger

logger = get_logger(__name__)


@register("in_group")
def in_group_condition(value: str | list[str], request, **kwargs):
    """
    Checks if the current user is in any of the specified groups.
    """

    logger.debug("in_group_condition", value=value)
    if not request.user.is_authenticated:
        return False

    if isinstance(value, str):
        group_names = [value]
    elif isinstance(value, (list, tuple)):
        group_names = value
    else:
        return False

    user_groups = request.user.groups.values_list("name", flat=True)
    return any(group_name in user_groups for group_name in group_names)
