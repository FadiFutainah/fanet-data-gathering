import itertools
import logging
from _typeshed import SupportsNext
from dataclasses import dataclass, field
from typing import Callable, ClassVar

from simpy import Environment

from environment.core.task_status import TaskStatus


@dataclass
class Task:
    created_time: float
    execution_duration: float
    id: int = field(init=False)
    operation: Callable[[], None]
    finished_time: float = field(init=False)
    status: TaskStatus = field(default=TaskStatus.READY)
    object_id: ClassVar[SupportsNext] = itertools.count(1)

    def __post_init__(self):
        self.id = next(self.object_id)

    def execute(self, env: Environment):
        try:
            self.status = TaskStatus.RUNNING
            self.operation()
            yield env.timeout(self.execution_duration)
            self.status = TaskStatus.COMPLETED
            self.finished_time = env.now
        except Exception as e:
            logging.error(e)
            self.status = TaskStatus.FAILED
