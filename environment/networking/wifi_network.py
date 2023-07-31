import logging
from dataclasses import field, dataclass
from typing import List

from environment.networking.connection_protocol import ConnectionProtocol
from environment.networking.transfer_type import TransferType
from environment.utils.vector import Vector


@dataclass
class WiFiNetwork:
    center: Vector
    bandwidth: int
    coverage_radius: int
    protocol: ConnectionProtocol
    connections: List = field(init=False, default_factory=list)

    def update_connections_distances(self) -> None:
        for connection in self.connections:
            if self.center.distance_from(connection.device2.position) > self.coverage_radius:
                self.disconnect(connection)

    def is_connected_to(self, device) -> bool:
        return self.get_connection(device) is not None

    def update_connections_speed(self):
        if len(self.connections) == 0:
            return
        new_speed = self.bandwidth // len(self.connections)
        for connection in self.connections:
            connection.speed = new_speed

    def connect(self, source, destination):
        from environment.networking.connection import Connection
        connection = Connection(source, destination, self.protocol)
        self.connections.append(connection)
        self.update_connections_speed()
        return connection
        # logging.info(f' connection added between {self} and {connection.device2}')

    def disconnect(self, connection):
        self.connections.remove(connection)
        self.update_connections_speed()
        # logging.info(f' connection removed between {self} and {connection.device2}')

    def transfer_data(self, source, destination, data_size: int, transfer_type: TransferType):
        connection = self.get_connection(destination)
        if connection is None:
            if not source.in_range(destination):
                logging.info(f'{destination} is out of {source} range')
                return None
            connection = self.connect(source, destination)
        return connection.run(data_size, transfer_type)

    def delete_all_connections(self) -> None:
        self.connections.clear()

    def get_connection(self, device):
        for connection in self.connections:
            if connection.device2 == device:
                return connection
        return None
