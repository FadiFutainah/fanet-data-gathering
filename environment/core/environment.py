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
    speed_rate: int = field(default=1)
    uavs: List[UAV] = List[UAV]
    sensors: List[Sensor] = List[Sensor]
    base_stations: List[BaseStation] = List[BaseStation]
    time_step: int = field(init=False, default=0)
    data_loss: int = field(init=False, default=0)
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
        pass

    @staticmethod
    def get_area_index(uav: UAV) -> int:
        return uav.current_way_point

    def calculate_e2e_delay(self, uav_index: int = -1) -> float:
        """
        Parameters
        ----------
        uav_id if uav_index is not passed then the method returns the overall end-to-end delay for all uavs
        Returns the end-to-end delay for the successfully received packets to the base stations
        -------
        """
        sum_of_delays = 0
        ns = 0
        """ number of received packets """
        received_data = []
        uav = self.uavs[uav_index]
        for base_station in self.base_stations:
            received_data.append(base_station.read_data())
        for packet_collection_list in received_data:
            for packet_collection in packet_collection_list:
                if uav.id == -1 or uav.id == packet_collection.uav_id:
                    sum_of_delays = packet_collection.get_e2e_delay()
                    ns += packet_collection.num_of_packets
        return sum_of_delays / ns

    def calculate_consumed_energy(self, uav_index: int = -1) -> float:
        """
        Parameters
        ----------
        uav_id if uav_index is not passed then the method returns the overall consumed energy for all uavs
        Returns the consumed energy in the current time step
        -------
        """
        if uav_index != -1:
            return self.uavs[uav_index].energy - self.initial_state.uavs[uav_index].energy
        consumed_energy = 0
        for start, end in zip(self.initial_state.uavs, self.uavs):
            consumed_energy += end.energy - start.energy
        return consumed_energy

    def run_sensors(self) -> None:
        pass

    def run_base_stations(self) -> None:
        pass

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

    def run(self) -> None:
        self.time_step += self.speed_rate
        logging.info(f'time step {self.time_step}:')
        self.run_uavs()
        self.run_sensors()
        self.run_base_stations()

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
        logging.info(f'\n== == == == == == ==\nreset environment to initial state\n== == == == == == ==\n')
        self.time_step = 0
        self.data_loss = 0
        self.sensors_data_transitions.clear()
        self.base_stations_data_transitions.clear()
        self.uavs = deepcopy(self.initial_state.uavs)
        self.sensors = deepcopy(self.initial_state.sensors)
        self.base_stations = deepcopy(self.initial_state.base_stations)

    def get_neighbouring_uavs(self, uav_index) -> List[UAV]:
        neighbours = []
        for i, uav in enumerate(self.uavs):
            if i != uav_index and self.uavs[uav_index].in_range(uav):
                neighbours.append(uav)
        return neighbours

    def get_sensors_in_range(self, uav: UAV) -> List[Sensor]:
        neighbours = []
        for sensor in self.sensors:
            if uav.in_range(sensor):
                neighbours.append(sensor)
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
