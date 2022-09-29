# coding: utf-8

import psutil
import humanize
from datetime import datetime
from typing import List, Union

from desktop_sensor.sensors import BinarySensor, Sensor

def get() -> List[Union[Sensor, BinarySensor]]:
    sensors = [] # type: List[Union[Sensor, BinarySensor]]

    cpu_usage = psutil.cpu_percent(percpu=True) # List[float]

    sensors.append(Sensor(name="CPU Usage (Average)",
                          type="power_factor",
                          state=int(sum(cpu_usage) / len(cpu_usage)),
                          unit="%",
                          icon="mdi:cpu-64-bit"))

    for i, usage in enumerate(cpu_usage):
        sensors.append(Sensor(name=f"CPU Usage (Core #{i})",
                              type="power_factor",
                              state=int(usage),
                              unit="%",
                              icon="mdi:cpu-64-bit"))

    battery = psutil.sensors_battery()

    if battery:
        sensors.append(BinarySensor(name="Charging",
                              type="battery_charging",
                              state=battery.power_plugged))

        sensors.append(Sensor(name="Battery State",
                              type="battery",
                              state=int(battery.percent),
                              unit="%"))

    mount_points = {disk.mountpoint for disk in psutil.disk_partitions()}

    for mount_point in mount_points:
        sensors.append(Sensor(name=f"Disk usage of {mount_point}",
                              state=psutil.disk_usage(mount_point).percent,
                              unit="%",
                              icon="mdi:harddisk"))

    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    sensors.append(Sensor(name="Uptime", state=humanize.precisedelta(uptime, suppress=["seconds"], format="%d"), type="duration", icon="mdi:clock"))

    sensors.append(Sensor(name="Used RAM", state=int(psutil.virtual_memory().percent), unit="%", icon="mdi:memory"))
    sensors.append(Sensor(name="Used Swap", state=int(psutil.swap_memory().percent), unit="%", icon="mdi:memory"))

    return sensors
