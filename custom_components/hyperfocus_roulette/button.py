"""Button platform for Hyperfocus Roulette."""

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .manager import HyperfocusManager


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Hyperfocus Roulette buttons."""

    async_add_entities([HyperfocusDrawButton(entry)])


class HyperfocusDrawButton(ButtonEntity):
    """Button that draws a task."""

    _attr_has_entity_name = True
    _attr_translation_key = "draw"
    _attr_icon = "mdi:shuffle-variant"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the draw button."""

        self._manager: HyperfocusManager = entry.runtime_data
        self._attr_unique_id = f"{entry.entry_id}_draw"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Ruleta del Hiperfoco",
            manufacturer="aldopez",
            model="Hyperfocus Roulette",
        )

    async def async_press(self) -> None:
        """Draw a new task."""

        self._manager.draw()