"""Tests for the Hyperfocus Roulette manager."""

import json

from uuid import UUID

import pytest

from custom_components.hyperfocus_roulette.manager import (
    HyperfocusManager,
    TaskAction,
    TaskStatus,
    ProjectHasTasksError,
    CurrentTaskDeletionError,
)


def test_draw_selects_known_task() -> None:
    """Test that drawing selects one of the available tasks."""

    manager = HyperfocusManager()

    assert manager.has_available_tasks

    selected_task = manager.draw()

    assert selected_task in manager.tasks
    assert selected_task.project_id in manager.projects
    assert manager.current_task is selected_task
    assert selected_task.status is TaskStatus.PROPOSED


def test_draw_does_not_repeat_current_task() -> None:
    """Test that consecutive draws do not repeat a task."""

    manager = HyperfocusManager()

    previous_task = manager.draw()

    for _ in range(20):
        selected_task = manager.draw()

        assert selected_task.task_id != previous_task.task_id

        previous_task = selected_task


def test_draw_notifies_listeners() -> None:
    """Test that drawing notifies registered listeners."""

    manager = HyperfocusManager()
    notifications: list[bool] = []

    manager.add_listener(lambda: notifications.append(True))

    manager.draw()

    assert len(notifications) == 1


def test_listener_can_be_removed() -> None:
    """Test that a listener can unsubscribe from manager updates."""

    manager = HyperfocusManager()
    notifications: list[bool] = []

    remove_listener = manager.add_listener(
        lambda: notifications.append(True)
    )

    manager.draw()
    remove_listener()
    manager.draw()

    assert len(notifications) == 1


def test_accept_activates_current_task() -> None:
    """Test that accepting activates the proposed task."""

    manager = HyperfocusManager()
    proposed_task = manager.draw()

    accepted_task = manager.accept()

    assert accepted_task is proposed_task
    assert accepted_task.status is TaskStatus.ACTIVE
    assert accepted_task.omission_count == 0


def test_skip_records_omission_and_draws_another_task() -> None:
    """Test that skipping records an omission and draws another task."""

    manager = HyperfocusManager()
    skipped_task = manager.draw()

    next_task = manager.skip()

    assert skipped_task.status is TaskStatus.AVAILABLE
    assert skipped_task.omission_count == 1
    assert next_task is manager.current_task
    assert next_task is not skipped_task
    assert next_task.status is TaskStatus.PROPOSED


def test_complete_finishes_active_task() -> None:
    """Test that completing finishes the active task."""

    manager = HyperfocusManager()
    manager.draw()
    active_task = manager.accept()

    completed_task = manager.complete()

    assert completed_task is active_task
    assert completed_task.status is TaskStatus.FINISHED


def test_three_omissions_block_last_available_task() -> None:
    """Test that three omissions block a task without raising an error."""

    manager = HyperfocusManager()
    task = manager.tasks[0]
    manager.tasks = [task]

    for _ in range(2):
        manager.draw()
        next_task = manager.skip()

        assert next_task is task
        assert task.status is TaskStatus.PROPOSED

    result = manager.skip()

    assert result is None
    assert task.status is TaskStatus.BLOCKED
    assert task.omission_count == 3
    assert manager.current_task is None
    assert not manager.has_available_tasks


def test_task_actions_are_recorded() -> None:
    """Test that task actions are recorded in order."""

    manager = HyperfocusManager()

    skipped_task = manager.draw()
    manager.skip()

    active_task = manager.accept()
    manager.complete()

    assert [
        result.action
        for result in manager.action_history
    ] == [
        TaskAction.SKIPPED,
        TaskAction.ACCEPTED,
        TaskAction.COMPLETED,
    ]

    skipped_result = manager.action_history[0]
    accepted_result = manager.action_history[1]
    completed_result = manager.action_history[2]

    assert skipped_result.task_id == skipped_task.task_id
    assert skipped_result.status is TaskStatus.AVAILABLE
    assert skipped_result.omission_count == 1

    assert accepted_result.task_id == active_task.task_id
    assert accepted_result.status is TaskStatus.ACTIVE

    assert completed_result.task_id == active_task.task_id
    assert completed_result.status is TaskStatus.FINISHED
    assert manager.last_action is completed_result
    assert skipped_result.project_id == skipped_task.project_id


def test_manager_data_can_be_serialized_and_restored() -> None:
    """Test that manager data survives a JSON round trip."""

    manager = HyperfocusManager()
    selected_task = manager.draw()
    manager.accept()

    serialized_data = manager.to_dict()

    json_data = json.dumps(serialized_data)
    restored_data = json.loads(json_data)

    restored_manager = HyperfocusManager.from_dict(restored_data)

    assert restored_manager.projects == manager.projects
    assert restored_manager.tasks == manager.tasks
    assert restored_manager.action_history == manager.action_history

    assert restored_manager.current_task is not None
    assert restored_manager.current_task.task_id == selected_task.task_id
    assert restored_manager.current_task.status is TaskStatus.ACTIVE

    assert restored_manager.last_action is not None
    assert restored_manager.last_action.action is TaskAction.ACCEPTED


def test_project_can_be_added() -> None:
    """Test creating a project with a generated UUID."""

    manager = HyperfocusManager()

    project = manager.add_project("Acuario plantado")

    assert project.name == "Acuario plantado"
    assert manager.projects[project.project_id] is project
    assert str(UUID(project.project_id)) == project.project_id


def test_project_can_be_renamed() -> None:
    """Test renaming a project without changing its identifier."""

    manager = HyperfocusManager()
    project = manager.add_project("Nombre anterior")
    project_id = project.project_id

    renamed_project = manager.rename_project(
        project_id,
        "Nombre nuevo",
    )

    assert renamed_project is project
    assert renamed_project.project_id == project_id
    assert renamed_project.name == "Nombre nuevo"


def test_empty_project_can_be_deleted() -> None:
    """Test deleting a project without tasks."""

    manager = HyperfocusManager()
    project = manager.add_project("Proyecto temporal")

    deleted_project = manager.delete_project(project.project_id)

    assert deleted_project is project
    assert project.project_id not in manager.projects


def test_project_with_tasks_cannot_be_deleted() -> None:
    """Test that a project containing tasks cannot be deleted."""

    manager = HyperfocusManager()
    project_id = manager.tasks[0].project_id

    with pytest.raises(ProjectHasTasksError):
        manager.delete_project(project_id)

    assert project_id in manager.projects


def test_task_can_be_added() -> None:
    """Test creating a task with a generated UUID."""

    manager = HyperfocusManager()
    project = next(iter(manager.projects.values()))

    task = manager.add_task(
        project_id=project.project_id,
        title="Comprar MOSFET logic-level",
        duration=20,
    )

    assert task in manager.tasks
    assert task.project_id == project.project_id
    assert task.title == "Comprar MOSFET logic-level"
    assert task.duration == 20
    assert task.status is TaskStatus.AVAILABLE
    assert str(UUID(task.task_id)) == task.task_id


def test_task_can_be_updated() -> None:
    """Test updating a task without resetting its state."""

    manager = HyperfocusManager()
    task = manager.tasks[0]
    destination_project = list(manager.projects.values())[1]

    task.status = TaskStatus.BLOCKED
    task.omission_count = 3
    task_id = task.task_id

    updated_task = manager.update_task(
        task_id=task_id,
        project_id=destination_project.project_id,
        title="Nueva descripción",
        duration=45,
    )

    assert updated_task is task
    assert updated_task.task_id == task_id
    assert updated_task.project_id == destination_project.project_id
    assert updated_task.title == "Nueva descripción"
    assert updated_task.duration == 45
    assert updated_task.status is TaskStatus.BLOCKED
    assert updated_task.omission_count == 3


def test_task_can_be_deleted() -> None:
    """Test deleting a task that is not currently in progress."""

    manager = HyperfocusManager()
    task = manager.tasks[0]

    deleted_task = manager.delete_task(task.task_id)

    assert deleted_task is task
    assert task not in manager.tasks


def test_current_proposed_or_active_task_cannot_be_deleted() -> None:
    """Test protecting the current proposed or active task."""

    proposed_manager = HyperfocusManager()
    proposed_task = proposed_manager.draw()

    with pytest.raises(CurrentTaskDeletionError):
        proposed_manager.delete_task(proposed_task.task_id)

    active_manager = HyperfocusManager()
    active_task = active_manager.draw()
    active_manager.accept()

    with pytest.raises(CurrentTaskDeletionError):
        active_manager.delete_task(active_task.task_id)