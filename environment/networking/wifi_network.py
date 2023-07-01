import logging
from dataclasses import field, dataclass
from typing import List, Optional, Callable

from environment.networking.connection_protocol import ConnectionProtocol
from environment.networking.transfer_type import TransferType
from environment.utils.vector import Vector


@dataclass
class WiFiNetwork:
    center: Vector
    bandwidth: int
    coverage_radius: int
    max_num_of_devices: int
    protocol: ConnectionProtocol
    connections: List['Connection'] = field(init=False, default_factory=list)

    def update_connections_distances(self) -> None:
        for connection in self.connections:
            if self.center.distance_from(connection.device2.position) > self.coverage_radius:
                self.disconnect_from(connection.device2.id)

    def is_connected_to(self, id: int) -> bool:
        return self.get_connection_by_id(id) is not None

    def update_connections_speed(self):
        new_speed = self.bandwidth // len(self.connections)
        for connection in self.connections:
            connection.speed = new_speed

    def get_connection_by_id(self, id: int) -> Optional['Connection']:
        for connection in self.connections:
            if connection.device2.id == id:
                return connection
        return None

    def update_connections(self, action: Callable, connection: 'Connection') -> None:
        action(connection)
        self.update_connections_speed()

    def add_connection(self, connection: 'Connection') -> None:
        if self.get_connection_by_id(connection.device2.id) is not None:
            logging.warning(f'{self} is already connected to device {id}')
            return
        self.update_connections(self.connections.append, connection)
        logging.info(f'connection has been established between {self} and device {id}')

    def disconnect_from(self, id: int) -> None:
        connection = self.get_connection_by_id(id)
        if connection is None:
            logging.error(f'{self} is not connected to device {id}')
            return
        self.update_connections(self.connections.remove, connection)
        logging.info(f'{self} disconnected from device {id}')

    def transfer_data(self, source: 'Device', destination: 'Device', data_size: int,
                      transfer_type: TransferType) -> 'DataTransition':
        connection = self.get_connection_by_id(destination.id)
        if not self.is_connected_to(destination.id):
            if not source.in_range(destination):
                logging.info(f'{destination} is out of {source} range')
                return None
            from environment.networking.connection import Connection
            connection = Connection(source, destination, self.protocol)
            self.add_connection(connection)
        return connection.run(data_size, transfer_type)
