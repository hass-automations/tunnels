from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_DISPLAY_NAME, DEFAULT_DISPLAY_NAME

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_DISPLAY_NAME, default=DEFAULT_DISPLAY_NAME): str,
    }
)


class TunnelsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tunnels (VPN tunnel manager)."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    def __init__(self) -> None:
        """Initialize config flow."""
        self._display_name: str = DEFAULT_DISPLAY_NAME

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            self._display_name = (
                user_input.get(CONF_DISPLAY_NAME) or DEFAULT_DISPLAY_NAME
            ).strip() or DEFAULT_DISPLAY_NAME
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=self._display_name,
                data={CONF_DISPLAY_NAME: self._display_name},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            description_placeholders={},
        )
