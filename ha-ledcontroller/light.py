"""Platform for Generic LED Controller integration."""
from __future__ import annotations

import logging

# Import the device class from the component that you want to support
from homeassistant.components.light import (ATTR_BRIGHTNESS, ColorMode,
                                            LightEntity)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.const import CONF_ID, CONF_TYPE
from . import const as c
from .helpers import Connection, get_handler
from ledcontroller import Multivision, OnlyGlass, TCPHandler, Controller

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the LED controller light from a config entry."""

    conn: Connection = entry.runtime_data
    handler: TCPHandler = get_handler(hass, conn)
    id = entry.data[CONF_ID]

    controller: Controller = None
    match entry.data[CONF_TYPE]:
        case c.CONF_MULTIVISION:
            controller = Multivision(handler, id)
        case c.CONF_ONLYGLASS:
            controller = OnlyGlass(handler)

    async_add_entities(
        [LEDControllerLightEntity(controller, entry)],
        update_before_add=True)


class LEDControllerLightEntity(LightEntity):
    """Representation of an Generic LED Controller as Light Entity"""

    def __init__(self, controller: Controller, entry: ConfigEntry) -> None:
        """Initialize the LED light."""
        self._controller = controller
        self._controller_type = controller.__class__.__name__
        self._entry_id = entry.entry_id
        id = entry.data[CONF_ID]

        self._attr_name = f"{self._controller_type} LED Controller #{id}"  # Or something user-friendly
        self._attr_unique_id = f"tcp_led_controller_{id}_@_{controller._handler.host}:{controller._handler.port}"  # Provide a stable, unique ID

        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        self._attr_color_mode = ColorMode.BRIGHTNESS

    @property
    def device_info(self) -> DeviceInfo:
        """
        Return device information to group this entity under a device.
        Using the same 'identifiers' tuple on multiple entities
        will group them under one device in Home Assistant.
        """
        return DeviceInfo(
            identifiers={(c.DOMAIN, self._entry_id)},
            name=f"{self._controller_type} LED Controller",
            manufacturer=self._controller_type,
            model="TCP LED Controller",
            sw_version="1.0",
        )

    @property
    def brightness(self) -> int | None:
        return self._controller.brightness_8bit

    @property
    def is_on(self) -> bool | None:
        if not self.brightness:
            return None

        return self.brightness > 0

    async def async_turn_on(self, **kwargs):
        """Turn on the light."""
        # If brightness was passed in the service call, use it
        brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        _LOGGER.debug( "Setting %s to brightness=%d", self._attr_name, self._attr_brightness)
        await self._controller.set_brightness_8bit(brightness)
        self.async_schedule_update_ha_state(force_refresh=True)

    async def async_turn_off(self, **kwargs):
        """Set the brightness of the controller to 0."""
        _LOGGER.debug("Turning off %s", self._attr_name)
        await self._controller.set_brightness_percent(0)
        self.async_schedule_update_ha_state(force_refresh=True)

    async def async_update(self):
        """Fetch new data from the controller."""
        try:
            await self._controller.update()
        except Exception as e:
            raise UpdateFailed() from e
