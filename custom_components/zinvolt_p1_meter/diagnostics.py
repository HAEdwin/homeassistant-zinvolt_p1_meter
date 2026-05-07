"""Diagnostics support for the Zinvolt P1-dongle Pro integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import ZinvoltP1Coordinator

# Serial number is a unique identifier – redact it from diagnostic dumps.
_TO_REDACT = {"sn", "serial_number"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,  # noqa: ARG001
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: ZinvoltP1Coordinator = entry.runtime_data

    return {
        "config_entry": {
            "domain": entry.domain,
            "version": entry.version,
            "data": async_redact_data(dict(entry.data), _TO_REDACT),
        },
        "coordinator": {
            "ws_connected": coordinator.ws_connected,
            "update_interval": str(coordinator.update_interval),
            "last_update_success": coordinator.last_update_success,
        },
        "data": async_redact_data(coordinator.data or {}, _TO_REDACT),
    }
