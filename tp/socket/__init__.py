from agbot.core.model.context import VerticalContext
from .tp_socket import SocketTestPoint


def run(tp_conf_dict, vertical_context: VerticalContext):
    return SocketTestPoint(tp_conf_dict, vertical_context)
