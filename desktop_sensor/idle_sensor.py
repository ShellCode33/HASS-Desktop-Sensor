# coding: utf-8

from subprocess import run

SUPPORTED_IDLE_HELPERS = {
    "xidlehook",
}

class IdleSensorException(Exception):
    "Thrown when something went wrong with the idle sensor"

def run_xidlehook() -> None:
    try:
        run(["xidlehook",
             "--not-when-fullscreen",
             "--not-when-audio",
             "--timer", "120", "echo idle", "echo active"])
    except FileNotFoundError:
        raise IdleSensorException(f"xidlehook not found, make sure it's available")

def main(idle_helper: str) -> None:

    if idle_helper not in SUPPORTED_IDLE_HELPERS:
        raise IdleSensorException(f"{idle_helper} helper is not supported")

    eval(f"run_{idle_helper}")()
