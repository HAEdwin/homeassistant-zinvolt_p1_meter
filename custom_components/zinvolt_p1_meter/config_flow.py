"""Config flow for Zinvolt P1 Meter integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_HOST, DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)


class ZinvoltP1MeterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zinvolt P1 Meter."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step where the user enters the IP address."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()

            # Check if already configured
            self._async_abort_entries_match({CONF_HOST: host})

            # Test connection
            try:
                session = async_get_clientsession(self.hass)
                url = f"http://{host}:{DEFAULT_PORT}"
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json(content_type=None)

                # Validate response structure
                if "device" not in data or "status" not in data.get("device", {}):
                    errors["base"] = "invalid_response"
                else:
                    serial = data["device"].get("sn", "unknown")
                    await self.async_set_unique_id(serial)
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"Zinvolt P1 Meter ({serial})",
                        data={CONF_HOST: host},
                    )

            except (aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception during config flow")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
