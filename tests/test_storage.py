"""Tests for Hyperfocus Roulette storage."""

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from custom_components.hyperfocus_roulette.manager import (
    HyperfocusManager,
    TaskAction,
    TaskStatus,
)
from custom_components.hyperfocus_roulette.storage import (
    STORAGE_KEY,
    STORAGE_VERSION,
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

async def test_storage_migrates_legacy_data(
    hass: HomeAssistant,
) -> None:
    """Test migrating data from storage version 1.1."""

    manager = HyperfocusManager()
    legacy_data = manager.to_dict()

    expected_task_ids = {
        task_data["task_id"]
        for task_data in legacy_data["tasks"]
    }

    for task_data in legacy_data["tasks"]:
        del task_data["status"]
        del task_data["omission_count"]

    del legacy_data["current_task_id"]
    del legacy_data["action_history"]

    legacy_store = Store[dict[str, Any]](
        hass,
        STORAGE_VERSION,
        STORAGE_KEY,
        minor_version=1,
    )

    await legacy_store.async_save(legacy_data)

    storage = HyperfocusStorage(hass)
    restored_manager = await storage.async_load()

    assert restored_manager is not None

    restored_task_ids = {
        task.task_id
        for task in restored_manager.tasks
    }

    assert restored_task_ids == expected_task_ids
    assert restored_manager.current_task is None
    assert restored_manager.action_history == []

    for task in restored_manager.tasks:
        assert task.status is TaskStatus.AVAILABLE
        assert task.omission_count == 0