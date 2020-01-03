from agbot.core.model.context import VerticalContext
from .tp_activemq import ActiveMqTestPoint


def run(tp_conf_dict, vertical_context: VerticalContext):
    return ActiveMqTestPoint(tp_conf_dict, vertical_context)
