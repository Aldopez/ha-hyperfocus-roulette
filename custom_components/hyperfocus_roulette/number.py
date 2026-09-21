"""Number platform for Hyperfocus Roulette."""

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
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
    """Set up Hyperfocus Roulette numbers."""

    async_add_entities([HyperfocusAvailableTimeNumber(entry)])


class HyperfocusAvailableTimeNumber(NumberEntity):
    """Represent the available time context."""

    _attr_has_entity_name = True
    _attr_translation_key = "available_time"
    _attr_icon = "mdi:timer-outline"
    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 5
    _attr_native_max_value = 180
    _attr_native_step = 5
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the available time number."""

        self._manager: HyperfocusManager = entry.runtime_data
        self._attr_unique_id = f"{entry.entry_id}_available_time"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Ruleta del Hiperfoco",
            manufacturer="aldopez",
            model="Hyperfocus Roulette",
        )

    @property
    def native_value(self) -> float:
        """Return the available time."""

        return float(self._manager.available_time)

    async def async_set_native_value(self, value: float) -> None:
        """Set the available time."""

        self._manager.set_available_time(int(value))

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