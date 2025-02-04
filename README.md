[![GitHub Release](https://img.shields.io/github/release/bkbilly/Seismoi.svg?style=flat-square)](https://github.com/bkbilly/Seismoi/releases)
[![License](https://img.shields.io/github/license/bkbilly/Seismoi.svg?style=flat-square)](LICENSE)
[![hacs](https://img.shields.io/badge/HACS-default-orange.svg?style=flat-square)](https://hacs.xyz)


# Seismoi - Home Assistant Custom Integration

Seismoi is a custom integration for Home Assistant that provides real-time earthquake event data for Greece. This integration allows users to track seismic activity in their chosen location and set up automations based on earthquake events.

## Features
 - Fetches real-time earthquake data from official Greek Geodynamic Institute.
 - Configurable location and radius for earthquake alerts.
 - Customizable minimum magnitude filter.
 - Home Assistant entity updates when a new earthquake event occurs.

## Installation

Easiest install is via [HACS](https://hacs.xyz/):

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=bkbilly&repository=Seismoi&category=integration)

Navigate to Settings > Devices & Services.
 - Click Add Integration and search for Seismoi.
 - Configure the integration by selecting:
   - Your location (latitude, longitude, and radius).
   - Minimum magnitude filter.
 - Click Submit to save the configuration.


## Automations
Example automation to send a notification when an earthquake is detected:
```yaml
trigger:
  - platform: geo_location
    source: seismoi
    zone: zone.danger
    event: enter
action:
  - action: notify.persistent_notification
    data:
      message: "{{ trigger }}"
```
