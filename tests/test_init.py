"""Tests for the Hyperfocus Roulette integration setup."""

from homeassistant.core import Event, HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.hyperfocus_roulette.const import (
    DOMAIN,
    EVENT_TASK_SELECTED,
)
from custom_components.hyperfocus_roulette.manager import HyperfocusManager


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

    await hass.async_block_till_done()

    assert len(received_events) == 1

    event = received_events[0]

    assert event.event_type == EVENT_TASK_SELECTED
    assert event.data == {
        "task_id": selected_task.task_id,
        "title": selected_task.title,
        "project": selected_task.project,
        "duration": selected_task.duration,
    }