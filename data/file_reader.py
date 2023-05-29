import os

import pandas as pd

from environment.devices.base_stations import BaseStation
from environment.devices.mobile_sink import MobileSink
from environment.devices.sensor import Sensor
from environment.plot_environment import PlotEnvironment
from environment.utils.position import Position


class FileReader:
    def __init__(self, path: str):
        self.path = path

    def read_csv_data(self, path):
        return pd.read_csv(self.path + path)

    def load_sensors(self) -> list:
        sensors = []
        data = self.read_csv_data(path='sensors/sensors.csv')
        for index, row in data.iterrows():
            sensor = Sensor(id=int(str(index)), position=Position(x=row['x'], y=row['y']))
            sensors.append(sensor)
        return sensors

    def load_base_stations(self):
        base_stations = []
        data = self.read_csv_data(path='base_stations/base_stations.csv')
        for index, row in data.iterrows():
            base_station = BaseStation(id=int(str(index)), position=Position(x=row['x'], y=row['y']))
            base_stations.append(base_station)
        return base_stations

    def load_mobile_sinks(self, solution_id: int) -> list:
        mobile_sinks = []
        directory = self.path + 'solutions/solution-' + str(solution_id) + '/'
        for file in os.listdir(directory):
            data = pd.read_csv(directory + file)
            rvps = []
            for index, row in data.iterrows():
                if row['x'] == -1 or row['y'] == -1:
                    continue
                rvps.append(Position(x=row['x'], y=row['y']))
            if len(rvps) == 0:
                continue
            mobile_sink = MobileSink(id=1, position=rvps[0], rvps=rvps[1:])
            mobile_sinks.append(mobile_sink)
        return mobile_sinks

    def load_environment(self, solution_id: int) -> PlotEnvironment:
        sensors = self.load_sensors()
        mobile_sinks = self.load_mobile_sinks(solution_id=solution_id)
        base_stations = self.load_base_stations()
        height = 1000
        width = 1000
        environment = PlotEnvironment(sensors=sensors, mobile_sinks=mobile_sinks, base_stations=base_stations,
                                      height=height, width=width)
        return environment
