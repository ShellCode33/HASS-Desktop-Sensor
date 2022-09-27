# coding: utf-8

import os
import sys
import time
import logging
import argparse
import requests
from string import ascii_lowercase, digits
from urllib.parse import urlparse

from desktop_sensor import idle_sensor, resources_sensor
from desktop_sensor.idle_sensor import SUPPORTED_IDLE_HELPERS, IdleSensorException

REQUIRED_ENV_VARIABLE = {"HASS_DEVICE_NAME", "HASS_URL", "HASS_ACCESS_TOKEN"}

def normalize_name(name: str) -> str:
    allowed_charset = " _" + ascii_lowercase + digits
    normalized_name = name.lower()
    normalized_name = normalized_name.replace("/", " slash ") # for disk usage
    normalized_name = "".join([c for c in normalized_name if c in allowed_charset])
    normalized_name = "_".join(normalized_name.split())
    return normalized_name

def hass_update() -> None:
    hass_url = os.environ["HASS_URL"].strip()
    hass_access_token = os.environ["HASS_ACCESS_TOKEN"].strip()
    hass_device_name = os.environ["HASS_DEVICE_NAME"].strip()

    normalized_device_name = normalize_name(hass_device_name)

    # Normalize URL because apparently Home Assistant returns 404 if url is like : http://hass:8123//api (double /)
    normalized_url = urlparse(hass_url)
    normalized_url = f"{normalized_url.scheme}://{normalized_url.netloc}"

    resp = requests.post(
        f"{normalized_url}/api/states/binary_sensor.{normalized_device_name}",
        headers={"Authorization": f"Bearer {hass_access_token}"},
        json={"state": idle_sensor.get(), "attributes": {"friendly_name": hass_device_name}}
    )

    if resp.status_code not in [200, 201]:
        logging.error(f"HASS API returned {resp.content} (code: {resp.status_code})")

    for sensor in resources_sensor.get():
        resp = requests.post(
            f"{normalized_url}/api/states/sensor.{normalized_device_name}_{normalize_name(sensor.name)}",
            headers={"Authorization": f"Bearer {hass_access_token}"},
            json={"state": sensor.value, "attributes": {"friendly_name": sensor.name,
                                                        "device_class": sensor.type,
                                                        "unit_of_measurement": sensor.unit}}
        )

        if resp.status_code not in [200, 201]:
            logging.error(f"HASS API returned {resp.content} (code: {resp.status_code})")


def parse_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Welcome to the desktop sensor utility')

    # Hidden parameters, for debug purposes, use environment variables instead
    parser.add_argument('--hass-device-name', help=argparse.SUPPRESS)
    parser.add_argument('--hass-url', help=argparse.SUPPRESS)
    parser.add_argument('--hass-access-token', help=argparse.SUPPRESS)

    parser.add_argument('--idle-helper', choices=SUPPORTED_IDLE_HELPERS, default="xidlehook", help="the external binary that should be used to detect activity")
    parser.add_argument('--idle-delay', type=int, help="the delay (in seconds) to wait before the user must be considered idle", default=30)
    parser.add_argument('--report-interval', type=int, help="the interval (in seconds) at which reports will be made to Home Assistant", default=5)

    args = parser.parse_args()

    if args.hass_device_name:
        os.environ["HASS_DEVICE_NAME"] = args.hass_device_name
        logging.warning("Passing --hass-device-name is for debug purposes only ! "
                        "You should use HASS_DEVICE_NAME environment variable instead")

    if args.hass_url:
        os.environ["HASS_URL"] = args.hass_url
        logging.warning("Passing --hass-url is for debug purposes only ! "
                        "You should use HASS_URL environment variable instead")

    if args.hass_access_token:
        os.environ["HASS_ACCESS_TOKEN"] = args.hass_access_token
        logging.warning("Passing --hass-access-token is for debug purposes only ! "
                        "You should use HASS_ACCESS_TOKEN environment variable instead")

    return args

def check_environment() -> bool:
    is_valid = True

    for var in REQUIRED_ENV_VARIABLE:
        if var not in os.environ:
            logging.error(f"Missing from environment: '{var}'")
            is_valid = False

    return is_valid

def main() -> None:
    log_level = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(level=log_level, format="[%(levelname)s] %(asctime)s %(message)s")

    args = parse_cli()
    is_env_valid = check_environment()

    if not is_env_valid:
        sys.exit(1)

    idle_sensor.setup(args.idle_helper, args.idle_delay)

    try:
        while True:
            hass_update()
            time.sleep(args.report_interval)
    except IdleSensorException as ise:
        logging.error(f"idle sensor failed: {ise}")
    except KeyboardInterrupt:
        print("\nBye !")
