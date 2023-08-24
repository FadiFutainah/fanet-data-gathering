import logging
from collections import defaultdict
from typing import Dict, List, Tuple

import numpy as np

from copy import deepcopy
from dataclasses import dataclass, field

from src.environment.devices.energy_model import EnergyModel
from src.environment.devices.uav import UAV
from src.environment.devices.sensor import Sensor
from src.environment.devices.base_station import BaseStation
from src.environment.networking.data_transition import DataTransition


@dataclass
class Environment:
    land_width: float
    land_height: float
    energy_model: EnergyModel
    speed_rate: int = field(default=1)
    uavs: List[UAV] = field(default_factory=list)
    sensors: List[Sensor] = field(default_factory=list)
    base_stations: List[BaseStation] = field(default_factory=list)
    run_until: int = 100
    time_step: int = field(init=False, default=0)
    data_loss: int = field(init=False, default=0)
    uav_data_transitions: Dict[int, List[DataTransition]] = field(init=False)
    sensors_data_transitions: Dict[int, List[DataTransition]] = field(init=False)
    base_stations_data_transitions: Dict[int, List[DataTransition]] = field(init=False)

    def __post_init__(self) -> None:
        self.uav_data_transitions = defaultdict(list)
        self.sensors_data_transitions = defaultdict(list)
        self.base_stations_data_transitions = defaultdict(list)
        self.initial_state = deepcopy(self)

    @staticmethod
    def get_area_index(uav: UAV) -> int:
        return uav.current_way_point

    def calculate_e2e_delay(self, uav_index: int) -> float:
        sum_of_delays = 0
        ns = 0
        """ number of received packets """
        uav = self.uavs[uav_index]
        for base_station in self.base_stations:
            received_data = base_station.read_data()
            sum_of_delays = sum(data.get_e2e_delay() for data in received_data if data.uav_id == uav.id)
        return sum_of_delays / ns

    def calculate_overall_consumed_energy(self):
        pass

    def calculate_consumed_energy(self, uav_index: int) -> float:
        return self.uavs[uav_index].energy - self.initial_state.uavs[uav_index].energy

    def run_base_stations(self) -> None:
        for base_station in self.base_stations:
            base_station.run(time=self.time_step)
            base_station.update_data_arrival_time(current_time=self.time_step)

    def run_sensors(self) -> None:
        for sensor in self.sensors:
            sensor.run(time=self.time_step)
            sensor.collect_data(current_time=self.time_step)

    def run_uavs(self) -> None:
        for uav in self.uavs:
            uav.run(time=self.time_step)
            index = self.get_area_index(uav)
            energy = 0
            if uav.forward_data_target is not None:
                data_transition = uav.forward_data()
                energy = self.energy_model.get_collecting_data_energy(data_transition, uav.network.coverage_radius)
            elif uav.areas_collection_rates[index] > 0:
                if not uav.busy:
                    data_transition_list = self.collect_data(uav)
                    for data_transition in data_transition_list:
                        energy += self.energy_model.get_collecting_data_energy(data_transition,
                                                                               uav.network.coverage_radius)
            else:
                if not uav.busy:
                    uav.update_velocity()
                    uav.move_to_next_position()
                # energy = self.energy_model.get_transition_data_energy(uav)
            # print(uav.energy, energy)
            uav.consume_energy(energy)

    def run(self) -> None:
        self.time_step += self.speed_rate
        logging.info(f'time step {self.time_step}:')
        self.run_sensors()
        self.run_uavs()
        self.run_base_stations()

    def has_ended(self) -> bool:
        all_reached = True
        for uav in self.uavs:
            if uav.busy or uav.current_way_point < len(uav.way_points) - 1:
                all_reached = False
                break
        return self.time_step >= self.run_until or all_reached

    def num_of_generated_packets(self) -> int:
        return int(np.sum(sensor.num_of_collected_packets for sensor in self.sensors))

    def num_of_received_packets(self) -> int:
        return int(np.sum(base_station.num_of_collected_packets for base_station in self.base_stations))

    def calculate_pdr(self) -> float:
        if self.num_of_generated_packets() == 0:
            return 0
        return self.num_of_received_packets() / self.num_of_generated_packets()

    def reset(self) -> None:
        logging.info(f'\n== == == == == == ==\n reset environment to initial state\n== == == == == == ==\n')
        self.time_step = 0
        self.data_loss = 0
        self.sensors_data_transitions.clear()
        self.base_stations_data_transitions.clear()
        self.uavs = deepcopy(self.initial_state.uavs)
        self.sensors = deepcopy(self.initial_state.sensors)
        self.base_stations = deepcopy(self.initial_state.base_stations)

    def reset_with_random_data_collection_rates(self):
        self.reset()
        for uav in self.uavs:
            uav.generate_random_data_collection_rates()

    def get_uavs_in_range(self, uav_index) -> List[UAV]:
        neighbours = []
        for i, uav in enumerate(self.uavs):
            if i != uav_index and self.uavs[uav_index].in_range(uav):
                neighbours.append(uav)
        return neighbours

    def get_base_stations_in_range(self, uav_index: int) -> List[BaseStation]:
        uav = self.uavs[uav_index]
        neighbours = []
        for base_station in self.base_stations:
            if uav.in_range(base_station):
                neighbours.append(base_station)
        return neighbours

    def get_sensors_in_range(self, uav: UAV) -> List[Sensor]:
        neighbours = []
        for sensor in self.sensors:
            if uav.in_range(sensor):
                neighbours.append(sensor)
        return neighbours

    def add_sensor_transition(self, transition: DataTransition) -> None:
        self.sensors_data_transitions[self.time_step].append(transition)

    def collect_data(self, uav: UAV) -> List[DataTransition]:
        sensors_in_range = self.get_sensors_in_range(uav)
        area_index = self.get_area_index(uav)
        uav.connect_to_all(sensors_in_range)
        data_transition_list = []
        for sensor in sensors_in_range:
            data_transition = uav.receive_from(sensor, uav.areas_collection_rates[area_index])
            data_transition_list.append(data_transition)
            self.add_sensor_transition(data_transition)
            self.data_loss += data_transition.data_loss
            uav.areas_collection_rates[area_index] -= data_transition.size
            if data_transition.size == 0:
                uav.areas_collection_rates[area_index] = 0
            uav.areas_collection_rates[area_index] = max(0, uav.areas_collection_rates[area_index])
            uav.num_of_collected_packets += data_transition.size
            if uav.areas_collection_rates[area_index] == 0:
                break
        return data_transition_list

    def get_transition_data_energy(self, uav: UAV) -> None:
        pass

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

    def get_collected_data_by_uav(self, uav: UAV) -> List[DataTransition]:
        data = []
        for key, transition_list in self.sensors_data_transitions:
            for transition in transition_list:
                if transition.destination == uav:
                    data.append(transition)
        return data

    def get_sensors_data_collection_heatmap(self) -> Tuple[Dict[Sensor, int], int]:
        heatmap = {}
        total_size = 0
        for key, transition_list in self.sensors_data_transitions:
            for transition in transition_list:
                heatmap[transition.source] = heatmap.get(transition.source, 0) + transition.size
                total_size += transition.size
        return heatmap, total_size

    def calculate_sensors_data_fairness(self) -> float:
        """ calculates the data fairness value, when the value is 0 then the data fairness is perfect """
        data, s = self.get_sensors_data_collection_heatmap()
        n = len(data.keys())
        avg = s / n
        data_fairness = sum(abs(avg - value) for key, value in data)
        return data_fairness
