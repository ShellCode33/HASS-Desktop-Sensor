# coding: utf-8

from typing import Union, Optional
from dataclasses import dataclass

@dataclass(frozen=True)
class Sensor:
    name: str
    state: Union[str, int, float]
    unit: Optional[str] = None
    type: Optional[str] = None # See https://www.home-assistant.io/integrations/sensor/#device-class
    icon: Optional[str] = None # Must start with "mdi:", see https://materialdesignicons.com/

@dataclass(frozen=True)
class BinarySensor:
    name: str
    state: bool
    type: Optional[str] = None
    icon: Optional[str] = None
