"""Config flow to configure the Seismoi integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigFlow,
    OptionsFlow,
    ConfigFlowResult,
)
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LOCATION,
    CONF_LONGITUDE,
    CONF_RADIUS,
    CONF_URL,
    UnitOfLength,
)
from homeassistant.helpers import config_validation as cv, selector
from homeassistant.util.unit_conversion import DistanceConverter

from .const import (
    DEFAULT_RADIUS_IN_M,
    DEFAULT_MAGNITUDE,
    DOMAIN,
    URL,
)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_LOCATION): selector.LocationSelector(
            selector.LocationSelectorConfig(radius=True, icon="")
        ),
        vol.Optional("Magnitude", default=DEFAULT_MAGNITUDE): vol.Coerce(float),
    }
)


class SeismoiEventsFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a Seismoi events config flow."""

    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the start of the config flow."""
        if not user_input:
            suggested_values: Mapping[str, Any] = {
                CONF_LOCATION: {
                    CONF_LATITUDE: self.hass.config.latitude,
                    CONF_LONGITUDE: self.hass.config.longitude,
                    CONF_RADIUS: DEFAULT_RADIUS_IN_M,
                }
            }
            data_schema = self.add_suggested_values_to_schema(
                DATA_SCHEMA, suggested_values
            )
            return self.async_show_form(
                step_id="user",
                data_schema=data_schema,
            )

        # url: str = user_input[CONF_URL]
        location: dict[str, Any] = user_input[CONF_LOCATION]
        latitude: float = location[CONF_LATITUDE]
        longitude: float = location[CONF_LONGITUDE]
        self._async_abort_entries_match(
            {
                CONF_URL: URL,
                CONF_LATITUDE: latitude,
                CONF_LONGITUDE: longitude,
            }
        )
        return self.async_create_entry(
            title=f"Seismoi ({latitude}, {longitude})",
            data={
                CONF_URL: URL,
                CONF_LATITUDE: latitude,
                CONF_LONGITUDE: longitude,
                CONF_RADIUS: DistanceConverter.convert(
                    location[CONF_RADIUS],
                    UnitOfLength.METERS,
                    UnitOfLength.KILOMETERS,
                ),
            },
        )

class OptionsFlowHandler(OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            self.hass.config_entries.async_update_entry(self.config_entry, options=user_input)
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "Magnitude",
                        default=self.config_entry.options.get(
                            "Magnitude", DEFAULT_MAGNITUDE
                        ),
                    ): str,
                }
            ),
        )
