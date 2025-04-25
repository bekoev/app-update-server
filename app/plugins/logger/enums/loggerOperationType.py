from enum import Enum


class LoggerOperationType(Enum):
    started = "started"
    finished = "finished"
    change = "change"
    exception = "exception"
    http_exception = "HTTPException"
