"""Constants for the AgriNode integration."""

DOMAIN = "agrinode"
DEFAULT_NAME = "AgriNode"
API_ENDPOINT = "/api/sensor-data"
SCAN_INTERVAL = 300  # Default scan interval in seconds (5 minutes)

# Configuration and options
CONF_HOST = "host"
CONF_PORT = "port"
CONF_API_KEY = "api_key"

# Sensor types
SENSOR_TYPES = {
    "air_temperature": {
        "name": "Temperature",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    "air_humidity": {
        "name": "Humidity",
        "unit": "%",
        "icon": "mdi:water-percent",
        "device_class": "humidity",
        "state_class": "measurement",
    },
    "soil_moisture": {
        "name": "Soil Moisture",
        "unit": "%",
        "icon": "mdi:water",
        "device_class": "moisture",
        "state_class": "measurement",
    },
    "brightness": {
        "name": "Brightness",
        "unit": "lx",
        "icon": "mdi:brightness-5",
        "device_class": "illuminance",
        "state_class": "measurement",
    },
    "battery_level": {
        "name": "Battery",
        "unit": "%",
        "icon": "mdi:battery",
        "device_class": "battery",
        "state_class": "measurement",
    },
}