"""Generic LED Controller"""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from .const import PLATFORMS
from .helpers import async_setup_connection_handler, Connection

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    conn = Connection(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT]
    )
    await async_setup_connection_handler(hass, conn)
    entry.runtime_data = conn
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the sensor config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
