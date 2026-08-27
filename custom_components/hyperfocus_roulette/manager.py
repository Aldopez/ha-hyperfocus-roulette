"""Task manager for Hyperfocus Roulette."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
import random


MAX_OMISSIONS = 3


class TaskStatus(StrEnum):
    """Possible states in the lifecycle of a task."""

    AVAILABLE = "available"
    PROPOSED = "proposed"
    ACTIVE = "active"
    BLOCKED = "blocked"
    FINISHED = "finished"


class NoAvailableTasksError(Exception):
    """Raised when the roulette has no available tasks."""

class InvalidTaskTransitionError(Exception):
    """Raised when an action is invalid for the current task state."""

@dataclass(slots=True)
class HyperfocusTask:
    """Represent a task available in the roulette."""

    task_id: str
    project: str
    title: str
    duration: int
    status: TaskStatus = TaskStatus.AVAILABLE
    omission_count: int = 0


class HyperfocusManager:
    """Manage tasks and the current roulette selection."""

    def __init__(self) -> None:
        """Initialize the manager."""

        self.tasks: list[HyperfocusTask] = [
            HyperfocusTask(
                task_id="pc_power_transistor",
                project="ESPHome PC Power Control",
                title="Dibujar la etapa BC548–PWR_SW",
                duration=20,
            ),
            HyperfocusTask(
                task_id="geeetech_pi_case",
                project="Geeetech A10",
                title="Montar la carcasa de la Raspberry Pi",
                duration=30,
            ),
            HyperfocusTask(
                task_id="nioh_yokai_cores",
                project="Nioh 2",
                title="Jugar una misión usando conscientemente tres núcleos yokai",
                duration=30,
            ),
        ]

        self.current_task: HyperfocusTask | None = None
        self._listeners: set[Callable[[], None]] = set()

    def draw(self) -> HyperfocusTask:
        """Select an available task without immediately repeating one."""

        previous_task = self.current_task

        if (
            previous_task is not None
            and previous_task.status is TaskStatus.PROPOSED
        ):
            previous_task.status = TaskStatus.AVAILABLE

        available_tasks = [
            task
            for task in self.tasks
            if task.status is TaskStatus.AVAILABLE
            and task.task_id != getattr(previous_task, "task_id", None)
        ]

        if not available_tasks:
            available_tasks = [
                task
                for task in self.tasks
                if task.status is TaskStatus.AVAILABLE
            ]

        if not available_tasks:
            self.current_task = None
            self._notify_listeners()
            raise NoAvailableTasksError

        self.current_task = random.choice(available_tasks)
        self.current_task.status = TaskStatus.PROPOSED

        self._notify_listeners()

        return self.current_task

    def accept(self) -> HyperfocusTask:
        """Accept the currently proposed task."""

        task = self._require_current_task(TaskStatus.PROPOSED)

        task.status = TaskStatus.ACTIVE
        task.omission_count = 0

        self._notify_listeners()

        return task

    def skip(self) -> HyperfocusTask | None:
        """Skip the current proposal and draw another task."""

        skipped_task = self._require_current_task(TaskStatus.PROPOSED)

        skipped_task.omission_count += 1

        if skipped_task.omission_count >= MAX_OMISSIONS:
            skipped_task.status = TaskStatus.BLOCKED
        else:
            skipped_task.status = TaskStatus.AVAILABLE

        try:
            return self.draw()
        except NoAvailableTasksError:
            return None

    def complete(self) -> HyperfocusTask:
        """Complete the currently active task."""

        task = self._require_current_task(TaskStatus.ACTIVE)

        task.status = TaskStatus.FINISHED

        self._notify_listeners()

        return task

    def _require_current_task(
        self,
        required_status: TaskStatus,
    ) -> HyperfocusTask:
        """Return the current task if it has the required status."""

        task = self.current_task

        if task is None or task.status is not required_status:
            raise InvalidTaskTransitionError

        return task

    def add_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Register a listener and return its unsubscribe callback."""

        self._listeners.add(listener)

        def remove_listener() -> None:
            self._listeners.discard(listener)

        return remove_listener

    def _notify_listeners(self) -> None:
        """Notify listeners that the state changed."""

        for listener in self._listeners:
            listener()