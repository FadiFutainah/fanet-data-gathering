from typing import List

from environment.devices.device import Device
from environment.networking.connection import Connection


class Network:
    bandwidth: int
    source: Device
    max_num_of_devices: int
    connections: List[Connection]

    def run(self) -> None:
        for connection in self.connections:
            connection.run()

    def add_connection(self, connection: Connection):
        self.connections.append(connection)
