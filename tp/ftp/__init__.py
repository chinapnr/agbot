from .tp_ftp import FtpTestPoint


def run(tp_conf_dict, vertical_context):
    return FtpTestPoint(tp_conf_dict, vertical_context)
