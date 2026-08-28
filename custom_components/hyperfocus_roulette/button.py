"""Button platform for Hyperfocus Roulette."""

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .manager import HyperfocusManager, TaskStatus


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Hyperfocus Roulette buttons."""

    async_add_entities(
        [
            HyperfocusDrawButton(entry),
            HyperfocusAcceptButton(entry),
            HyperfocusSkipButton(entry),
            HyperfocusCompleteButton(entry),
        ]
    )


class HyperfocusButton(ButtonEntity):
    """Base class for Hyperfocus Roulette buttons."""

    _attr_has_entity_name = True

    def __init__(
        self,
        entry: ConfigEntry,
        action: str,
    ) -> None:
        """Initialize a Hyperfocus Roulette button."""

        self._manager: HyperfocusManager = entry.runtime_data
        self._attr_unique_id = f"{entry.entry_id}_{action}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Ruleta del Hiperfoco",
            manufacturer="aldopez",
            model="Hyperfocus Roulette",
        )

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


class HyperfocusDrawButton(HyperfocusButton):
    """Button that draws a task."""

    _attr_translation_key = "draw"
    _attr_icon = "mdi:shuffle-variant"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the draw button."""

        super().__init__(entry, "draw")

    @property
    def available(self) -> bool:
        """Return whether drawing is currently allowed."""

        current_task = self._manager.current_task
        has_available_tasks = self._manager.has_available_tasks

        return has_available_tasks and (
            current_task is None
            or current_task.status is TaskStatus.FINISHED
        )

    async def async_press(self) -> None:
        """Draw a new task."""

        self._manager.draw()


class HyperfocusAcceptButton(HyperfocusButton):
    """Button that accepts the proposed task."""

    _attr_translation_key = "accept"
    _attr_icon = "mdi:check"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the accept button."""

        super().__init__(entry, "accept")

    @property
    def available(self) -> bool:
        """Return whether accepting is currently allowed."""

        task = self._manager.current_task

        return (
            task is not None
            and task.status is TaskStatus.PROPOSED
        )

    async def async_press(self) -> None:
        """Accept the proposed task."""

        self._manager.accept()


class HyperfocusSkipButton(HyperfocusButton):
    """Button that skips the proposed task."""

    _attr_translation_key = "skip"
    _attr_icon = "mdi:skip-next"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the skip button."""

        super().__init__(entry, "skip")

    @property
    def available(self) -> bool:
        """Return whether skipping is currently allowed."""

        task = self._manager.current_task

        return (
            task is not None
            and task.status is TaskStatus.PROPOSED
        )

    async def async_press(self) -> None:
        """Skip the proposed task."""

        self._manager.skip()


class HyperfocusCompleteButton(HyperfocusButton):
    """Button that completes the active task."""

    _attr_translation_key = "complete"
    _attr_icon = "mdi:check-circle"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the complete button."""

        super().__init__(entry, "complete")

    @property
    def available(self) -> bool:
        """Return whether completing is currently allowed."""

        task = self._manager.current_task

        return (
            task is not None
            and task.status is TaskStatus.ACTIVE
        )

    async def async_press(self) -> None:
        """Complete the active task."""

        self._manager.complete()