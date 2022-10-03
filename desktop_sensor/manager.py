# coding: utf-8

from desktop_sensor.sensors import BinarySensor, Sensor
import os
import sys
import time
import logging
import argparse
import requests
from typing import List, Dict, Union
from string import ascii_lowercase, digits
from urllib.parse import urlparse

from desktop_sensor import idle_sensor, resources_sensor
from desktop_sensor.idle_sensor import SUPPORTED_IDLE_HELPERS, IdleSensorException

SENSOR_MODULES = {idle_sensor, resources_sensor}

def normalize_name(name: str) -> str:
    allowed_charset = " _" + ascii_lowercase + digits
    normalized_name = name.lower()
    normalized_name = normalized_name.replace("/", " slash ") # for disk usage
    normalized_name = "".join([c for c in normalized_name if c in allowed_charset])
    normalized_name = "_".join(normalized_name.split())
    return normalized_name

def hass_update(hass_url: str, hass_device_name: str, sensors: List[Union[Sensor, BinarySensor]]) -> None:
    normalized_device_name = normalize_name(hass_device_name)

    # Normalize URL because apparently Home Assistant returns 404 if url is like : http://hass:8123//api (double /)
    normalized_url = urlparse(hass_url)
    normalized_url = f"{normalized_url.scheme}://{normalized_url.netloc}/api/states/"

    hass_access_token = os.environ["HASS_ACCESS_TOKEN"].strip()

    for sensor in sensors:
        endpoint = normalized_url

        attributes = {
            "friendly_name": sensor.name,
            "device_class": sensor.type,
            "icon": sensor.icon,
        } # type: Dict[str, Union[str, None]]

        if isinstance(sensor, BinarySensor):
            state = "on" if sensor.state else "off"
            endpoint += "binary_"
        elif isinstance(sensor, Sensor):
            state = sensor.state
            attributes.update({"unit_of_measurement": sensor.unit})
        else:
            raise TypeError(f"Expected Sensor or BinarySensor, got {sensor}")

        endpoint += f"sensor.{normalized_device_name}_{normalize_name(sensor.name)}"

        try:
            resp = requests.post(
                endpoint,
                headers={"Authorization": f"Bearer {hass_access_token}"},
                json={"state": state, "attributes": attributes}
            )

            if resp.status_code not in {200, 201}:
                logging.error(f"HASS API returned {resp.content} (code: {resp.status_code})")

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            logging.error("HTTP request to HASS failed, will retry later")
            return

def parse_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Welcome to the desktop sensor utility')

    parser.add_argument('--hass-device-name', help="friendly name of the computer you're running this on")
    parser.add_argument('--hass-url', help="URL (including port) to your Home Assistant instance")

    parser.add_argument('--idle-helper', choices=SUPPORTED_IDLE_HELPERS, default="xidlehook", help="the external binary that should be used to detect activity")
    parser.add_argument('--idle-delay', type=int, help="the delay (in seconds) to wait before the user must be considered idle", default=60 * 5)
    parser.add_argument('--report-interval', type=int, help="the interval (in seconds) at which reports will be made to Home Assistant", default=5)

    args = parser.parse_args()
    return args

def main() -> None:
    log_level = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(level=log_level, format="[%(levelname)s] %(asctime)s %(message)s")

    args = parse_cli()

    if "HASS_ACCESS_TOKEN" not in os.environ:
        logging.error("HASS_ACCESS_TOKEN environment variable missing")
        sys.exit(1)

    idle_sensor.setup(args.idle_helper, args.idle_delay)

    try:
        while True:
            for sensor_module in SENSOR_MODULES:
                sensors = sensor_module.get() # type: List[Union[BinarySensor, Sensor]]

                if not isinstance(sensors, list):
                    sensors = [sensors]

                hass_update(args.hass_url, args.hass_device_name, sensors)

            time.sleep(args.report_interval)
    except IdleSensorException as ise:
        logging.error(f"idle sensor failed: {ise}")
    except KeyboardInterrupt:
        print("\nBye !")
