from agbot.core.model.context import VerticalContext
from .tp_ui import UiTestPoint


def run(tp_conf_dict, vertical_context: VerticalContext):
    return UiTestPoint(tp_conf_dict, vertical_context)
