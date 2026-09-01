"""Storage support for Hyperfocus Roulette."""

from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store

from .const import DOMAIN
from .manager import HyperfocusManager


STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.data"
STORAGE_SAVE_DELAY = 1.0


class HyperfocusStorage:
    """Store and restore Hyperfocus Roulette data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize storage."""

        self._store: Store[dict[str, Any]] = Store(
            hass,
            STORAGE_VERSION,
            STORAGE_KEY,
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