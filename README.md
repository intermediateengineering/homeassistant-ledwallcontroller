# Home Assistant LED Wall Controller

A [Home Assistant](https://www.home-assistant.io/) integration for LED Wall controllers

## Features

- Represents a LED Wall controller as a light entity

Supported Systems:

- Multivision
- OnlyGlass

> [!important]
> This integration is currently only useful for internal needs but can be extended if necessary

## Installation

### Installation via HACS

1. Add this repository as a custom repository to HACS:

[![Add Repository](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=intermediateengineering&repository=ledwallcontroller&category=Integration)

2. Use HACS to install the integration.
3. Restart Home Assistant.
4. Set up the integration using the UI:

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ha-ledcontroller)


### Manual Installation

1. Download the integration files from the GitHub repository.
2. Place the integration folder in the custom_components directory of Home Assistant.
3. Restart Home Assistant.
4. Set up the integration using the UI:

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ha-ledcontroller)

## Debugging

It is possible to show the info and debug logs for the Pi-hole V6 integration, to do this you need to enable logging in the configuration.yaml, example below:

```
logger:
  default: warning
  logs:
    # Log for Pi-hole V6 integation
    custom_components.ha-ledcontroller: debug
```

Logs do not remove sensitive information so careful what you share, check what you are about to share and blank identifying information.

## Local Testing

When testing inside DevContainers use "host.docker.internal" as host.


