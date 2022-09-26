# coding: utf-8

import os
import sys
import logging
import argparse
from desktop_sensor.idle_sensor import SUPPORTED_IDLE_HELPERS

REQUIRED_ENV_VARIABLE = {"HASS_DEVICE_NAME", "HASS_URL", "HASS_ACCESS_TOKEN"}

def main() -> None:
    parser = argparse.ArgumentParser(description='Welcome to the desktop sensor utility')
    parser.add_argument('--hass-device-name')
    parser.add_argument('--hass-url')
    parser.add_argument('--hass-access-token')
    parser.add_argument('--report-interval', type=int, help="the interval at which reports will be made to Home Assistant")
    parser.add_argument('--idle-helper', choices=SUPPORTED_IDLE_HELPERS, help="the external binary that should be used to detect activity")

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

    for var in REQUIRED_ENV_VARIABLE:
        if var not in os.environ:
            logging.error(f"Missing from environment: '{var}'")
            sys.exit(1)

