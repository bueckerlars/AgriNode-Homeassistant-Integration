"""AgriNode Integration für Home Assistant."""
import asyncio
import logging
from datetime import timedelta

import aiohttp
import async_timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, API_ENDPOINT, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the AgriNode component from YAML configuration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up AgriNode from a config entry."""
    host = entry.data["host"]
    api_key = entry.data.get("api_key")
    port = entry.data.get("port", 5066)

    coordinator = AgriNodeDataUpdateCoordinator(hass, host, port, api_key)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class AgriNodeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass, host, port, api_key):
        """Initialize."""
        self.host = host
        self.port = port
        self.api_key = api_key
        self.api_endpoint = f"http://{host}:{port}{API_ENDPOINT}"
        self.sensors = {}
        self.sensors_data = {}
        self.session = aiohttp.ClientSession()

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=SCAN_INTERVAL)
        )

    async def _async_update_data(self):
        """Update data via API."""
        try:
            # Fetch sensors (if needed) and then fetch data for each sensor
            return await self._fetch_data()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def _fetch_sensors(self):
        """Fetch available sensors from the API."""
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"ApiKey {self.api_key}"

            async with async_timeout.timeout(10):
                response = await self.session.get(
                    f"http://{self.host}:{self.port}/api/sensors", headers=headers
                )
                if response.status == 200:
                    data = await response.json()
                    if data.get("success", False) and "data" in data:
                        self.sensors = {sensor["sensor_id"]: sensor for sensor in data["data"]}
                        return self.sensors
                    return {}
                else:
                    _LOGGER.error("Error fetching sensors: %s", response.status)
                    return {}
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error("Error fetching sensors: %s", err)
            return {}

    async def _fetch_data(self):
        """Fetch data for all sensors."""
        # Ensure we have a list of sensors
        if not self.sensors:
            await self._fetch_sensors()

        # Fetch data for each sensor
        result = {}
        for sensor_id in self.sensors:
            try:
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"ApiKey {self.api_key}"

                async with async_timeout.timeout(10):
                    response = await self.session.get(
                        f"http://{self.host}:{self.port}/api/sensor-data/sensor/{sensor_id}",
                        headers=headers,
                    )
                    if response.status == 200:
                        data = await response.json()
                        if "success" in data and data["success"] and "data" in data:
                            # Sort by timestamp to get most recent data
                            sensor_data = sorted(
                                data["data"], 
                                key=lambda x: x.get("timestamp", ""), 
                                reverse=True
                            )
                            if sensor_data:
                                result[sensor_id] = sensor_data[0]  # Get most recent data
                    else:
                        _LOGGER.error(
                            "Error fetching data for sensor %s: %s", sensor_id, response.status
                        )
            except (asyncio.TimeoutError, aiohttp.ClientError) as err:
                _LOGGER.error("Error fetching data for sensor %s: %s", sensor_id, err)

        return {"sensors": self.sensors, "data": result}