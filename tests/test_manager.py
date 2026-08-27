"""Tests for the Hyperfocus Roulette manager."""

from custom_components.hyperfocus_roulette.manager import (
    HyperfocusManager,
    TaskStatus,
)


def test_draw_selects_known_task() -> None:
    """Test that drawing selects one of the available tasks."""

    manager = HyperfocusManager()

    selected_task = manager.draw()

    assert selected_task in manager.tasks
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