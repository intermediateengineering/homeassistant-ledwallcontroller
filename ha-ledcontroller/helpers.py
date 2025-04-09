from __future__ import annotations
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from ledcontroller import TCPHandler
from dataclasses import dataclass
from .const import DOMAIN, CONN_HANDLERS

@dataclass
class Connection:
    host: str
    port: int

    @classmethod
    def from_handler(cls, handler: TCPHandler) -> Connection:
        return Connection(
            host=handler.host,
            port=handler.port
        )

async def async_setup_connection_handler(hass: HomeAssistant, connection: Connection):
    set_or_create_handler(hass, connection)
    handler = get_handler(hass, connection)

    try:
        await handler.connect()
    except Exception as e:
        raise ConfigEntryNotReady() from e

    if not handler.connected:
        raise ConfigEntryNotReady(f"Couldnt connect to LED Controller @ tcp://{connection.host}:{connection.port}")

def set_or_create_handler(hass: HomeAssistant, connection: Connection):
    """Ensures that exactly one TCPHandler is set per Connection in Homeassistant."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(CONN_HANDLERS, [])

    handlers: list[TCPHandler] = hass.data[DOMAIN][CONN_HANDLERS]
    for handler in handlers:
        if Connection.from_handler(handler) == connection:
            return

    handlers.append(TCPHandler(
        host=connection.host,
        port=connection.port
    ))

def get_handler(hass: HomeAssistant, connection: Connection) -> TCPHandler | None:
    """Get the Connection-Handler for the connection."""
    if not hass.data[DOMAIN][CONN_HANDLERS]:
        raise Exception(f"Couldnt find any connection for {connection.host}:{connection.port}")

    for handler in hass.data[DOMAIN][CONN_HANDLERS]:
        if Connection.from_handler(handler) == connection:
            return handler