import logging
import random

import matplotlib
import matplotlib.pyplot as plt

from environment.devices.mobile_sink import MobileSink
from environment.devices.sensor import Sensor
from environment.environment import Environment
from environment.plot.mobile_sink_plot import MobileSinkPlot


class PlotEnvironment(Environment):
    def __init__(self, sensors: list, mobile_sinks: list, base_stations: list, height: float, width: float) -> None:
        super().__init__(sensors, mobile_sinks, base_stations, height, width)
        matplotlib.use('TkAgg')
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.colors = ['g', 'c', 'm', 'y']
        self.mobile_sinks_plots = []
        self.sensors_plots = None
        self.init_plot()

    def init_plot(self) -> None:
        plt.xlim(-50, self.width + 50)
        plt.ylim(-50, self.height + 50)

    @staticmethod
    def save_on_file(name: str) -> None:
        plt.savefig(name + '.png')

    @staticmethod
    def get_sensor_color(sensor: Sensor) -> str:
        if sensor.is_empty():
            return 'darkgray'
        return 'red'

    def draw_devices(self, devices: list, shape: str, size: int, colors: list, alpha: float = 1):
        xs = [device.position.x for device in devices]
        ys = [device.position.y for device in devices]
        return self.ax.scatter(xs, ys, s=[size] * len(devices), c=colors, alpha=alpha, marker=shape)

    def draw_sensors(self):
        sensors_colors = [self.get_sensor_color(sensor=sensor) for sensor in self.sensors]
        return self.draw_devices(devices=self.sensors, shape='.', size=135, alpha=0.6, colors=sensors_colors)

    def draw_base_stations(self):
        base_stations_colors = ['b'] * len(self.base_stations)
        self.draw_devices(devices=self.base_stations, shape='^', size=600, alpha=0.4, colors=base_stations_colors)

    def draw_mobile_sink(self, mobile_sink: MobileSink):
        color = random.choice(self.colors)
        p, = self.ax.plot(mobile_sink.position.x, mobile_sink.position.y, color + 'd', markersize=15, alpha=0.7)
        c = self.draw_circle(mobile_sink=mobile_sink, color=color)
        self.mobile_sinks_plots.append(MobileSinkPlot(position=p, range=c, color=color))
        self.draw_items(items=[mobile_sink.position, *mobile_sink.way_points], shape=color + '--o', size=6)

    def remove_sensors(self):
        self.sensors_plots.remove()

    def draw_items(self, items: list, shape, size: int) -> None:
        xs = [item.x for item in items]
        ys = [item.y for item in items]
        self.ax.plot(xs, ys, shape, markersize=size)

    def draw_circle(self, mobile_sink: MobileSink, color: str):
        radius = plt.Circle((mobile_sink.position.x, mobile_sink.position.y), mobile_sink.coverage_radius, color=color,
                            alpha=0.2)
        return self.ax.add_patch(radius)

    def run(self) -> None:
        for mobile_sink in self.mobile_sinks:
            self.draw_mobile_sink(mobile_sink)
        self.sensors_plots = self.draw_sensors()
        self.draw_base_stations()

    def next_time_step(self):
        self.time_step += 1
        logging.info(f'time step {self.time_step}: ')
        plt.pause(interval=0.7)
        for i in range(len(self.mobile_sinks)):
            self.collect_data(self.mobile_sinks[i])
            self.remove_sensors()
            self.sensors_plots = self.draw_sensors()
            self.mobile_sinks_plots[i].range.remove()
            self.mobile_sinks_plots[i].position.remove()
            self.mobile_sinks[i].hop()
            p, = self.ax.plot(self.mobile_sinks[i].position.x, self.mobile_sinks[i].position.y,
                              self.mobile_sinks_plots[i].color + 'd', markersize=15, alpha=0.7)
            c = self.draw_circle(self.mobile_sinks[i], self.mobile_sinks_plots[i].color)
            self.mobile_sinks_plots[i] = MobileSinkPlot(position=p, range=c, color=self.mobile_sinks_plots[i].color)

    def render(self) -> None:
        self.run()
        plt.grid()
        while self.has_moves():
            self.next_time_step()
        self.next_time_step()
        self.transmit_data(self.mobile_sinks[0], self.mobile_sinks[1], self.mobile_sinks[0].collected_data_size)
        for mobile_sink in self.mobile_sinks[1:]:
            self.transmit_data(mobile_sink, self.base_stations[0], mobile_sink.collected_data_size)
        self.initial_state.get_results()
        self.get_results()
        logging.info('the simulation ended')
        # plt.show()
