from copy import deepcopy
from dataclasses import dataclass
from typing import Tuple, Any, List

import pandas as pd

from environment.devices.base_station import BaseStation
from environment.devices.memory import Memory
from environment.devices.uav import UAV
from environment.devices.sensor import Sensor
from environment.core.environment import Environment
from environment.networking.connection_protocol import ConnectionProtocol
from environment.networking.data_packet_collection import DataPacketCollection
from environment.networking.wifi_network import WiFiNetwork
from environment.utils.vector import Vector


@dataclass
class FileManager:
    solution_id: int

    def __post_init__(self):
        self.input_dir = f'data/input/sample_{self.solution_id}/'
        self.output_dir = f'data/output/sample_{self.solution_id}/'

    def read_table(self, path: str) -> Any:
        return pd.read_csv(self.input_dir + path)

    def load_basic_variables(self) -> Tuple[int, int, int]:
        table = self.read_table(path='environment_basics.csv')
        data = []
        for index, row in table.iterrows():
            data.append((row['width'], row['height'], row['speed rate']))
        return data[0][0], data[0][1], data[0][2]

    def load_sensors(self) -> List[Sensor]:
        sensors = []
        table = self.read_table(path='sensors.csv')
        for index, row in table.iterrows():
            id = int(str(index))
            velocity = Vector(row['x velocity'], row['y velocity'], row['z velocity'])
            position = Vector(row['x'], row['y'], row['z'])
            acceleration = Vector(row['x acceleration'], row['y acceleration'], row['z acceleration'])
            buffer = Memory(row['buffer size'], row['buffer io speed'])
            memory = Memory(row['memory size'], row['memory io speed'])
            protocol = ConnectionProtocol(row['network protocol data loss percentage'],
                                          row['network protocol data loss probability'],
                                          row['network protocol data init size'])
            network = WiFiNetwork(position, row['network bandwidth'], row['network coverage radius'],
                                  row['network max devices'],
                                  protocol)
            data_collecting_rate = row['data collecting rate']
            sensor = Sensor(position, velocity, acceleration, id, buffer, memory, network, 0, data_collecting_rate)
            init_data_size = row['initial data size']
            num_of_packets = init_data_size / 30
            sensor.memory.store_data([DataPacketCollection(life_time=40, packet_size=30, created_time=0,
                                                           num_of_packets=num_of_packets)])
            sensors.append(sensor)
        return sensors

    def load_base_stations(self) -> List[BaseStation]:
        base_stations = []
        table = self.read_table(path='base_stations.csv')
        for index, row in table.iterrows():
            id = int(str(index))
            velocity = Vector(row['x velocity'], row['y velocity'], row['z velocity'])
            position = Vector(row['x'], row['y'], row['z'])
            acceleration = Vector(row['x acceleration'], row['y acceleration'], row['z acceleration'])
            buffer = Memory(row['buffer size'], row['buffer io speed'])
            memory = Memory(row['memory size'], row['memory io speed'])
            protocol = ConnectionProtocol(row['network protocol data loss percentage'],
                                          row['network protocol data loss probability'],
                                          row['network protocol data init size'])
            network = WiFiNetwork(position, row['network bandwidth'], row['network coverage radius'],
                                  row['network max devices'],
                                  protocol)
            base_station = BaseStation(position, velocity, acceleration, id, buffer, memory, network, 0)
            base_stations.append(base_station)
        return base_stations

    def load_uavs(self) -> List[UAV]:
        uavs = []
        uav_table = self.read_table(path='uavs.csv')
        way_points_table = self.read_table(path='way_points.csv')
        for index, row in uav_table.iterrows():
            id = int(str(index)) + 1
            velocity = Vector(row['x velocity'], row['y velocity'], row['z velocity'])
            position = Vector(row['x'], row['y'], row['z'])
            acceleration = Vector(row['x acceleration'], row['y acceleration'], row['z acceleration'])
            buffer = Memory(row['buffer size'], row['buffer io speed'])
            memory = Memory(row['memory size'], row['memory io speed'])
            protocol = ConnectionProtocol(row['network protocol data loss percentage'],
                                          row['network protocol data loss probability'],
                                          row['network protocol data init size'])
            network = WiFiNetwork(position, row['network bandwidth'], row['network coverage radius'],
                                  row['network max devices'],
                                  protocol)
            uav = UAV(position, velocity, acceleration, id, buffer, memory, network, 0, row['energy'], [], [])
            uavs.append(uav)
        for index, row in way_points_table.iterrows():
            position = Vector(row['x'], row['y'], row['z'])
            id = int(row['uav id'])
            found = None
            for uav in uavs:
                if uav.id == id:
                    found = uav
                    break
            found.way_points.append(position)
            found.areas_collection_rates.append(row['collection rate'])
        return uavs

    def load_environment(self) -> Environment:
        height, width, speed_rate = self.load_basic_variables()
        uavs = self.load_uavs()
        sensors = self.load_sensors()
        base_stations = self.load_base_stations()
        return Environment(width, height, speed_rate, uavs, sensors, base_stations)
