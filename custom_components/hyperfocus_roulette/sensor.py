"""Sensor platform for Hyperfocus Roulette."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Hyperfocus Roulette sensors."""

    async_add_entities([HyperfocusStatusSensor(entry)])


class HyperfocusStatusSensor(SensorEntity):
    """Represent the Hyperfocus Roulette status."""

    _attr_has_entity_name = True
    _attr_name = "Estado"
    _attr_icon = "mdi:slot-machine"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the status sensor."""

        self._attr_unique_id = f"{entry.entry_id}_status"
        self._attr_native_value = "ready"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Ruleta del Hiperfoco",
            manufacturer="aldopez",
            model="Hyperfocus Roulette",
        )