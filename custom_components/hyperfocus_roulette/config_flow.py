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
from .manager import (
    CurrentTaskDeletionError,
    HyperfocusManager,
    ProjectHasTasksError,
)

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
        self._selected_task_id: str | None = None

    @property
    def manager(self) -> HyperfocusManager:
        """Return the active manager."""

        return self._config_entry.runtime_data

    def _task_options(self) -> dict[str, str]:
        """Return task identifiers and display names."""

        return {
            task.task_id: (
                f"{self.manager.get_project(task.project_id).name}: "
                f"{task.title}"
            )
            for task in self.manager.tasks
        }

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Show the management menu."""

        return self.async_show_menu(
            step_id="init",
            menu_options=[
                "add_project",
                "rename_project",
                "delete_project",
                "add_task",
                "update_task",
                "delete_task",
            ],
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

    async def async_step_rename_project(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Rename a project."""

        errors: dict[str, str] = {}

        if user_input is not None:
            name = user_input["name"].strip()

            if name:
                self.manager.rename_project(
                    user_input["project_id"],
                    name,
                )

                return self.async_create_entry(
                    title="",
                    data=dict(self._config_entry.options),
                )

            errors["name"] = "empty_name"

        return self.async_show_form(
            step_id="rename_project",
            data_schema=vol.Schema(
                {
                    vol.Required("project_id"): vol.In(
                        {
                            project.project_id: project.name
                            for project in self.manager.projects.values()
                        }
                    ),
                    vol.Required("name"): str,
                }
            ),
            errors=errors,
        )

    async def async_step_delete_project(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Delete an empty project."""

        errors: dict[str, str] = {}

        if user_input is not None:
            if not user_input["confirm"]:
                errors["confirm"] = "confirmation_required"
            else:
                try:
                    self.manager.delete_project(
                        user_input["project_id"]
                    )
                except ProjectHasTasksError:
                    errors["base"] = "project_has_tasks"
                else:
                    return self.async_create_entry(
                        title="",
                        data=dict(self._config_entry.options),
                    )

        return self.async_show_form(
            step_id="delete_project",
            data_schema=vol.Schema(
                {
                    vol.Required("project_id"): vol.In(
                        {
                            project.project_id: project.name
                            for project in self.manager.projects.values()
                        }
                    ),
                    vol.Required("confirm", default=False): bool,
                }
            ),
            errors=errors,
        )

    async def async_step_add_task(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Create a task."""

        errors: dict[str, str] = {}

        if user_input is not None:
            title = user_input["title"].strip()

            if title:
                self.manager.add_task(
                    project_id=user_input["project_id"],
                    title=title,
                    duration=user_input["duration"],
                )

                return self.async_create_entry(
                    title="",
                    data=dict(self._config_entry.options),
                )

            errors["title"] = "empty_title"

        return self.async_show_form(
            step_id="add_task",
            data_schema=vol.Schema(
                {
                    vol.Required("project_id"): vol.In(
                        {
                            project.project_id: project.name
                            for project
                            in self.manager.projects.values()
                        }
                    ),
                    vol.Required("title"): str,
                    vol.Required(
                        "duration",
                        default=30,
                    ): vol.All(
                        int,
                        vol.Range(min=1),
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_update_task(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Select a task to update."""

        if user_input is not None:
            self._selected_task_id = user_input["task_id"]

            return await self.async_step_edit_task()

        return self.async_show_form(
            step_id="update_task",
            data_schema=vol.Schema(
                {
                    vol.Required("task_id"): vol.In(
                        self._task_options()
                    ),
                }
            ),
        )

    async def async_step_edit_task(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Update the selected task."""

        assert self._selected_task_id is not None

        task = self.manager.get_task(self._selected_task_id)
        errors: dict[str, str] = {}

        if user_input is not None:
            title = user_input["title"].strip()

            if title:
                self.manager.update_task(
                    task_id=task.task_id,
                    project_id=user_input["project_id"],
                    title=title,
                    duration=user_input["duration"],
                )

                return self.async_create_entry(
                    title="",
                    data=dict(self._config_entry.options),
                )

            errors["title"] = "empty_title"

        return self.async_show_form(
            step_id="edit_task",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "project_id",
                        default=task.project_id,
                    ): vol.In(
                        {
                            project.project_id: project.name
                            for project
                            in self.manager.projects.values()
                        }
                    ),
                    vol.Required(
                        "title",
                        default=task.title,
                    ): str,
                    vol.Required(
                        "duration",
                        default=task.duration,
                    ): vol.All(
                        int,
                        vol.Range(min=1),
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_delete_task(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Delete a task that is not currently in progress."""

        errors: dict[str, str] = {}

        if user_input is not None:
            if not user_input["confirm"]:
                errors["confirm"] = "confirmation_required"
            else:
                try:
                    self.manager.delete_task(
                        user_input["task_id"]
                    )
                except CurrentTaskDeletionError:
                    errors["base"] = "current_task"
                else:
                    return self.async_create_entry(
                        title="",
                        data=dict(self._config_entry.options),
                    )

        return self.async_show_form(
            step_id="delete_task",
            data_schema=vol.Schema(
                {
                    vol.Required("task_id"): vol.In(
                        self._task_options()
                    ),
                    vol.Required(
                        "confirm",
                        default=False,
                    ): bool,
                }
            ),
            errors=errors,
        )