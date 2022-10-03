# coding: utf-8

import subprocess
import logging
import time
from threading import Thread, Lock
from typing import Optional
from desktop_sensor.sensors import BinarySensor

_last_known_status_lock = Lock()
_last_known_status = "active"
sensor_exception = None # type: Optional[IdleSensorException]

SUPPORTED_IDLE_HELPERS = {
    "xidlehook",
}

class IdleSensorException(Exception):
    "Thrown when something went wrong with the idle sensor"

def _run_xidlehook(interval: int) -> None:
    global sensor_exception

    try:
        process = subprocess.Popen([
            "xidlehook",
            #"--not-when-fullscreen",
            "--not-when-audio",
            "--timer", str(interval),
            "echo idle",
            "echo active"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.2) # Give it some time to start properly
    except FileNotFoundError:
        sensor_exception = IdleSensorException(f"xidlehook not found, make sure it's available")
        return

    if process.stdout is None:
        sensor_exception = IdleSensorException("stdout is not accessible")
        return

    if process.stderr is None:
        sensor_exception = IdleSensorException("stdout is not accessible")
        return

    logging.info("xidlehook started")

    while process.poll() is None:
        line = process.stdout.readline()
        status = line[:-1].decode()

        if status in {"idle", "active"}:
            with _last_known_status_lock:
                global _last_known_status
                _last_known_status = status

            logging.debug(f"Status set to {status}")

        else:
            logging.error(f"Unexpected status value: {status}")

        time.sleep(0.5)

    for line in process.stderr:
        logging.error(f"xidlehook: {line.decode().strip()}")

    sensor_exception = IdleSensorException("xidlehook stopped running")

def get() -> BinarySensor:

    if sensor_exception:
        raise sensor_exception

    with _last_known_status_lock:
        return BinarySensor(name="Activity",
                            state=_last_known_status == "active",
                            icon="mdi:account-question")

def setup(idle_helper: str, interval: int) -> None:

    if idle_helper not in SUPPORTED_IDLE_HELPERS:
        raise IdleSensorException(f"{idle_helper} helper is not supported")

    idle_helper_func = eval(f"_run_{idle_helper}")
    Thread(target=idle_helper_func, daemon=True, args=(interval,)).start()
    time.sleep(0.4) # Give some time to the thread to start properly
