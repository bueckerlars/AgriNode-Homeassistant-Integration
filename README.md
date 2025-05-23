# AgriNode Integration for Home Assistant

[![Status](https://img.shields.io/badge/Status-Development-yellow)](https://github.com/bueckerlars/AgriNode-Homeassistant-Integration)
[![GitHub Issues](https://img.shields.io/github/issues/bueckerlars/AgriNode-Homeassistant-Integration)](https://github.com/bueckerlars/AgriNode-Homeassistant-Integration/issues)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview

The AgriNode Integration for Home Assistant enables seamless connection with the AgriNode Gateway, allowing you to monitor and visualize data from AgriNode plant sensors in your smart home.

The integration offers the following features:
- Automatic discovery of all sensors from the AgriNode Gateway
- Creation of separate devices for each sensor
- Dedicated entities for each measurement (temperature, humidity, soil moisture, brightness, battery level)
- Regular sensor data updates
- Support for authentication with API keys

## Installation

### Manual Installation

1. Copy the `custom_components/agrinode` folder to the `custom_components` directory of your Home Assistant installation.
   ```bash
   cp -r custom_components/agrinode /path/to/your/homeassistant/config/custom_components/
   ```

2. Restart Home Assistant.

### Installation with HACS (Home Assistant Community Store)

1. Make sure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance.
2. Click on "Integration" in the HACS interface.
3. Click on the three dots in the top right corner and select "Custom repository".
4. Add the GitHub repository link to the AgriNode integration and select "Integration" as the category.
5. Click "Add".
6. Search for "AgriNode" and install the integration.
7. Restart Home Assistant.

## Configuration

After installation, the integration can be configured through the Home Assistant user interface:

1. Go to "Configuration" > "Devices & Services" > "Add Integration".
2. Search for "AgriNode" and select it.
3. Enter the required information:
   - **Host**: The IP address or hostname of the AgriNode Gateway
   - **Port**: The port on which the gateway is accessible (default: 5066)
   - **API Key**: Optional, if your gateway requires an API key for authentication

## Entities and Devices

For each sensor registered in the AgriNode Gateway, the integration creates a separate device in Home Assistant. Each device has multiple entities, depending on which measurements the sensor can provide:

### Sensors
- **Temperature**: Air temperature in °C
- **Humidity**: Relative air humidity in %
- **Soil Moisture**: Relative soil moisture in %
- **Brightness**: Ambient light intensity in Lux (lx)
- **Battery**: Battery status in %

All sensors have the following properties:
- Correct units according to Home Assistant standards
- Appropriate icons and device classes
- Additional attributes such as timestamp of last update

## Update Interval

Sensor data is fetched from the AgriNode Gateway every 5 minutes. This interval can be adjusted by editing the `const.py` file if a different update interval is desired.

## Troubleshooting

### The integration does not appear in the list

- Make sure the `agrinode` folder is correctly placed in your `custom_components` directory
- Check the Home Assistant logs for errors during the loading of the integration

### Connection errors

- Check if the AgriNode Gateway is accessible
- Ensure that the URL is correctly formatted (e.g., the correct IP and port)
- Verify that your API key is valid (if used)
- Test the gateway connection with the command `curl http://YOUR_GATEWAY_IP:PORT/status`

### No data

- Check if your sensors are properly registered and active in the AgriNode Gateway
- Make sure the sensors have sent data recently
- Check permissions to ensure that the API key used has access to the sensor data

## API Endpoints

The integration uses the following API endpoints of the AgriNode Gateway:

- `/status`: Connection check
- `/api/sensors`: Fetch all available sensors
- `/api/sensor-data/sensor/{sensor_id}`: Fetch sensor data for a specific sensor

## Privacy

The integration stores the following data:
- Configuration data (host, port, API key)
- Cached sensor data during runtime

All data is stored locally in your Home Assistant instance.

## Requirements

- Home Assistant 2023.1.0 or higher
- Working AgriNode Gateway (version 0.5.0 or higher)
- Network connection between Home Assistant and the AgriNode Gateway

## Supported by

- [Home Assistant](https://www.home-assistant.io/)
- [AgriNode Project](https://github.com/bueckerlars/AgriNode)

## Version History

- 0.1.0: Initial version with basic functions

## License

This integration is licensed under the MIT License. See the attached license file for details.
