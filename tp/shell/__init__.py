from agbot.core.model.context import VerticalContext
from .tp_shell import ShellTestPoint


def run(tp_conf_dict, vertical_context: VerticalContext):
    return ShellTestPoint(tp_conf_dict, vertical_context)
