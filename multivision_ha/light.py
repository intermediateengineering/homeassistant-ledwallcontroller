"""Platform for Multivision LED Controller integration."""
from __future__ import annotations

import logging
import asyncio

# Import the device class from the component that you want to support
from homeassistant.components.light import (ATTR_BRIGHTNESS, ColorMode,
                                            LightEntity)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.const import CONF_COUNT
from .const import DOMAIN
from multivision import ControllerManager, LEDController


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the LED controller light from a config entry."""

    manager: ControllerManager = entry.runtime_data
    count = entry.data[CONF_COUNT]
    for i in range(1, count+1): # Multivision IDs start at 1
        manager.add_controller("multivision", i) # TODO ID should be supplied by the user
        await manager.controllers[-1].update()
        await asyncio.sleep(0.5)

    async_add_entities(
        [LEDControllerLightEntity(c, manager, entry, hass)
        for c in manager.controllers])


class LEDControllerLightEntity(LightEntity):
    """Representation of an Multivision LED Controller"""

    def __init__(self, controller: LEDController, manager: ControllerManager, entry: ConfigEntry, hass: HomeAssistant) -> None:
        """Initialize the LED light."""
        self._controller = controller
        self._id: int = controller.api.controller_id
        self._entry_id = entry.entry_id
        self._host = manager.tcp_handler.host
        self._port = manager.tcp_handler.port

        self._attr_name = f"LED Controller #{self._id}"  # Or something user-friendly
        self._attr_unique_id = f"multivision_led_{self._id}_@_{self._host}:{self._port}"  # Provide a stable, unique ID

        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self._attr_is_on = controller.brightness_8bit > 0
        self._attr_brightness = controller.brightness_8bit

    @property
    def device_info(self) -> DeviceInfo:
        """
        Return device information to group this entity under a device.
        Using the same 'identifiers' tuple on multiple entities
        will group them under one device in Home Assistant.
        """
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name="Multivision LED Controller",
            manufacturer="Multivision",
            model="TCP LED Controller",
            sw_version="1.0",
        )

    async def async_turn_on(self, **kwargs):
        """Turn on the light."""
        # If brightness was passed in the service call, use it
        if ATTR_BRIGHTNESS in kwargs:
            self._attr_brightness = kwargs[ATTR_BRIGHTNESS]
        _LOGGER.info( "Setting %s to brightness=%d", self._attr_name, self._attr_brightness)
        self._attr_is_on = True
        await self._controller.set_brightness_8bit(self._attr_brightness)
        # await self.async_schedule_update_ha_state(force_refresh=True)
        await self.async_update()

    async def async_turn_off(self, **kwargs):
        """Set the brightness of the controller to 0."""
        _LOGGER.info("Turning off Multivision LED Controller: %s:%s", self._host, self._port)
        self._attr_is_on = False
        await self._controller.set_brightness_percent(0)
        await self.async_update()

    async def async_update(self):
        """Fetch new data from the controller."""
        try:
            await self._controller.update()
            await asyncio.sleep(.5)
            brightness = self._controller.brightness_8bit
            self._attr_brightness = brightness
            self._attr_is_on = brightness > 0
            self.async_write_ha_state()
        except TypeError:
            raise UpdateFailed("Didnt receive Data from the device yet (or received invalid Data).")
        except Exception as e:
            raise UpdateFailed(e)

