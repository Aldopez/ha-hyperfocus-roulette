"""Storage support for Hyperfocus Roulette."""

from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store

from .const import DOMAIN
from .manager import (
    DEFAULT_AVAILABLE_TIME,
    HyperfocusManager
)


STORAGE_VERSION = 1
STORAGE_MINOR_VERSION = 3
STORAGE_KEY = f"{DOMAIN}.data"
STORAGE_SAVE_DELAY = 1.0


class HyperfocusStore(Store[dict[str, Any]]):
    """Store Hyperfocus Roulette data with migration support."""

    async def _async_migrate_func(
        self,
        old_major_version: int,
        old_minor_version: int,
        old_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Migrate stored data to the current version."""

        if old_major_version != STORAGE_VERSION:
            raise NotImplementedError

        if old_minor_version < 2:
            for task_data in old_data.get("tasks", []):
                task_data.setdefault("status", "available")
                task_data.setdefault("omission_count", 0)

            old_data.setdefault("current_task_id", None)
            old_data.setdefault("action_history", [])

        if old_minor_version < 3:
            old_data.setdefault(
                "available_time",
                DEFAULT_AVAILABLE_TIME,
            )

        return old_data


class HyperfocusStorage:
    """Store and restore Hyperfocus Roulette data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize storage."""

        self._store = HyperfocusStore(
            hass,
            STORAGE_VERSION,
            STORAGE_KEY,
            minor_version=STORAGE_MINOR_VERSION,
        )

    async def async_load(self) -> HyperfocusManager | None:
        """Load a manager from storage."""

        data = await self._store.async_load()

        if data is None:
            return None

        return HyperfocusManager.from_dict(data)

    async def async_save(
        self,
        manager: HyperfocusManager,
    ) -> None:
        """Save manager data."""

        await self._store.async_save(manager.to_dict())

    @callback
    def async_schedule_save(
        self,
        manager: HyperfocusManager,
    ) -> None:
        """Schedule manager data to be saved."""

        self._store.async_delay_save(
            manager.to_dict,
            STORAGE_SAVE_DELAY,
        )