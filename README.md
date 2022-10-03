# HASS Desktop Sensor

Desktop activity sensor for Home Assistant

## Features

- Tracks idleness thanks to [xidlehook](https://github.com/jD91mZM2/xidlehook)
- Reports system resources usage

By default you'll be considered idle if you don't use the mouse and keyboard for 5 minutes.
Note that if you're playing some audio, you won't be considered idle. This is to prevent
false positives while watching videos.

The Desktop Sensor will report status to HASS every 5 seconds by default.

## Requirements

- [Install xidlehook](https://github.com/jD91mZM2/xidlehook#installation)
- Enable the [API integration](https://www.home-assistant.io/integrations/api/) of Home Assistant (just add `api:` to your `configuration.yaml`).
- Create a long-lived access token (go to your profile in Home Assistant, scroll down to the bottom, and click "Create Token")

## Installation

As simple as :

```bash
$ pip install --user hass-desktop-sensor
````

To make sure it's working, try to run the script manually like so :

```bash
$ HASS_ACCESS_TOKEN=[YOUR ACCESS TOKEN HERE] hass_desktop_sensor --hass-url 'http://homeassistant.local:8123' --hass-device-name 'My Laptop'
```

To test your automations, you can pass `--idle-delay 1` and `--report-interval 1` to the command line.
You will be considered idle after 1 second, and your idleness status will be reported every second.
This is useful for debug purposes but I don't recommend doing that in real world scenarios.

*Note:* You can increase log verbosity by setting `LOGLEVEL=DEBUG` at the beginning of your command line.

## Automatic startup

Chances are you are using systemd, if you're not, you're on your own. But I'm pretty sure if you're not
using systemd you'll figure out by yourself how to automatically start this script :)

So... For systemd users, create a service file with the following content :

```ini
[Unit]
Description=Home Assistant Desktop Sensor

[Service]
Type=simple
Environment=HASS_ACCESS_TOKEN=[YOUR ACCESS TOKEN HERE]
ExecStart=hass_desktop_sensor --hass-url 'http://homeassistant.local:8123' --hass-device-name 'My Laptop'

[Install]
WantedBy=multi-user.target
```

## Ping integration

If for whatever reason the desktop sensor is not able to report idleness (power failure, network issues, etc.)
some of your automations might not trigger. This is why additionnaly to this desktop sensor, I suggest you
setup the [ping integration](https://www.home-assistant.io/integrations/ping/) of Home Assistant to turn off
what is usually turned on by your automations based on the Desktop Sensor.
