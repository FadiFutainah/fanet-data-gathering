import random

import matplotlib
import matplotlib.pyplot as plt

from environment.devices.mobile_sink import MobileSink
from environment.devices.sensor import Sensor
from environment.environment import Environment


class PlotEnvironment(Environment):
    def __init__(self, sensors: list, mobile_sinks: list, base_stations: list, height: float, width: float):
        super().__init__(sensors, mobile_sinks, base_stations, height, width)
        self.colors = ['b', 'g', 'c', 'm', 'y']
        matplotlib.use('TkAgg')
        self.fig, self.ax = plt.subplots()

    @staticmethod
    def get_sensor_color(sensor: Sensor) -> str:
        if sensor.is_empty():
            return 'darkgray'
        return 'red'

    def draw_devices(self, devices: list, shape: str, size: int, colors: list, alpha: float = 1) -> None:
        xs = [device.position.x for device in devices]
        ys = [device.position.y for device in devices]
        self.ax.scatter(list(xs), list(ys), s=[size] * len(devices), c=colors, alpha=alpha, marker=shape)

    def draw_items(self, items: list, shape, size: int) -> None:
        xs = [item.x for item in items]
        ys = [item.y for item in items]
        self.ax.plot(list(xs), list(ys), shape, markersize=size)

    def draw_circle(self, mobile_sink: MobileSink, color: str) -> None:
        radius = plt.Circle((mobile_sink.position.x, mobile_sink.position.y), mobile_sink.coverage_radius, color=color,
                            alpha=0.2)
        self.ax.add_patch(radius)

    def random_color(self) -> str:
        return random.choice(self.colors)

    def run(self) -> None:
        for mobile_sink in self.mobile_sinks:
            color = self.random_color()
            self.ax.plot(mobile_sink.position.x, mobile_sink.position.y, color + 'd', markersize=15, alpha=0.7)
            self.draw_items(items=[mobile_sink.position, *mobile_sink.way_points], shape=color + '--o', size=6)
            self.draw_circle(mobile_sink=mobile_sink, color=color)
        sensors_colors = [self.get_sensor_color(sensor=sensor) for sensor in self.sensors]
        base_stations_colors = ['b'] * len(self.base_stations)
        self.draw_devices(devices=self.sensors, shape='.', size=135, alpha=0.6, colors=sensors_colors)
        self.draw_devices(devices=self.base_stations, shape='^', size=450, alpha=0.6, colors=base_stations_colors)

    def render(self) -> None:
        self.run()
        plt.grid()
        plt.show()
