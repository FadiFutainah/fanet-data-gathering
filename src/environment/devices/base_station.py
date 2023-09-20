from dataclasses import dataclass

from src.environment.devices.device import Device


@dataclass(order=True)
class BaseStation(Device):
    pass
