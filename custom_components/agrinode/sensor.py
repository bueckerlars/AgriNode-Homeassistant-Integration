"""Support for AgriNode sensors."""
from datetime import datetime
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the AgriNode sensors from config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Wait for the coordinator to do at least one refresh
    await coordinator.async_config_entry_first_refresh()

    entities = []
    for sensor_id, sensor_info in coordinator.data["sensors"].items():
        for sensor_type, properties in SENSOR_TYPES.items():
            # Check if this sensor has data for this sensor type
            if sensor_id in coordinator.data["data"] and sensor_type in coordinator.data["data"][sensor_id]:
                entities.append(
                    AgriNodeSensor(
                        coordinator, 
                        sensor_id, 
                        sensor_type, 
                        properties, 
                        sensor_info
                    )
                )

    async_add_entities(entities)


class AgriNodeSensor(CoordinatorEntity, SensorEntity):
    """Implementation of an AgriNode sensor."""

    def __init__(
        self, 
        coordinator: DataUpdateCoordinator, 
        sensor_id: str, 
        sensor_type: str, 
        properties: dict,
        sensor_info: dict
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_id = sensor_id
        self._sensor_type = sensor_type
        self._attr_name = f"{sensor_info['name']} {properties['name']}"
        self._attr_unique_id = f"agrinode_{sensor_id}_{sensor_type}"
        self._attr_native_unit_of_measurement = properties["unit"]
        self._attr_device_class = properties.get("device_class")
        self._attr_state_class = properties.get("state_class")
        self._attr_icon = properties.get("icon")
        
        # Create a device info dictionary
        self._attr_device_info = {
            "identifiers": {(DOMAIN, sensor_id)},
            "name": sensor_info["name"],
            "manufacturer": "AgriNode",
            "model": sensor_info.get("type", "Generic Sensor"),
        }
        
        # Add optional location as the suggested area
        if sensor_info.get("location"):
            self._attr_suggested_area = sensor_info["location"]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if (
            self._sensor_id in self.coordinator.data["data"]
            and self._sensor_type in self.coordinator.data["data"][self._sensor_id]
        ):
            self._attr_native_value = self.coordinator.data["data"][self._sensor_id][self._sensor_type]
            
            # For battery sensor, we want a percentage (between 0 and 100)
            if self._sensor_type == "battery_level" and self._attr_native_value is not None:
                self._attr_native_value = min(100, max(0, float(self._attr_native_value)))
        
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # The entity is available if the coordinator has data and the sensor has data
        return (
            self.coordinator.last_update_success
            and self._sensor_id in self.coordinator.data["data"]
            and self._sensor_type in self.coordinator.data["data"][self._sensor_id]
        )

    @property
    def last_reset(self):
        """Return the time when the sensor was last reset, if any."""
        return None  # We don't reset cumulative sensors

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = {}
        
        # Add timestamp if available
        if (
            self._sensor_id in self.coordinator.data["data"]
            and "timestamp" in self.coordinator.data["data"][self._sensor_id]
        ):
            timestamp = self.coordinator.data["data"][self._sensor_id]["timestamp"]
            if timestamp:
                attrs["last_updated"] = timestamp
        
        return attrs