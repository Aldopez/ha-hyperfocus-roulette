"""Task manager for Hyperfocus Roulette."""

from collections.abc import Callable
from dataclasses import dataclass
import random


@dataclass(frozen=True, slots=True)
class HyperfocusTask:
    """Represent a task available in the roulette."""

    task_id: str
    project: str
    title: str
    duration: int


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
        """Select a task without immediately repeating the current one."""

        available_tasks = [
            task
            for task in self.tasks
            if task.task_id != getattr(self.current_task, "task_id", None)
        ]

        if not available_tasks:
            available_tasks = self.tasks

        self.current_task = random.choice(available_tasks)
        self._notify_listeners()

        return self.current_task

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