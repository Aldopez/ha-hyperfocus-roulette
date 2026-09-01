"""Config flow for Hyperfocus Roulette."""

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN
from .manager import HyperfocusManager


class HyperfocusRouletteConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hyperfocus Roulette."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> "HyperfocusRouletteOptionsFlow":
        """Return the options flow."""

        return HyperfocusRouletteOptionsFlow(config_entry)

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the initial setup step."""

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(
                title="Ruleta del Hiperfoco",
                data={},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )


class HyperfocusRouletteOptionsFlow(OptionsFlow):
    """Handle Hyperfocus Roulette management options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the options flow."""

        self._config_entry = config_entry

    @property
    def manager(self) -> HyperfocusManager:
        """Return the active manager."""

        return self._config_entry.runtime_data

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Show the management menu."""

        return self.async_show_menu(
            step_id="init",
            menu_options=["add_project"],
        )

    async def async_step_add_project(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Create a project."""

        errors: dict[str, str] = {}

        if user_input is not None:
            name = user_input["name"].strip()

            if name:
                self.manager.add_project(name)

                return self.async_create_entry(
                    title="",
                    data=dict(self._config_entry.options),
                )

            errors["name"] = "empty_name"

        return self.async_show_form(
            step_id="add_project",
            data_schema=vol.Schema(
                {
                    vol.Required("name"): str,
                }
            ),
            errors=errors,
        )