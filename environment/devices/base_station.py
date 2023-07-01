from dataclasses import dataclass

from environment.devices.device import Device


@dataclass(order=True)
class BaseStation(Device):
    pass
