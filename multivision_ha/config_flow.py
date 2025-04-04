"""Config Flow."""

import voluptuous as vol

from typing import Any
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
import homeassistant.helpers.config_validation as cv

from homeassistant.const import CONF_HOST, CONF_PORT, CONF_COUNT
from .const import DOMAIN

SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT, default=4010): cv.port,
        vol.Required(CONF_COUNT, default=1): cv.positive_int,
    }
)


class MultivisionConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow in the UI."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        # If user has submitted the form
        if user_input is not None:
            # Create the config entry
            return self.async_create_entry(title="Multivision LED Controller", data=user_input)

        return self.async_show_form(step_id="user", data_schema=SCHEMA, errors=errors)
