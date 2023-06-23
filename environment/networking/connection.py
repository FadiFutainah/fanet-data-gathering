from dataclasses import dataclass

from environment.devices.device import Device


@dataclass
class Connection:
    speed: int
    destination: Device

    def run_connection(self):
        pass
