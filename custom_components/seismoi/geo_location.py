"""Support for generic Seismoi events."""

from __future__ import annotations

from collections.abc import Callable
import logging
from typing import Any

from aio_geojson_generic_client.feed_entry import GenericFeedEntry

from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SeismoiFeedEntityManager
from .const import (
    DEFAULT_MAGNITUDE,
    DOMAIN,
    SIGNAL_DELETE_ENTITY,
    SIGNAL_UPDATE_ENTITY,
    SOURCE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Seismoi Events platform."""
    manager: SeismoiFeedEntityManager = hass.data[DOMAIN][entry.entry_id]

    @callback
    def async_add_geolocation(
        feed_manager: SeismoiFeedEntityManager,
        external_id: str,
    ) -> None:
        """Add geolocation entity from feed."""
        new_entity = SeismoiLocationEvent(feed_manager, external_id)
        magnitude = float(feed_manager.get_entry(external_id).properties["Magnitude"])
        if magnitude > float(entry.options.get("Magnitude", DEFAULT_MAGNITUDE)):
            _LOGGER.debug("Adding geolocation %s", new_entity)
            async_add_entities([new_entity], True)

    manager.listeners.append(
        async_dispatcher_connect(hass, manager.signal_new_entity, async_add_geolocation)
    )
    # Do not wait for update here so that the setup can be completed and because an
    # update will fetch data from the feed via HTTP and then process that data.
    entry.async_create_task(hass, manager.async_update())
    _LOGGER.debug("Geolocation setup done")


class SeismoiLocationEvent(GeolocationEvent):
    """Represents an external event with Seismoi data."""

    _attr_should_poll = False
    _attr_source = SOURCE
    _attr_unit_of_measurement = UnitOfLength.KILOMETERS

    def __init__(
        self,
        feed_manager: SeismoiFeedEntityManager,
        external_id: str,
    ) -> None:
        """Initialize entity with data from feed entry."""
        self._feed_manager = feed_manager
        self._external_id = external_id
        self._attr_unique_id = f"{feed_manager.entry_id}_{external_id}"
        self._remove_signal_delete: Callable[[], None]
        self._remove_signal_update: Callable[[], None]

    async def async_added_to_hass(self) -> None:
        """Call when entity is added to hass."""
        self._remove_signal_delete = async_dispatcher_connect(
            self.hass,
            SIGNAL_DELETE_ENTITY.format(self._external_id),
            self._delete_callback,
        )
        self._remove_signal_update = async_dispatcher_connect(
            self.hass,
            SIGNAL_UPDATE_ENTITY.format(self._external_id),
            self._update_callback,
        )

    @callback
    def _delete_callback(self) -> None:
        """Remove this entity."""
        self._remove_signal_delete()
        self._remove_signal_update()
        self.hass.async_create_task(self.async_remove(force_remove=True))

    @callback
    def _update_callback(self) -> None:
        """Call update method."""
        self.async_schedule_update_ha_state(True)

    async def async_update(self) -> None:
        """Update this entity from the data held in the feed manager."""
        _LOGGER.debug("Updating %s", self._external_id)
        feed_entry = self._feed_manager.get_entry(self._external_id)
        if feed_entry:
            self._update_from_feed(feed_entry)

    def _update_from_feed(self, feed_entry: GenericFeedEntry) -> None:
        """Update the internal state from the provided feed entry."""
        self._attr_name = f"{DOMAIN}_{feed_entry.properties["EventId"]}"
        self._attr_distance = feed_entry.distance_to_home
        self._attr_latitude = feed_entry.coordinates[0]
        self._attr_longitude = feed_entry.coordinates[1]
        self._attr_magnitude = feed_entry.properties["Magnitude"]
        self._attr_depth = feed_entry.properties["Depth"]
        self._attr_gmt = feed_entry.properties["Gmt"]
        self._attr_type = feed_entry.properties["Type"]
        self._attr_location = feed_entry.properties["Location"]
        self._attr_location_gr = feed_entry.properties["Location_gr"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the device state attributes."""
        return {
            "magnitude": self._attr_magnitude,
            "depth": self._attr_depth,
            "gmt": self._attr_gmt,
            "type": self._attr_type,
            "location": self._attr_location,
            "location_gr": self._attr_location_gr,
        }
