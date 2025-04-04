"""Manager for Multivision LED Controllers."""

import multivision
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.exceptions import ConfigEntryNotReady


class MultivisionManager:
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry
        self.hass = hass
        self._manager: multivision.ControllerManager = None

    @property
    def host(self) -> str:
        return self.config_entry.data[CONF_HOST]

    @property
    def port(self) -> str:
        return self.config_entry.data[CONF_PORT]

    @property
    def controllers(self) -> list[multivision.LEDController]:
        return self._manager.controllers

    async def async_initialize_manager(self) -> bool:
        manager = multivision.ControllerManager(self.host, self.port)
        try:
            await manager.connect_tcp_host()
        except Exception as e:
            raise ConfigEntryNotReady(e)

        if not manager.tcp_handler.connected:
            raise ConfigEntryNotReady(f"Couldnt connect to Multivision Controller Manager @ tcp://{self.host}:{self.port}")

        self._manager = manager
        return True

    async def add_controller(self, id: int):
        self._manager.add_controller("multivision", id)
        await self._manager.controllers[-1].update()