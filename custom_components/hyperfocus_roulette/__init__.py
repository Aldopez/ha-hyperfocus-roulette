"""The Hyperfocus Roulette integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import PLATFORMS
from .manager import HyperfocusManager

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up Hyperfocus Roulette from a config entry."""

    entry.runtime_data = HyperfocusManager()
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload a Hyperfocus Roulette config entry."""

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)