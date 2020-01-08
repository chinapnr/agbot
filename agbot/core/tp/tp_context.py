from datetime import datetime
from typing import Dict, List

from ...constant.ag_enum import TestStatus
from ...tools.ag_error import ErrorInfo


class TpRequest:

    def __init__(self, content):
        self.content = content

    def __str__(self):
        repr_str = ("<TpResponse("
                    "content={content} "
                    ")>".format(
            content=self.content))
        return repr_str


class TpResponse:

    def __init__(self, content, code):
        self.content = content
        self.code = code

    def __str__(self):
        repr_str = ("<TpResponse("
                    "content={content}, "
                    "code={code}, "
                    ")>".format(
            content=self.content,
            code=self.code))
        return repr_str


class TpContext:
    assertion: List[Dict]
    error: ErrorInfo
    response: TpResponse
    request: TpRequest

    def __init__(self,
                 id: str,
                 start_time: datetime
                 ):
        self.id = id
        self.name = None
        self.start_time = start_time
        self.end_time = None
        self.type = None
        self.conf = None
        self.status = TestStatus.INIT
        self.request = None
        self.response = None
        self.replacement = []
        self.error = None
        self.assertion = None

    def __str__(self):
        repr_str = ("<TpContext("
                    "id={id}, "
                    "name={name}, "
                    "start_time={start_time}, "
                    "end_time={end_time}, "
                    "type={type}, "
                    "conf={conf}, "
                    "status={status}, "
                    "request={request}, "
                    "response={response}, "
                    "assertion={assertion} "
                    ")>".format(
            id=self.id,
            name=self.name,
            start_time=self.start_time,
            end_time=self.end_time,
            type=self.type,
            conf=self.conf,
            status=self.status,
            request=self.request,
            response=self.response,
            assertion=self.assertion))
        return repr_str
