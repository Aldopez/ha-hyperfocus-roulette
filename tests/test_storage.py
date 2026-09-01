"""Tests for Hyperfocus Roulette storage."""

from homeassistant.core import HomeAssistant

from custom_components.hyperfocus_roulette.manager import (
    HyperfocusManager,
    TaskAction,
    TaskStatus,
)
from custom_components.hyperfocus_roulette.storage import (
    HyperfocusStorage,
)


async def test_manager_can_be_saved_and_loaded(
    hass: HomeAssistant,
) -> None:
    """Test saving and loading manager data."""

    storage = HyperfocusStorage(hass)

    assert await storage.async_load() is None

    manager = HyperfocusManager()
    selected_task = manager.draw()
    manager.accept()

    await storage.async_save(manager)

    restored_manager = await storage.async_load()

    assert restored_manager is not None
    assert restored_manager.projects == manager.projects
    assert restored_manager.tasks == manager.tasks
    assert restored_manager.action_history == manager.action_history

    assert restored_manager.current_task is not None
    assert restored_manager.current_task.task_id == selected_task.task_id
    assert restored_manager.current_task.status is TaskStatus.ACTIVE

    assert restored_manager.last_action is not None
    assert restored_manager.last_action.action is TaskAction.ACCEPTED