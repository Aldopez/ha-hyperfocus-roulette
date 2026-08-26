"""Tests for the Hyperfocus Roulette manager."""

from custom_components.hyperfocus_roulette.manager import HyperfocusManager


def test_draw_selects_known_task() -> None:
    """Test that drawing selects one of the available tasks."""

    manager = HyperfocusManager()

    selected_task = manager.draw()

    assert selected_task in manager.tasks
    assert manager.current_task is selected_task


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