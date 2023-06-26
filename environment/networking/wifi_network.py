import logging
from typing import List, Optional

from environment.devices.device import Device
from environment.networking.connection import Connection
from environment.networking.transfer_type import TransferType
from environment.networking.data_transition import DataTransition
from environment.networking.connection_protocol import ConnectionProtocol


class WiFiNetwork:
    bandwidth: int
    source: Device
    coverage_radius: int
    max_num_of_devices: int
    protocol: ConnectionProtocol
    connections: List[Connection]

    def run(self) -> None:
        for connection in self.connections:
            if self.source.position.distance_from(connection.destination.position) > self.coverage_radius:
                self.remove_connection(connection.destination.id)
            else:
                connection.run()

    def is_connected_to(self, id: int) -> bool:
        return self.get_connection_by_id(id) is not None

    def update_connections_speed(self):
        new_speed = self.bandwidth // len(self.connections)
        for connection in self.connections:
            connection.speed = new_speed

    def get_connection_by_id(self, id: int) -> Optional[Connection]:
        for connection in self.connections:
            if connection.destination.id == id:
                return connection
        return None

    def get_connection(self, connection: Connection) -> Optional[Connection]:
        for c1 in self.connections:
            if c1.destination.id == id:
                return connection
        return None

    def add_connection(self, connection: Connection) -> None:
        found = self.get_connection(connection)
        if found is not None:
            logging.warning(f'{self} is already connected to device {id}')
            return
        self.connections.append(connection)
        self.update_connections_speed()
        logging.info(f'connection has been established between {self} and device {id}')

    def remove_connection(self, id: int) -> None:
        connection = self.get_connection_by_id(id)
        if connection is None:
            logging.error(f'{self} is not connected to device {id}')
            return
        self.connections.remove(connection)
        self.update_connections_speed()
        logging.info(f'{self} disconnected from device {id}')

    def transfer_data(self, destination: Device, data_size: int, transfer_type: TransferType) -> DataTransition:
        connection = self.get_connection_by_id(destination.id)
        if not self.is_connected_to(destination.id):
            connection = Connection(destination=destination, protocol=self.protocol)
            self.add_connection(connection)
        source = self.source
        if transfer_type == TransferType.SEND:
            connection.get_data()
        elif transfer_type == TransferType.RECEIVE:
            source = destination
        return DataTransition(source, data_packets, destination, destination.protocol)
