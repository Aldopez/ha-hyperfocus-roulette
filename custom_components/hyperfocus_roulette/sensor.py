"""Sensor platform for Hyperfocus Roulette."""

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .manager import HyperfocusManager


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Hyperfocus Roulette sensors."""

    async_add_entities([HyperfocusCurrentTaskSensor(entry)])


class HyperfocusCurrentTaskSensor(SensorEntity):
    """Represent the currently selected task."""

    _attr_has_entity_name = True
    _attr_translation_key = "current_task"
    _attr_icon = "mdi:clipboard-text"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the current task sensor."""

        self._manager: HyperfocusManager = entry.runtime_data
        self._attr_unique_id = f"{entry.entry_id}_current_task"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Ruleta del Hiperfoco",
            manufacturer="aldopez",
            model="Hyperfocus Roulette",
        )

    @property
    def native_value(self) -> str:
        """Return the current task title."""

        if self._manager.current_task is None:
            return "none"

        return self._manager.current_task.title

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return information about the current task."""

        task = self._manager.current_task

        if task is None:
            return {}
        
        return {
            "task_id": task.task_id,
            "project": task.project,
            "duration": task.duration,
            "status": task.status,
            "omission_count": task.omission_count,
        }        

    async def async_added_to_hass(self) -> None:
        """Register for manager updates."""

        await super().async_added_to_hass()

        self.async_on_remove(
            self._manager.add_listener(self._handle_manager_update)
        )

    @callback
    def _handle_manager_update(self) -> None:
        """Write manager changes to Home Assistant."""

        self.async_write_ha_state()