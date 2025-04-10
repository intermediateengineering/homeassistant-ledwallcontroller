"""Platform for Generic LED Controller integration."""

from __future__ import annotations

import logging

# Import the device class from the component that you want to support
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
    LightEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.const import CONF_ID, CONF_TYPE
from . import const as c
from .helpers import Connection, get_handler
from ledcontroller import Multivision, OnlyGlass, TCPHandler, Controller
from dataclasses import dataclass

_LOGGER = logging.getLogger(__name__)


@dataclass(kw_only=True, frozen=True)
class LEDControllerLightEntityDescription(LightEntityDescription):
    """Description for LED Controller light entities."""

    controller: Controller
    handler: TCPHandler
    controller_type: str


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the LED controller light from a config entry."""

    conn: Connection = entry.runtime_data
    handler: TCPHandler = get_handler(hass, conn)
    id = None

    controller: Controller = None
    match entry.data[CONF_TYPE]:
        case c.CONF_MULTIVISION:
            id = entry.data[CONF_ID]
            controller = Multivision(handler, id)
            controller_type = c.CONF_MULTIVISION
            name = f"Module #{id}"
        case c.CONF_ONLYGLASS:
            controller = OnlyGlass(handler)
            controller_type = c.CONF_ONLYGLASS
            name = "Brightness"

    description = LEDControllerLightEntityDescription(
        key=f"led_controller_light_{id or 0}",
        name=name,
        controller=controller,
        handler=handler,
        controller_type=controller_type,
        icon="mdi:led-outline",
    )

    async_add_entities([LEDControllerLightEntity(description)], update_before_add=True)


class LEDControllerLightEntity(LightEntity):
    """Representation of an Generic LED Controller as Light Entity"""

    _attr_has_entity_name = True
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS

    def __init__(self, entity_description: LEDControllerLightEntityDescription) -> None:
        """Initialize the LED light."""
        self.entity_description = entity_description
        self._attr_unique_id = f"{entity_description.key}_{entity_description.handler.host}:{entity_description.handler.port}"

    @property
    def device_info(self) -> DeviceInfo:
        """
        Return device information to group this entity under a device.
        Using the same 'identifiers' tuple on multiple entities
        will group them under one device in Home Assistant.
        """
        return DeviceInfo(
            identifiers={(c.DOMAIN, self._attr_unique_id)},
            name=f"{self.entity_description.controller_type} LED Controller",
            manufacturer=self.entity_description.controller_type,
            model="TCP LED Controller",
            sw_version="1.0",
        )

    @property
    def brightness(self) -> int | None:
        return self.entity_description.controller.brightness_8bit

    @property
    def is_on(self) -> bool | None:
        if not self.brightness:
            return None

        return self.brightness > 0

    async def async_turn_on(self, **kwargs):
        """Turn on the light."""
        # If brightness was passed in the service call, use it
        brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        _LOGGER.debug(
            "Setting %s to brightness=%d", self.entity_description.name, brightness
        )
        await self.entity_description.controller.set_brightness_8bit(brightness)
        self.async_schedule_update_ha_state(force_refresh=True)

    async def async_turn_off(self, **kwargs):
        """Set the brightness of the controller to 0."""
        _LOGGER.debug("Turning off %s", self.entity_description.name)
        await self.entity_description.controller.set_brightness_percent(0)
        self.async_schedule_update_ha_state(force_refresh=True)

    async def async_update(self):
        """Fetch new data from the controller."""
        try:
            await self.entity_description.controller.update()
        except Exception as e:
            raise UpdateFailed() from e
