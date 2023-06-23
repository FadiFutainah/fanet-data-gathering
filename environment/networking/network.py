from typing import List

from environment.devices.device import Device
from environment.networking.connection import Connection


class Network:
    bandwidth: int
    source: Device
    connections: List[Connection]
