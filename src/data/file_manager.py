import copy
import os
from dataclasses import dataclass, field
from typing import Any, List, Tuple

import pandas as pd

from src.agents.data_collection_agent import DataCollectionAgent
from src.agents.data_forwarding_agent import DataForwardingAgent
from src.algorithms.dqn_algorithm import DQNAgent
from src.environment.simulation_models.energy.energy_model import EnergyModel
from src.environment.core.environment import Environment
from src.environment.devices.base_station import BaseStation
from src.environment.simulation_models.memory.memory import Memory
from src.environment.devices.sensor import Sensor
from src.environment.devices.uav import UAV
from src.environment.simulation_models.memory.memory_model import MemoryModel
from src.environment.simulation_models.network.connection_protocol import ConnectionProtocol
from src.environment.simulation_models.network.network_model import NetworkModel
from src.environment.utils.vector import Vector


@dataclass
class FileManager:
    solution_id: int
    memory_models: list = field(init=False, default_factory=list)
    network_models: list = field(init=False, default_factory=list)
    energy_model: EnergyModel = field(init=False, default_factory=list)

    def __post_init__(self):
        self.input_dir = f'data/input/test_sample_{self.solution_id}/'
        self.output_dir = f'data/output/test_sample_{self.solution_id}/'
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

    def read_table(self, name: str) -> Any:
        if len(name) <= 4 or name[-4:] != '.csv':
            name += '.csv'
        return pd.read_csv(self.input_dir + name)

    def load_basic_variables(self) -> Tuple:
        basic_variables_table = self.read_table(name='environment_basics')
        energy_model_table = self.read_table(name='energy_model')
        assert len(
            list(basic_variables_table.iterrows())) == 1, 'environment_basics should not contains more than one row'
        assert len(list(energy_model_table.iterrows())) == 1, 'energy_model should not contains more than one row'
        data = []
        for index, row in basic_variables_table.iterrows():
            data.append((row['width'], row['height'], row['speed rate'], row['run until']))
        for index, row in energy_model_table.iterrows():
            energy_model = EnergyModel(e_elec=row['e_elec'], c=row['c'], delta=row['delta'], scale=row['scale'],
                                       distance_threshold=row['distance_threshold'],
                                       power_amplifier_for_fs=row['power_amplifier_for_fs'],
                                       power_amplifier_for_amp=row['power_amplifier_for_amp'])
            data[0] += (energy_model,)
        return data[0]

    def load_sensors(self) -> List[Sensor]:
        sensors = []
        table = self.read_table(name='sensors.csv')
        for index, row in table.iterrows():
            id = int(str(index))
            velocity = Vector(row['x velocity'], row['y velocity'], row['z velocity'])
            position = Vector(row['x'], row['y'], row['z'])
            acceleration = Vector(row['x acceleration'], row['y acceleration'], row['z acceleration'])
            data_collecting_rate = row['data collecting rate']
            packet_life_time = row['packet life time']
            packet_size = row['packet size']
            energy = row['energy']
            sensor = Sensor(position=position, velocity=velocity, acceleration=acceleration, id=id,
                            memory_model=self.memory_models[0], network_model=self.network_models[0],
                            num_of_collected_packets=0, data_collecting_rate=data_collecting_rate,
                            packet_size=packet_size, packet_life_time=packet_life_time, consumed_energy=energy,
                            energy_model=self.energy_model)
            sensors.append(sensor)
        return sensors

    def load_base_stations(self) -> List[BaseStation]:
        base_stations = []
        table = self.read_table(name='base_stations.csv')
        for index, row in table.iterrows():
            id = int(str(index))
            velocity = Vector(row['x velocity'], row['y velocity'], row['z velocity'])
            position = Vector(row['x'], row['y'], row['z'])
            acceleration = Vector(row['x acceleration'], row['y acceleration'], row['z acceleration'])
            energy = row['energy']
            base_station = BaseStation(position=position, velocity=velocity, acceleration=acceleration, id=id,
                                       memory_model=self.memory_models[1], network_model=self.network_models[1],
                                       consumed_energy=energy, num_of_collected_packets=0,
                                       energy_model=self.energy_model)
            base_stations.append(base_station)
        return base_stations

    def load_uavs(self) -> List[UAV]:
        uavs = []
        uav_table = self.read_table(name='uavs.csv')
        way_points_table = self.read_table(name='way_points.csv')
        for index, row in uav_table.iterrows():
            id = int(str(index)) + 1
            velocity = Vector(row['x velocity'], row['y velocity'], row['z velocity'])
            position = Vector(row['x'], row['y'], row['z'])
            acceleration = Vector(row['x acceleration'], row['y acceleration'], row['z acceleration'])
            energy = row['energy']
            speed = row['speed']
            uav = UAV(position=position, velocity=velocity, acceleration=acceleration, id=id,
                      memory_model=self.memory_models[2], network_model=self.network_models[2],
                      energy_model=self.energy_model, num_of_collected_packets=0, way_points=[],
                      speed=speed)
            uavs.append(uav)
        for index, row in way_points_table.iterrows():
            position = Vector(row['x'], row['y'], row['z'])
            id = int(row['uav id'])
            found = None
            for uav in uavs:
                if uav.id == id:
                    found = uav
                    break
            found.add_way_point(position, row['collection rate'])
        return uavs

    def load_agents(self):
        tables = [self.read_table('agent_data'), self.read_table('data_collection_agent'),
                  self.read_table('data_forward_agent'), self.read_table('dqn_data')]
        for index, row in tables[0].iterrows():
            action_size = row['action_size']
            state_size = row['state_size']
            epsilon_min = row['epsilon_min']
            epsilon = row['epsilon']
            epsilon_decay = row['epsilon_decay']
            max_steps_in_episode = row['max_steps_in_episode']
            num_of_episodes = row['num_of_episodes']
            alpha = row['alpha']
            gamma = row['gamma']
        for index, row in tables[1].iterrows():
            alpha1 = row['alpha1']
            beta1 = row['beta1']
        for index, row in tables[2].iterrows():
            max_delay = row['max_delay']
            max_energy = row['max_energy']
            max_queue_length = row['max_queue_length']
            beta = row['beta']
            gamma_e = row['gamma_e']
            sigma_q = row['sigma_q']
            lambda_d = row['lambda_d']
            k = row['k']
        for index, row in tables[3].iterrows():
            checkpoint_path = row['checkpoint_path']
            checkpoint_freq = row['checkpoint_freq']
            state_dim = row['state_dim']
            buffer_size = row['buffer_size']
            batch_size = row['batch_size']
            tau = row['tau']
            target_update_freq = row['target_update_freq']
        data_collection_agent = DataCollectionAgent(alpha=alpha1, beta=beta1, action_size=action_size,
                                                    state_size=state_size, env=None)
        data_forwarding_agent = DataForwardingAgent(beta=beta, lambda_d=lambda_d,
                                                    max_queue_length=max_queue_length, max_energy=max_energy,
                                                    max_delay=max_delay, state_size=state_size, action_size=action_size,
                                                    gamma_e=gamma_e, k=k, env=None)
        dqn_algorithm = DQNAgent(agent=data_forwarding_agent, alpha=alpha, batch_size=batch_size,
                                 max_steps=max_steps_in_episode, num_of_episodes=num_of_episodes,
                                 epsilon_min=epsilon_min, epsilon_decay=epsilon_decay, epsilon=epsilon, gamma=gamma,
                                 buffer_size=buffer_size, tau=tau)
        return data_collection_agent, data_forwarding_agent, dqn_algorithm

    def load_memories(self):
        table = self.read_table(name='memory_models')
        data = []
        for index, row in table.iterrows():
            sending_buffer = Memory(size=row['buffer size'], io_speed=row['buffer io speed'])
            memory = Memory(size=row['memory size'], io_speed=row['memory io speed'])
            receiving_buffer = copy.copy(sending_buffer)
            data.append(MemoryModel(sending_buffer=sending_buffer, receiving_buffer=receiving_buffer, memory=memory))
        return data

    def load_networks(self):
        table = self.read_table(name='network_models')
        data = []
        for index, row in table.iterrows():
            protocol = ConnectionProtocol(data_loss_percentage=row['data loss percentage'],
                                          data_loss_probability=row['data loss probability'],
                                          initialization_data_size=row['data init size'])
            network = NetworkModel(center=Vector(0, 0, 0), bandwidth=row['bandwidth'],
                                   coverage_radius=row['coverage radius'], protocol=protocol)
            data.append(network)
        return data

    def load_environment(self) -> Environment:
        height, width, speed_rate, run_until, self.energy_model = self.load_basic_variables()
        self.memory_models = self.load_memories()
        self.network_models = self.load_networks()
        uavs = self.load_uavs()
        sensors = self.load_sensors()
        base_stations = self.load_base_stations()
        return Environment(land_height=height, land_width=width, speed_rate=speed_rate, uavs=uavs, sensors=sensors,
                           base_stations=base_stations, run_until=run_until)
