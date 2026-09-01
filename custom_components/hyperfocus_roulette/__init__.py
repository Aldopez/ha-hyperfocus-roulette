"""The Hyperfocus Roulette integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback

from .const import (
    EVENT_TASK_ACTION,
    EVENT_TASK_SELECTED,
    PLATFORMS,
)
from .manager import (
    HyperfocusManager,
    TaskActionResult,
    TaskStatus,
)
from .storage import HyperfocusStorage


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up Hyperfocus Roulette from a config entry."""

    storage = HyperfocusStorage(hass)
    manager = await storage.async_load()

    if manager is None:
         manager = HyperfocusManager()
         await storage.async_save(manager)

    entry.runtime_data = manager

    @callback
    def handle_manager_update() -> None:
        """Fire an event when a task is selected."""

        task = manager.current_task

        if task is None or task.status is not TaskStatus.PROPOSED:
            return

        project = manager.get_project(task.project_id)

        hass.bus.async_fire(
            EVENT_TASK_SELECTED,
            {
                "task_id": task.task_id,
                "project_id": task.project_id,
                "title": task.title,
                "project": project.name,
                "duration": task.duration,
            },
        )

    @callback
    def handle_task_action(result: TaskActionResult) -> None:
        """Fire an event when a task action is recorded."""

        hass.bus.async_fire(
            EVENT_TASK_ACTION,
            {
                "action": result.action.value,
                "task_id": result.task_id,
                "project_id": result.project_id,
                "title": result.title,
                "project": result.project,
                "duration": result.duration,
                "status": result.status.value,
                "omission_count": result.omission_count,
            },
        )

    entry.async_on_unload(
        manager.add_listener(handle_manager_update)
    )
    entry.async_on_unload(
        manager.add_action_listener(handle_task_action)
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload a Hyperfocus Roulette config entry."""

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)