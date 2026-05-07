"""DataUpdateCoordinator for the Zinvolt P1-dongle Pro integration."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_WS_PATH,
    DOMAIN,
    WS_HEARTBEAT,
    WS_RECONNECT_INITIAL,
    WS_RECONNECT_MAX,
)


_LOGGER = logging.getLogger(__name__)
_TIMEOUT = aiohttp.ClientTimeout(total=10)


class ZinvoltP1Coordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that uses WebSocket push updates with HTTP polling as fallback."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        host = entry.data[CONF_HOST]
        self.url = f"http://{host}:{DEFAULT_PORT}"
        self._ws_url = f"ws://{host}:{DEFAULT_PORT}{DEFAULT_WS_PATH}"
        self._session = async_get_clientsession(hass)
        self._ws_connected = False
        self._ws_task: asyncio.Task[None] | None = None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
            config_entry=entry,
        )

    # ── Public API ───────────────────────────────────────────────────────

    def start_ws_listener(self) -> None:
        """Start the WebSocket background task (called after first HTTP refresh)."""
        self._ws_task = self.config_entry.async_create_background_task(
            self.hass,
            self._ws_listen(),
            "zinvolt_p1_ws",
        )

    @property
    def ws_connected(self) -> bool:
        """Return True if the WebSocket connection is active."""
        return self._ws_connected

    @property
    def serial_number(self) -> str | None:
        """Return the serial number of the device."""
        return self.data.get("sn") if self.data else None

    # ── WebSocket listener ───────────────────────────────────────────────

    async def _ws_listen(self) -> None:
        """Maintain a persistent WebSocket connection with exponential back-off.

        On successful connection polling is disabled (update_interval = None).
        On disconnect, polling is re-enabled until the connection is restored.
        If the device does not support WebSocket the task exits quietly and
        the integration continues in polling mode.
        """
        backoff = WS_RECONNECT_INITIAL

        while True:
            try:
                async with self._session.ws_connect(
                    self._ws_url,
                    heartbeat=WS_HEARTBEAT,
                ) as ws:
                    _LOGGER.info("WebSocket connected to %s", self._ws_url)
                    self._ws_connected = True
                    backoff = WS_RECONNECT_INITIAL  # reset on clean connect
                    self.update_interval = None  # disable polling

                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            self._handle_ws_message(msg.data)
                        elif msg.type in (
                            aiohttp.WSMsgType.CLOSED,
                            aiohttp.WSMsgType.ERROR,
                        ):
                            break

            except asyncio.CancelledError:
                # Entry is being unloaded – exit cleanly.
                return

            except aiohttp.WSServerHandshakeError as err:
                # Server actively rejected the upgrade (e.g. 404/400).
                # The device does not support WebSocket – stay in polling mode.
                _LOGGER.info(
                    "Device at %s does not support WebSocket (%s); using polling",
                    self._ws_url,
                    err.status,
                )
                return

            except (aiohttp.ClientError, OSError) as err:
                _LOGGER.debug(
                    "WebSocket connection error (%s); reconnecting in %ds", err, backoff
                )

            finally:
                if self._ws_connected:
                    self._ws_connected = False
                    self.update_interval = DEFAULT_SCAN_INTERVAL
                    _LOGGER.debug("WebSocket disconnected – polling re-enabled")

            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, WS_RECONNECT_MAX)

    def _handle_ws_message(self, raw: str) -> None:
        """Parse a raw WebSocket text message and push it to HA."""
        try:
            data = json.loads(raw)
            parsed = self._parse_data(data)
        except (ValueError, KeyError, TypeError) as err:
            _LOGGER.debug("Could not parse WebSocket message: %s – %s", raw[:120], err)
            return
        self.async_set_updated_data(parsed)

    # ── HTTP fallback ────────────────────────────────────────────────────

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data via HTTP (used during startup and WS fallback)."""
        try:
            async with self._session.get(self.url, timeout=_TIMEOUT) as resp:
                resp.raise_for_status()
                data = await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="communication_error",
                translation_placeholders={"error": str(err)},
            ) from err
        except Exception as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="unexpected_error",
                translation_placeholders={"error": str(err)},
            ) from err

        try:
            return self._parse_data(data)
        except (KeyError, TypeError) as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="invalid_data",
                translation_placeholders={"error": str(err)},
            ) from err

    # ── Shared parser ────────────────────────────────────────────────────

    @staticmethod
    def _parse_data(data: dict[str, Any]) -> dict[str, Any]:
        """Extract a flat dict from the device JSON payload."""
        device_data = data["device"]
        status = device_data["status"]
        return {
            "sn": device_data.get("sn"),
            "type": device_data.get("type"),
            "model": device_data.get("model"),
            **status,
        }

