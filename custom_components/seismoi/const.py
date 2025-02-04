"""Define constants for the Seismoi events integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "seismoi"

PLATFORMS: Final = [Platform.GEO_LOCATION]

ATTR_EXTERNAL_ID: Final = "external_id"
DEFAULT_RADIUS_IN_KM: Final = 20.0
DEFAULT_RADIUS_IN_M: Final = 20000.0
DEFAULT_MAGNITUDE: Final = 3.2
DEFAULT_UPDATE_INTERVAL: Final = timedelta(seconds=300)
SOURCE: Final = "Institude of Geodynamics"
URL: Final = "https://bbnet2.gein.noa.gr/data/1"

SIGNAL_DELETE_ENTITY: Final = "seismoi_delete_{}"
SIGNAL_UPDATE_ENTITY: Final = "seismoi_update_{}"
