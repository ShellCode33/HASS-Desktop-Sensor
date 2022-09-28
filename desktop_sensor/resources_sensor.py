# coding: utf-8

from typing import List, Union
import psutil
from datetime import datetime

from desktop_sensor.sensors import BinarySensor, Sensor

# From https://gist.github.com/dhrrgn/7255361
def human_delta(tdelta):
    """
    Takes a timedelta object and formats it for humans.
    Usage:
        # 149 day(s) 8 hr(s) 36 min 19 sec
        print human_delta(datetime(2014, 3, 30) - datetime.now())
    Example Results:
        23 sec
        12 min 45 sec
        1 hr(s) 11 min 2 sec
        3 day(s) 13 hr(s) 56 min 34 sec
    :param tdelta: The timedelta object.
    :return: The human formatted timedelta
    """
    d = dict(days=tdelta.days)
    d['hrs'], rem = divmod(tdelta.seconds, 3600)
    d['min'], d['sec'] = divmod(rem, 60)

    if d['min'] == 0:
        fmt = '{sec} sec'
    elif d['hrs'] == 0:
        fmt = '{min} min {sec} sec'
    elif d['days'] == 0:
        fmt = '{hrs} hr(s) {min} min {sec} sec'
    else:
        fmt = '{days} day(s) {hrs} hr(s) {min} min {sec} sec'

    return fmt.format(**d)

def get() -> List[Union[Sensor, BinarySensor]]:
    sensors = [] # type: List[Union[Sensor, BinarySensor]]

    cpu_usage = psutil.cpu_percent(percpu=True) # List[float]

    sensors.append(Sensor(name="CPU Usage (Average)",
                          type="power_factor",
                          state=sum(cpu_usage) / len(cpu_usage),
                          unit="%"))

    for i, usage in enumerate(cpu_usage):
        sensors.append(Sensor(name=f"CPU Usage (Core #{i})",
                              type="power_factor",
                              state=usage,
                              unit="%"))

    battery = psutil.sensors_battery()

    if battery:
        sensors.append(BinarySensor(name="Charging",
                              type="battery_charging",
                              state=battery.power_plugged))

        sensors.append(Sensor(name="Battery State",
                              type="battery",
                              state=battery.percent,
                              unit="%"))

    mount_points = {disk.mountpoint for disk in psutil.disk_partitions()}

    for mount_point in mount_points:
        sensors.append(Sensor(name=f"Disk usage of {mount_point}",
                              state=psutil.disk_usage(mount_point).percent,
                              unit="%"))

    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    sensors.append(Sensor(name="Uptime", state=human_delta(uptime), type="duration"))

    sensors.append(Sensor(name="Used RAM", state=psutil.virtual_memory().percent, unit="%"))
    sensors.append(Sensor(name="Used Swap", state=psutil.swap_memory().percent, unit="%"))

    return sensors
