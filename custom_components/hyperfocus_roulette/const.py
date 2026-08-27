"""Constantes para la integración Hyperfocus Roulette."""

from homeassistant.const import Platform

DOMAIN = "hyperfocus_roulette"
EVENT_TASK_SELECTED = f"{DOMAIN}_task_selected"

PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.SENSOR,
]