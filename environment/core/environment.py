import logging
from typing import Dict, List

import numpy as np

from copy import deepcopy
from dataclasses import dataclass, field

from environment.devices.uav import UAV
from environment.devices.sensor import Sensor
from environment.devices.base_station import BaseStation
from environment.networking.data_transition import DataTransition


@dataclass
class Environment:
    land_width: float
    land_height: float
    maximum_delay: int
    uavs: List[UAV] = List[UAV]
    sensors: List[Sensor] = List[Sensor]
    base_stations: List[BaseStation] = List[BaseStation]
    environment_speed_rate: int = field(default=1)
    time_step: int = field(init=False, default=0)
    data_loss: int = field(init=False, default=0)
    initial_state: 'Environment' = field(init=False)
    uav_data_transitions: Dict[int, List[DataTransition]] = field(init=False)
    sensors_data_transitions: Dict[int, List[DataTransition]] = field(init=False)
    base_stations_data_transitions: Dict[int, List[DataTransition]] = field(init=False)

    def __post_init__(self) -> None:
        self.uav_data_transitions = {}
        self.sensors_data_transitions = {}
        self.base_stations_data_transitions = {}
        self.initial_state = deepcopy(self)
        self.divide_to_areas()

    def divide_to_areas(self):
        for uav in self.uavs:
            for _ in uav.way_points:
                uav.add_area(0)

    @staticmethod
    def get_area_index(uav: UAV) -> int:
        return uav.current_way_point

    def calculate_data_forwarding_reward(self):
        pass

    def calculate_e2e_delay(self) -> float:
        sum_of_delays = 0
        ns = 0
        """ the number of successfully received packets """

        for time_step, data_transitions in self.base_stations_data_transitions:
            for data_transition in data_transitions:
                for data_packets in data_transition.data:
                    sum_of_delays += (time_step - data_packets.packet_size) * data_packets.num_of_packets
                    ns += data_packets.num_of_packets
        return sum_of_delays / ns

    def calculate_delay_penalty(self):
        pass

    def run_sensors(self) -> None:
        pass

    def run_base_stations(self) -> None:
        pass

    def calculate_data_collection_reward(self, uav: UAV) -> float:
        alpha, beta = 1, 1
        data = List[int]
        for key, value in self.sensors_data_transitions:
            np.append(data, [e.data_size for e in value])
        reward = alpha * uav.energy + beta * np.var(data)
        return reward

    def data_forwarding_state(self, uav_index: int):
        return self.uavs[uav_index], self.get_neighbouring_uavs(uav_index),

    def run_uavs(self) -> None:
        for uav in self.uavs:
            index = self.get_area_index(uav)
            if uav.areas_collection_rates[index] != 0:
                self.collect_data(uav)
            else:
                uav.move_to_next_position()

    def run_connected_devices(self):
        for sensor, uav, base_station in zip(self.sensors, self.uavs, self.base_stations):
            uav.prepare_data_sending()
            sensor.prepare_data_sending()
            base_station.prepare_data_sending()

    def run_agent(self):
        pass

    def run(self) -> None:
        self.time_step += self.environment_speed_rate
        logging.info(f'time step {self.time_step}:')
        self.run_uavs()
        self.run_sensors()
        self.run_base_stations()
        self.run_agent()

    def render(self) -> None:
        pass

    def num_of_generated_packets(self) -> int:
        return int(np.sum(sensor.num_of_collected_packets for sensor in self.sensors))

    def num_of_received_packets(self) -> int:
        return int(np.sum(base_station.num_of_collected_packets for base_station in self.base_stations))

    def calculate_pdr(self) -> float:
        if self.num_of_generated_packets() == 0:
            return 0
        return self.num_of_received_packets() / self.num_of_generated_packets()

    def reset(self) -> None:
        logging.info(f'reset environment to initial state')
        self.time_step = 0
        self.data_loss = 0
        self.sensors_data_transitions.clear()
        self.base_stations_data_transitions.clear()
        self.uavs = deepcopy(self.initial_state.uavs)
        self.sensors = deepcopy(self.initial_state.sensors)
        self.base_stations = deepcopy(self.initial_state.base_stations)

    def get_neighbouring_uavs(self, uav_index):
        other_uavs = self.uavs[:, uav_index] + self.uavs[uav_index + 1, :]
        neighbours = []
        for uav in other_uavs:
            if self.uavs[uav_index].in_range(uav):
                np.append(neighbours, [uav])
        return neighbours

    def data_collection_state(self, uav_index: int) -> (UAV, List[UAV], Dict[int, List[DataTransition]]):
        return self.uavs[uav_index], self.get_neighbouring_uavs(uav_index), self.sensors_data_transitions

    def get_sensors_in_range(self, uav: UAV) -> List[Sensor]:
        neighbours = []
        for sensor in self.sensors:
            if uav.in_range(sensor):
                np.append(neighbours, [sensor])
        return neighbours

    def add_sensor_transition(self, transition: DataTransition) -> None:
        self.sensors_data_transitions[self.time_step].append(transition)

    def collect_data(self, uav: UAV) -> None:
        sensors_in_range = self.get_sensors_in_range(uav)
        area_index = self.get_area_index(uav)
        collection_rate = uav.areas_collection_rates[area_index]
        for sensor in sensors_in_range:
            data_transition = uav.receive_data(sensor, collection_rate)
            self.add_sensor_transition(data_transition)
            self.data_loss += data_transition.data_loss
            uav.areas_collection_rates[area_index] = max(0, collection_rate - data_transition.size)
            if uav.areas_collection_rates[area_index] == 0:
                break

    @staticmethod
    def adjust_collection_rate(uav: UAV, area: int, rate: int) -> None:
        uav.areas_collection_rates[area] = rate

    def get_results(self):
        logging.info(f'the experiment took: {self.time_step}')
        logging.info(f'{len(self.sensors)} sensor')
        logging.info(f'{len(self.uavs)} mobile sink')
        logging.info(f'{len(self.base_stations)} base station')
        logging.info(f'pdr: {self.calculate_pdr()}')
        for mobile_sink in self.uavs:
            logging.info(f'{mobile_sink} energy: {mobile_sink.energy}')
        for transition in self.sensors_data_transitions:
            logging.info(f'{transition}')
        for transition in self.base_stations_data_transitions:
            logging.info(f'{transition}')

    def choose_collection_area(self):
        pass

    def bfs(self):
        pass

    def calculate_sensors_heatmap(self) -> list:
        maximum_value = max(sensor.num_of_collected_packets for sensor in self.sensors)
        minimum_value = min(sensor.num_of_collected_packets for sensor in self.sensors)
        value_range = maximum_value - minimum_value
        heatmap = []
        for sensor in self.sensors:
            heatmap.append(sensor.num_of_collected_packets / value_range)
        return heatmap

    def calculate_sensors_data_fairness(self) -> float:
        maximum_value = max(sensor.num_of_collected_packets for sensor in self.sensors)
        minimum_value = min(sensor.num_of_collected_packets for sensor in self.sensors)
        median = (maximum_value - minimum_value) / 2
        average = sum(sensor.num_of_collected_packets for sensor in self.sensors) / len(self.sensors)
        return abs(average - median)

    def get_heatmap_history(self):
        pass

    def calculate_data_transitions_variance(self) -> float:
        pass

    def calculate_data_transition_deviation(self) -> float:
        return self.calculate_data_transitions_variance() ** 0.5

    def get_neighbours(self, mobile_sink: UAV):
        pass
