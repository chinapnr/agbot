from datetime import datetime
from typing import Dict, List

from ...constant.ag_enum import TestStatus


class PluginContext:

    start_time: datetime
    replacement: List
    conf: Dict
    status: TestStatus

    def __init__(self,
                 id: str,
                 start_time: datetime
                 ):
        self.id = id
        self.start_time = start_time
        self.status = None
        self.end_time = None
        self.conf = None
        self.replacement = []
