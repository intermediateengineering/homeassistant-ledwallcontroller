"""Constants."""

from homeassistant.const import Platform

DOMAIN = "ha-ledcontroller"  # has to be the same as parent directory name and match the name in manifest.json
PLATFORMS = [Platform.LIGHT]  # delegates to each <PLATFORM>.py
CONF_MULTIVISION = "Multivision"
CONF_ONLYGLASS = "OnlyGlass"
CONN_HANDLERS = "handler"
