"""Tests for the Hyperfocus Roulette number platform."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.hyperfocus_roulette.const import DOMAIN
from custom_components.hyperfocus_roulette.manager import (
    HyperfocusManager,
)
from custom_components.hyperfocus_roulette.number import (
    HyperfocusAvailableTimeNumber,
)


async def test_available_time_number_updates_manager() -> None:
    """Test changing the available time entity."""

    manager = HyperfocusManager()
    entry = MockConfigEntry(domain=DOMAIN)
    entry.runtime_data = manager

    entity = HyperfocusAvailableTimeNumber(entry)

    assert entity.native_value == 30

    await entity.async_set_native_value(45)

    assert manager.available_time == 45
    assert entity.native_value == 45