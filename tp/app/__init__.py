from agbot.core.model.context import VerticalContext
from .tp_app import AppTestPoint


def run(tp_conf_dict, vertical_context: VerticalContext):
    return AppTestPoint(tp_conf_dict, vertical_context)
