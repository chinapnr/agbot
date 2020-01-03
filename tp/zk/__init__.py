from agbot.core.model.context import VerticalContext
from .tp_zk import ZkTestPoint


def run(tp_conf_dict, vertical_context: VerticalContext):
    return ZkTestPoint(tp_conf_dict, vertical_context)
