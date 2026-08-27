"""The Hyperfocus Roulette integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback

from .const import EVENT_TASK_SELECTED, PLATFORMS
from .manager import HyperfocusManager, TaskStatus


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up Hyperfocus Roulette from a config entry."""

    manager = HyperfocusManager()
    entry.runtime_data = manager

    @callback
    def handle_manager_update() -> None:
        """Fire an event when a task is selected."""

        task = manager.current_task

        if task is None or task.status is not TaskStatus.PROPOSED:
            return

        hass.bus.async_fire(
            EVENT_TASK_SELECTED,
            {
                "task_id": task.task_id,
                "title": task.title,
                "project": task.project,
                "duration": task.duration,
            },
        )

    entry.async_on_unload(
        manager.add_listener(handle_manager_update)
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload a Hyperfocus Roulette config entry."""

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)