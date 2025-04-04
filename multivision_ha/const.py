"""Constants."""

from homeassistant.const import Platform

DOMAIN = "multivision_ha"  # has to be the same as parent directory name and match the name in manifest.json
PLATFORMS = [Platform.LIGHT]  # delegates to each <PLATFORM>.py
CONF_MANAGER = "manager"