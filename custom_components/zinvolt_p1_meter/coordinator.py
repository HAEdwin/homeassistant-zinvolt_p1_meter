"""DataUpdateCoordinator for the Zinvolt P1 Meter integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_HOST, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DOMAIN


_LOGGER = logging.getLogger(__name__)


class ZinvoltP1Coordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to fetch data from the Zinvolt P1 Meter."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.url = f"http://{entry.data[CONF_HOST]}:{DEFAULT_PORT}"
        self._session = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
            config_entry=entry,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the Zinvolt P1 Meter."""
        try:
            async with self._session.get(
                self.url, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                resp.raise_for_status()
                data = await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise UpdateFailed(
                f"Error communicating with Zinvolt P1 Meter: {err}"
            ) from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err

        try:
            device_data = data["device"]
            status = device_data["status"]
        except (KeyError, TypeError) as err:
            raise UpdateFailed(
                f"Invalid data received from Zinvolt P1 Meter: {err}"
            ) from err

        return {
            "sn": device_data.get("sn"),
            "type": device_data.get("type"),
            "model": device_data.get("model"),
            **status,
        }

    @property
    def serial_number(self) -> str | None:
        """Return the serial number of the device."""
        return self.data.get("sn") if self.data else None
