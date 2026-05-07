"""Config flow for Zinvolt P1-dongle Pro integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)
_TIMEOUT = aiohttp.ClientTimeout(total=10)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)


class ZinvoltP1DongleProConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zinvolt P1-dongle Pro."""

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
                async with session.get(url, timeout=_TIMEOUT) as resp:
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
                        title=f"Zinvolt P1-dongle Pro ({serial})",
                        data={CONF_HOST: host},
                    )

            except (aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            except ValueError:
                errors["base"] = "invalid_response"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception during config flow")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Allow the user to update the IP address without re-adding the entry."""
        errors: dict[str, str] = {}
        reconfigure_entry = self._get_reconfigure_entry()

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            try:
                session = async_get_clientsession(self.hass)
                url = f"http://{host}:{DEFAULT_PORT}"
                async with session.get(url, timeout=_TIMEOUT) as resp:
                    resp.raise_for_status()
                    data = await resp.json(content_type=None)

                if "device" not in data or "status" not in data.get("device", {}):
                    errors["base"] = "invalid_response"
                else:
                    return self.async_update_reload_and_abort(
                        reconfigure_entry,
                        data_updates={CONF_HOST: host},
                    )

            except (aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            except ValueError:
                errors["base"] = "invalid_response"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception during reconfigure flow")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {vol.Required(CONF_HOST, default=reconfigure_entry.data[CONF_HOST]): str}
            ),
            errors=errors,
        )
