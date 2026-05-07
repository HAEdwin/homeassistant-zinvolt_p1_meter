"""The Zinvolt P1-dongle Pro integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import ZinvoltP1Coordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Zinvolt P1-dongle Pro from a config entry."""
    coordinator = ZinvoltP1Coordinator(hass, entry)

    # Perform first HTTP fetch to populate data before entities are created.
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Start WebSocket listener *after* entities are registered so that
    # async_set_updated_data() has subscribers to notify immediately.
    coordinator.start_ws_listener()

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Zinvolt P1-dongle Pro config entry."""
    # The WS background task is tied to the config entry via
    # async_create_background_task and is cancelled automatically on unload.
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
