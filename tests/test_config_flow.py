"""Tests for the Hyperfocus Roulette options flow."""

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.hyperfocus_roulette.const import DOMAIN
from custom_components.hyperfocus_roulette.manager import (
    HyperfocusManager,
)


async def test_options_flow_can_add_project(
    hass: HomeAssistant,
) -> None:
    """Test creating a project from the options flow."""

    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    manager: HyperfocusManager = entry.runtime_data
    existing_project_ids = set(manager.projects)

    result = await hass.config_entries.options.async_init(
        entry.entry_id
    )

    assert result["type"] is FlowResultType.MENU
    assert result["step_id"] == "init"
    assert result["menu_options"] == [
        "add_project",
        "rename_project",
        "delete_project",
    ]

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"next_step_id": "add_project"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "add_project"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"name": "Acuario plantado"},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY

    new_project_ids = set(manager.projects) - existing_project_ids

    assert len(new_project_ids) == 1

    new_project = manager.projects[new_project_ids.pop()]

    assert new_project.name == "Acuario plantado"


async def test_options_flow_can_rename_project(
    hass: HomeAssistant,
) -> None:
    """Test renaming a project from the options flow."""

    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    manager: HyperfocusManager = entry.runtime_data
    project = next(iter(manager.projects.values()))
    project_id = project.project_id

    result = await hass.config_entries.options.async_init(
        entry.entry_id
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"next_step_id": "rename_project"},
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "project_id": project_id,
            "name": "Proyecto renombrado",
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert manager.projects[project_id].name == "Proyecto renombrado"


async def test_options_flow_can_delete_empty_project(
    hass: HomeAssistant,
) -> None:
    """Test deleting an empty project from the options flow."""

    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    manager: HyperfocusManager = entry.runtime_data
    project = manager.add_project("Proyecto temporal")

    result = await hass.config_entries.options.async_init(
        entry.entry_id
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"next_step_id": "delete_project"},
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "project_id": project.project_id,
            "confirm": True,
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert project.project_id not in manager.projects


async def test_options_flow_rejects_deleting_project_with_tasks(
    hass: HomeAssistant,
) -> None:
    """Test rejecting deletion of a project containing tasks."""

    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    manager: HyperfocusManager = entry.runtime_data
    project_id = manager.tasks[0].project_id

    result = await hass.config_entries.options.async_init(
        entry.entry_id
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"next_step_id": "delete_project"},
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "project_id": project_id,
            "confirm": True,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {
        "base": "project_has_tasks"
    }
    assert project_id in manager.projects