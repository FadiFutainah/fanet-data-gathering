from enum import Enum


class TaskStatus(Enum):
    READY = 1
    RUNNING = 2
    CANCELED = 3
    FAILED = 4
    COMPLETED = 5
