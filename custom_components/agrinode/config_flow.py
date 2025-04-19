"""Config flow for AgriNode integration."""
import logging
import voluptuous as vol
import aiohttp

from homeassistant import config_entries, core, exceptions
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=5066): int,
        vol.Optional(CONF_API_KEY): str,
    }
)


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect."""
    host = data[CONF_HOST]
    port = data.get(CONF_PORT, 5066)
    api_key = data.get(CONF_API_KEY)

    session = async_get_clientsession(hass)
    headers = {"Content-Type": "application/json"}
    
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    try:
        response = await session.get(
            f"http://{host}:{port}/status",
            headers=headers,
        )
        
        if response.status != 200:
            raise CannotConnect(f"Error connecting to API: {response.status}")
        
        return {"title": f"AgriNode Gateway ({host})"}
    except aiohttp.ClientError as err:
        _LOGGER.error("Client error: %s", err)
        raise CannotConnect from err


class AgriNodeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AgriNode."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                
                # Check if we already have an entry with this host
                await self.async_set_unique_id(f"agrinode_{user_input[CONF_HOST]}")
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""