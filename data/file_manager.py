from dataclasses import dataclass
from typing import Any, List, Tuple

import pandas as pd

from environment.core.energy_model import EnergyModel
from environment.core.environment import Environment
from environment.devices.base_station import BaseStation
from environment.devices.memory import Memory
from environment.devices.sensor import Sensor
from environment.devices.uav import UAV
from environment.networking.connection_protocol import ConnectionProtocol
from environment.networking.data_packet_collection import PacketData
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

    def load_basic_variables(self) -> Tuple:
        table = self.read_table(path='environment_basics.csv')
        data = []
        for index, row in table.iterrows():
            energy_model = EnergyModel(e_elec=row['E elec'], c=row['c'], delta=row['delta'],
                                       distance_threshold=row['distance threshold'],
                                       power_amplifier_for_fs=row['power amplifier for fs'],
                                       power_amplifier_for_amp=row['power amplifier for amp'])
            data.append((row['width'], row['height'], row['speed rate'],
                         row['run until'], energy_model))
        return data[0]

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
                                  row['network max devices'], protocol)
            data_collecting_rate = row['data collecting rate']
            packet_life_time = row['packet life time']
            packet_size = row['packet size']
            energy = row['energy']
            sensor = Sensor(position, velocity, acceleration, id, buffer, buffer, memory, network, 0,
                            data_collecting_rate, packet_size, packet_life_time, energy)
            init_data_size = row['initial data size']
            num_of_packets = init_data_size / 30
            sensor.memory.store_data([PacketData(life_time=40, packet_size=30, created_time=0,
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
            energy = row['energy']
            base_station = BaseStation(position, velocity, acceleration, id, buffer, buffer, memory, network, 0, energy)
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
            energy = row['energy']
            uav = UAV(position, velocity, acceleration, id, buffer, buffer, memory, network, 0, energy, [], [])
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
        height, width, speed_rate, run_until, energy_model = self.load_basic_variables()
        uavs = self.load_uavs()
        sensors = self.load_sensors()
        base_stations = self.load_base_stations()
        return Environment(land_height=height, land_width=width, speed_rate=speed_rate, uavs=uavs, sensors=sensors,
                           base_stations=base_stations, run_until=run_until, energy_model=energy_model)
