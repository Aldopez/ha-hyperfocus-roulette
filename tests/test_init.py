"""Tests for the Hyperfocus Roulette integration setup."""

from homeassistant.core import Event, HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from unittest.mock import patch

from custom_components.hyperfocus_roulette.const import (
    DOMAIN,
    EVENT_TASK_ACTION,
    EVENT_TASK_SELECTED,
)
from custom_components.hyperfocus_roulette.manager import (
    HyperfocusManager,
    TaskAction,
    TaskStatus,
)
from custom_components.hyperfocus_roulette.storage import (
    HyperfocusStorage,
)


async def test_draw_fires_task_selected_event(
    hass: HomeAssistant,
) -> None:
    """Test that drawing a task fires a Home Assistant event."""

    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    received_events: list[Event] = []

    hass.bus.async_listen(
        EVENT_TASK_SELECTED,
        received_events.append,
    )

    manager: HyperfocusManager = entry.runtime_data
    selected_task = manager.draw()
    project = manager.get_project(selected_task.project_id)

    await hass.async_block_till_done()

    assert len(received_events) == 1

    event = received_events[0]

    assert event.event_type == EVENT_TASK_SELECTED
    assert event.data == {
        "task_id": selected_task.task_id,
        "title": selected_task.title,
        "project_id": selected_task.project_id,
        "project": project.name,
        "duration": selected_task.duration,
    }


async def test_accept_fires_task_action_event(
    hass: HomeAssistant,
) -> None:
    """Test that accepting fires a task action event."""

    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    received_events: list[Event] = []

    hass.bus.async_listen(
        EVENT_TASK_ACTION,
        received_events.append,
    )

    manager: HyperfocusManager = entry.runtime_data
    selected_task = manager.draw()
    project = manager.get_project(selected_task.project_id)
    manager.accept()

    await hass.async_block_till_done()

    assert len(received_events) == 1

    event = received_events[0]

    assert event.event_type == EVENT_TASK_ACTION
    assert event.data == {
        "action": TaskAction.ACCEPTED.value,
        "task_id": selected_task.task_id,
        "title": selected_task.title,
        "project_id": selected_task.project_id,
        "project": project.name,
        "duration": selected_task.duration,
        "status": TaskStatus.ACTIVE.value,
        "omission_count": 0,
    }


async def test_setup_restores_saved_manager(
    hass: HomeAssistant,
) -> None:
    """Test that setup restores previously saved manager data."""

    storage = HyperfocusStorage(hass)

    saved_manager = HyperfocusManager()
    selected_task = saved_manager.draw()
    saved_manager.accept()

    await storage.async_save(saved_manager)

    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    restored_manager: HyperfocusManager = entry.runtime_data

    assert restored_manager.current_task is not None
    assert restored_manager.current_task.task_id == selected_task.task_id
    assert restored_manager.current_task.status is TaskStatus.ACTIVE
    assert restored_manager.tasks == saved_manager.tasks
    assert restored_manager.action_history == saved_manager.action_history


async def test_manager_update_schedules_storage_save(
    hass: HomeAssistant,
) -> None:
    """Test that manager updates schedule persistent storage."""

    with patch.object(
        HyperfocusStorage,
        "async_schedule_save",
    ) as schedule_save:
        entry = MockConfigEntry(domain=DOMAIN)
        entry.add_to_hass(hass)

        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        manager: HyperfocusManager = entry.runtime_data
        manager.draw()

        schedule_save.assert_called_once_with(manager)