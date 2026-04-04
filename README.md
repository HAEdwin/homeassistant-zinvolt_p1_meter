# Zinvolt P1 Meter – Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Custom [Home Assistant](https://www.home-assistant.io/) integration for the **Zinvolt P1 Meter**, providing real-time energy monitoring over your local network.

## Features

- **Local polling** – communicates directly with the meter on your LAN; no cloud dependency.
- **Config flow** – set up via the Home Assistant UI (Settings → Devices & Services → Add Integration).
- **Automatic device discovery** – identifies the meter by its serial number and prevents duplicate entries.
- **18 sensor entities** covering:

| Category | Sensors |
|---|---|
| **Power** (W) | Total power, Phase A / B / C power |
| **Voltage** (V) | Phase A / B / C voltage |
| **Current** (A) | Phase A / B / C current |
| **Energy consumed** (kWh) | Total, Off-peak, Flat-rate |
| **Energy returned** (kWh) | Total, Off-peak, Flat-rate |
| **Device info** | Device type, Device model (serial number and firmware version are shown in the device registry) |

- **Energy Dashboard ready** – energy sensors use `total_increasing` state class, they can be added to the Home Assistant Energy dashboard.
- **Fast update interval** – data is polled every 2 seconds by default.

## Requirements

- A **Zinvolt P1-dongle pro** accessible on your local network by Home Assistant.
- **Home Assistant 2024.1** or newer.
<img src="https://github.com/HAEdwin/homeassistant-zinvolt_p1_meter/blob/main/Zinvolt P1-dongle pro.PNG?raw=true">



## Installation

### HACS (recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed.
2. In HACS go to **Integrations** → **⋮** (top-right menu) → **Custom repositories**.
3. Add the repository URL:
   ```
   https://github.com/HAEdwin/homeassistant-zinvolt_p1_meter
   ```
   Category: **Integration**
4. Search for **Zinvolt P1 Meter** in HACS and click **Install**.
5. Restart Home Assistant.

### Manual

1. Copy the `custom_components/zinvolt_p1_meter` folder into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Zinvolt P1 Meter**.
3. Enter the **IP address** of your meter and submit.

The integration will verify connectivity, read the device serial number, and create all sensor entities automatically.

## Troubleshooting

| Error | Cause / Fix |
|---|---|
| *Unable to connect* | Verify the IP address is correct and the meter is powered on and reachable. |
| *Invalid response* | The device responded but returned unexpected data — make sure it is a Zinvolt P1 Meter. |
| *Already configured* | A meter with the same serial number is already set up. Remove or reconfigure the existing entry first. |

## License

See [LICENSE](LICENSE) for details.

## Contributing

Issues and pull requests are welcome on [GitHub](https://github.com/HAEdwin/homeassistant-zinvolt_p1_meter).
