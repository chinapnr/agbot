from agbot.core.model.context import VerticalContext
from .tp_log import LogTestPoint


def run(tp_conf_dict, vertical_context: VerticalContext):
    return LogTestPoint(tp_conf_dict, vertical_context)
