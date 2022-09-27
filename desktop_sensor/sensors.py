# coding: utf-8

from typing import Union, Optional
from dataclasses import dataclass

@dataclass(frozen=True)
class BinarySensor:
    name: str
    state: bool

@dataclass(frozen=True)
class Sensor:
    name: str
    value: Union[str, int, float]
    unit: Optional[str] = None
    type: Optional[str] = None # See https://www.home-assistant.io/integrations/sensor/#device-class
