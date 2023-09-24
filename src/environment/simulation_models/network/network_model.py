from dataclasses import field, dataclass
from typing import List

from src.environment.simulation_models.network.connection_protocol import ConnectionProtocol
from src.environment.simulation_models.network.data_transition import TransferType
from src.environment.utils.vector import Vector


@dataclass
class NetworkModel:
    center: Vector
    bandwidth: int
    coverage_radius: int
    protocol: ConnectionProtocol
    connections: List = field(init=False, default_factory=list)

    def update_connections_distances(self) -> None:
        for connection in self.connections:
            if self.center.distance_from(connection.device2.position) > self.coverage_radius:
                self.disconnect(connection)

    def step(self) -> None:
        self.update_connections_distances()

    def in_range(self, position: Vector) -> bool:
        return self.center.distance_from(position) <= self.coverage_radius

    def is_connected_to(self, device) -> bool:
        return self.get_connection(device) is not None

    def update_connections_speed(self):
        if len(self.connections) == 0:
            return
        new_speed = self.bandwidth // len(self.connections)
        for connection in self.connections:
            connection.update_speed(new_speed)

    def connect(self, source, destination, speed=0):
        from src.environment.simulation_models.network.connection import Connection
        connection = Connection(source, destination, self.protocol, speed)
        self.connections.append(connection)
        self.update_connections_speed()
        return connection

    def disconnect(self, connection):
        self.connections.remove(connection)
        self.update_connections_speed()

    def transfer_data(self, source, destination, data_size: int, transfer_type: TransferType, time_step: int,
                      speed: int = 0):
        connection = self.get_connection(destination)
        if connection is None:
            # if not source.in_range(destination):
            #     return None
            assert source.in_range(destination), f'{destination} must be in range of the {source}'
            connection = self.connect(source, destination, speed)
        return connection.run(data_size, transfer_type, time_step)

    def delete_all_connections(self) -> None:
        self.connections.clear()

    def get_connection(self, device):
        for connection in self.connections:
            if connection.device2 == device:
                return connection
        return None
