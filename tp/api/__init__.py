from agbot.core.model.context import VerticalContext
from .tp_api import ApiTestPoint


def run(tp_conf_dict, vertical_context: VerticalContext):
    return ApiTestPoint(tp_conf_dict, vertical_context)
