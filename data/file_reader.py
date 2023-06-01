import os

import pandas as pd
from pandas import DataFrame

from environment.devices.base_stations import BaseStation
from environment.devices.mobile_sink import MobileSink
from environment.devices.sensor import Sensor
from environment.environment import Environment
from environment.utils.data_transition import DataTransition
from environment.utils.position import Position


# TODO: rename to FileManager
# TODO: some refactor
class FileReader:
    def __init__(self, path: str) -> None:
        self.path = path

    def read_csv_data(self, path) -> DataFrame:
        return pd.read_csv(self.path + path)

    @staticmethod
    def get_episode_data_frame(environment: Environment) -> DataFrame:
        data = {
            'time steps': [environment.time_step],
            'number of sensors': [len(environment.sensors)],
            'number of mobile sinks': [len(environment.mobile_sinks)],
            'number of base stations': [len(environment.base_stations)],
            'data left': [environment.data_left],
            'data received': [environment.data_received],
            'PDR': [environment.calculate_pdr()],
        }
        return pd.DataFrame(data)

    @staticmethod
    def get_mobile_sinks_data_frame(mobile_sinks: list) -> DataFrame:
        data = {
            'energy left': [e.energy for e in mobile_sinks],
            'coverage radius': [e.coverage_radius for e in mobile_sinks],
            'collected data size': [e.collected_data_size for e in mobile_sinks],
            'memory size': [e.memory_size for e in mobile_sinks],
        }
        return pd.DataFrame(data)

    @staticmethod
    def get_sensors_data_frame(sensors: list) -> DataFrame:
        data = {
            'collected data size': [e.collected_data_size for e in sensors],
            'memory size': [e.memory_size for e in sensors],
        }
        return pd.DataFrame(data)

    @staticmethod
    def get_base_stations_data_frame(base_stations: list) -> DataFrame:
        data = {
            'collected data size': [e.collected_data_size for e in base_stations],
            'memory size': [e.memory_size for e in base_stations],
        }
        return pd.DataFrame(data)

    @staticmethod
    def get_data_transitions_data_frame(data_transitions: list) -> DataFrame:
        data = {
            'data size': [e.data_size for e in data_transitions],
            'source': [str(e.source) for e in data_transitions],
            'destination': [str(e.destination) for e in data_transitions],
            'created time (time step)': [e.created_time for e in data_transitions],
        }
        return pd.DataFrame(data)

    def write_episode_data(self, environment: Environment) -> None:
        # csv_data = pd.read_csv('output/episodes.csv')
        current_data = self.get_episode_data_frame(environment)
        # combined_data = pd.concat([csv_data, current_data])
        current_data.to_csv('output/episodes.csv')

    def write_data_on_csv(self, environment: Environment) -> None:
        self.write_episode_data(environment)
        self.get_mobile_sinks_data_frame(environment.mobile_sinks).to_csv('output/mobile_sinks.csv')
        self.get_sensors_data_frame(environment.sensors).to_csv('output/sensors.csv')
        self.get_data_transitions_data_frame(environment.data_transitions).to_csv('output/data_transitions.csv')
        self.get_base_stations_data_frame(environment.base_stations).to_csv('output/base_stations.csv')

    def load_sensors(self) -> list:
        sensors = []
        data = self.read_csv_data(path='sensors/sensors.csv')
        for index, row in data.iterrows():
            sensor = Sensor(id=int(str(index)), position=Position(x=row['x'], y=row['y']))
            sensors.append(sensor)
        return sensors

    def load_base_stations(self) -> list:
        base_stations = []
        data = self.read_csv_data(path='base_stations/base_stations.csv')
        for index, row in data.iterrows():
            base_station = BaseStation(id=int(str(index)), position=Position(x=row['x'], y=row['y']))
            base_stations.append(base_station)
        return base_stations

    def load_mobile_sinks(self, solution_id: int) -> list:
        mobile_sinks = []
        directory = self.path + 'solutions/solution-' + str(solution_id) + '/'
        for i, file in enumerate(os.listdir(directory)):
            data = pd.read_csv(directory + file)
            way_points = []
            for index, row in data.iterrows():
                if row['x'] == -1 or row['y'] == -1:
                    continue
                way_points.append(Position(x=row['x'], y=row['y']))
            if len(way_points) == 0:
                continue
            mobile_sink = MobileSink(id=i + 1, position=way_points[0], way_points=way_points[1:])
            mobile_sinks.append(mobile_sink)
        return mobile_sinks

    def load_environment(self, solution_id: int, environment, height: int = 1000, width: int = 1000) -> Environment:
        sensors = self.load_sensors()
        mobile_sinks = self.load_mobile_sinks(solution_id=solution_id)
        base_stations = self.load_base_stations()
        return environment(sensors=sensors, mobile_sinks=mobile_sinks, base_stations=base_stations, height=height,
                           width=width)
