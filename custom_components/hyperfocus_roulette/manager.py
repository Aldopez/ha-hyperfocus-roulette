"""Task manager for Hyperfocus Roulette."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
import random
from typing import Any
from uuid import uuid4


MAX_OMISSIONS = 3


class TaskStatus(StrEnum):
    """Possible states in the lifecycle of a task."""

    AVAILABLE = "available"
    PROPOSED = "proposed"
    ACTIVE = "active"
    BLOCKED = "blocked"
    FINISHED = "finished"


class TaskAction(StrEnum):
    """Actions that can be performed on a task."""

    ACCEPTED = "accepted"
    SKIPPED = "skipped"
    COMPLETED = "completed"


class NoAvailableTasksError(Exception):
    """Raised when the roulette has no available tasks."""


class InvalidTaskTransitionError(Exception):
    """Raised when an action is invalid for the current task state."""


class ProjectNotFoundError(Exception):
    """Raised when a project does not exist."""


class ProjectHasTasksError(Exception):
    """Raised when deleting a project that still has tasks."""


@dataclass(slots=True)
class HyperfocusProject:
    """Represent a project containing roulette tasks."""

    project_id: str
    name: str


@dataclass(slots=True)
class HyperfocusTask:
    """Represent a task available in the roulette."""

    task_id: str
    project_id: str
    title: str
    duration: int
    status: TaskStatus = TaskStatus.AVAILABLE
    omission_count: int = 0


@dataclass(frozen=True, slots=True)
class TaskActionResult:
    """Represent the recorded result of a task action."""

    action: TaskAction
    task_id: str
    project_id: str
    project: str
    title: str
    duration: int
    status: TaskStatus
    omission_count: int


class HyperfocusManager:
    """Manage tasks and the current roulette selection."""

    def __init__(self) -> None:
        """Initialize the manager."""

        pc_power_project = HyperfocusProject(
            project_id="3f2cb6e8-4b2f-4f18-9e2d-7a9d63f94b01",
            name="ESPHome PC Power Control",
        )
        geeetech_project = HyperfocusProject(
            project_id="a718d4e2-78c0-4ff1-8a4a-24c2d90f2b11",
            name="Geeetech A10",
        )
        nioh_project = HyperfocusProject(
            project_id="c8d84fd0-b7ec-4cab-a1a1-dc85ad7c0312",
            name="Nioh 2",
        )

        self.projects: dict[str, HyperfocusProject] = {
            project.project_id: project
            for project in (
                pc_power_project,
                geeetech_project,
                nioh_project,
            )
        }

        self.tasks: list[HyperfocusTask] = [
            HyperfocusTask(
                task_id="51eb6b3a-2d86-42bd-8b48-9a5ee2d9a101",
                project_id=pc_power_project.project_id,
                title="Dibujar la etapa BC548–PWR_SW",
                duration=20,
            ),
            HyperfocusTask(
                task_id="2fd7a4bc-8f31-48e6-9f1b-702ca6a4b202",
                project_id=geeetech_project.project_id,
                title="Montar la carcasa de la Raspberry Pi",
                duration=30,
            ),
            HyperfocusTask(
                task_id="9a3cda10-63e2-4fb7-a827-1e15c985c303",
                project_id=nioh_project.project_id,
                title=(
                    "Jugar una misión usando conscientemente "
                    "tres núcleos yokai"
                ),
                duration=30,
            ),
        ]

        self.current_task: HyperfocusTask | None = None
        self.action_history: list[TaskActionResult] = []
        self._action_listeners: set[
            Callable[[TaskActionResult], None]
        ] = set()
        self._listeners: set[Callable[[], None]] = set()

    @property
    def has_available_tasks(self) -> bool:
        """Return whether at least one task is available."""

        return any(
            task.status is TaskStatus.AVAILABLE
            for task in self.tasks
        )

    @property
    def last_action(self) -> TaskActionResult | None:
        """Return the most recently recorded action."""

        if not self.action_history:
            return None

        return self.action_history[-1]

    def get_project(self, project_id: str,) -> HyperfocusProject:
        """Return a project by its identifier."""

        try:
            return self.projects[project_id]
        except KeyError as error:
            raise ProjectNotFoundError from error

    def add_project(self, name: str) -> HyperfocusProject:
        """Create a project."""

        project = HyperfocusProject(
            project_id=str(uuid4()),
            name=name,
        )

        self.projects[project.project_id] = project
        self._notify_listeners()

        return project

    def rename_project(
        self,
        project_id: str,
        name: str,
    ) -> HyperfocusProject:
        """Rename an existing project."""

        project = self.get_project(project_id)
        project.name = name

        self._notify_listeners()

        return project

    def delete_project(
        self,
        project_id: str,
    ) -> HyperfocusProject:
        """Delete an empty project."""

        project = self.get_project(project_id)

        if any(
            task.project_id == project_id
            for task in self.tasks
        ):
            raise ProjectHasTasksError

        del self.projects[project_id]
        self._notify_listeners()

        return project

    def to_dict(self) -> dict[str, Any]:
        """Return all manager data in a JSON-compatible structure."""

        return {
            "projects": [
                {
                    "project_id": project.project_id,
                    "name": project.name,
                }
                for project in self.projects.values()
            ],
            "tasks": [
                {
                    "task_id": task.task_id,
                    "project_id": task.project_id,
                    "title": task.title,
                    "duration": task.duration,
                    "status": task.status.value,
                    "omission_count": task.omission_count,
                }
                for task in self.tasks
            ],
            "current_task_id": (
                self.current_task.task_id
                if self.current_task is not None
                else None
            ),
            "action_history": [
                {
                    "action": result.action.value,
                    "task_id": result.task_id,
                    "project_id": result.project_id,
                    "project": result.project,
                    "title": result.title,
                    "duration": result.duration,
                    "status": result.status.value,
                    "omission_count": result.omission_count,
                }
                for result in self.action_history
            ],
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "HyperfocusManager":
        """Create a manager from previously serialized data."""

        manager = cls()

        manager.projects = {
            project_data["project_id"]: HyperfocusProject(
                project_id=project_data["project_id"],
                name=project_data["name"],
            )
            for project_data in data["projects"]
        }

        manager.tasks = [
            HyperfocusTask(
                task_id=task_data["task_id"],
                project_id=task_data["project_id"],
                title=task_data["title"],
                duration=task_data["duration"],
                status=TaskStatus(task_data["status"]),
                omission_count=task_data["omission_count"],
            )
            for task_data in data["tasks"]
        ]

        manager.action_history = [
            TaskActionResult(
                action=TaskAction(result_data["action"]),
                task_id=result_data["task_id"],
                project_id=result_data["project_id"],
                project=result_data["project"],
                title=result_data["title"],
                duration=result_data["duration"],
                status=TaskStatus(result_data["status"]),
                omission_count=result_data["omission_count"],
            )
            for result_data in data["action_history"]
        ]

        current_task_id = data["current_task_id"]

        manager.current_task = next(
            (
                task
                for task in manager.tasks
                if task.task_id == current_task_id
            ),
            None,
        )

        return manager

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

        self._record_action(TaskAction.ACCEPTED, task)
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

        self._record_action(TaskAction.SKIPPED, skipped_task)

        try:
            return self.draw()
        except NoAvailableTasksError:
            return None

    def complete(self) -> HyperfocusTask:
        """Complete the currently active task."""

        task = self._require_current_task(TaskStatus.ACTIVE)

        task.status = TaskStatus.FINISHED

        self._record_action(TaskAction.COMPLETED, task)
        self._notify_listeners()

        return task

    def _record_action(self, action: TaskAction, task: HyperfocusTask,) -> TaskActionResult:
        """Record and return the result of a task action."""
        
        project = self.get_project(task.project_id)
        
        result = TaskActionResult(
            action=action,
            task_id=task.task_id,
            project_id=task.project_id,
            project=project.name,
            title=task.title,
            duration=task.duration,
            status=task.status,
            omission_count=task.omission_count,
        )

        self.action_history.append(result)
        self._notify_action_listeners(result)

        return result

    def _require_current_task(
        self,
        required_status: TaskStatus,
    ) -> HyperfocusTask:
        """Return the current task if it has the required status."""

        task = self.current_task

        if task is None or task.status is not required_status:
            raise InvalidTaskTransitionError

        return task

    def add_action_listener(
        self,
        listener: Callable[[TaskActionResult], None],
    ) -> Callable[[], None]:
        """Register a listener for recorded task actions."""

        self._action_listeners.add(listener)

        def remove_listener() -> None:
            self._action_listeners.discard(listener)

        return remove_listener

    def add_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Register a listener and return its unsubscribe callback."""

        self._listeners.add(listener)

        def remove_listener() -> None:
            self._listeners.discard(listener)

        return remove_listener

    def _notify_action_listeners(
        self,
        result: TaskActionResult,
    ) -> None:
        """Notify listeners that a task action was recorded."""

        for listener in self._action_listeners:
            listener(result)

    def _notify_listeners(self) -> None:
        """Notify listeners that the state changed."""

        for listener in self._listeners:
            listener()