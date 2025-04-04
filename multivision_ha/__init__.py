"""Multivision LED Controller"""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.exceptions import ConfigEntryNotReady
from .const import PLATFORMS, CONF_MANAGER
from multivision import ControllerManager

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    manager = await async_manager_from_entry(entry)
    entry.runtime_data = manager
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the sensor config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_manager_from_entry(entry: ConfigEntry) -> ControllerManager:
    """Create a Multivision ControllerManager from a ConfigEntry."""
    manager = ControllerManager(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT]
    )
    try:
        await manager.connect_tcp_host()
    except Exception as e:
        raise ConfigEntryNotReady(e)
    
    if not manager.tcp_handler.connected:
        raise ConfigEntryNotReady(f"Couldnt connect to Multivision Controller Manager @ tcp://{self.host}:{self.port}")

    return manager