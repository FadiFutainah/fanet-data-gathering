import random

from environment.devices.mobile_sink import MobileSink
from environment.environment import Environment
import matplotlib.pyplot as plt


class PlotEnvironment(Environment):
    def __init__(self, sensors: list, mobile_sinks: list, base_stations: list, height: float, width: float):
        super().__init__(sensors, mobile_sinks, base_stations, height, width)
        self.colors = ['b', 'g', 'c', 'm', 'y']
        self.fig, self.ax = plt.subplots()

    def draw_devices(self, devices: list, shape: str, size: int, alpha: float = 1) -> None:
        xs = map(lambda device: device.position.x, devices)
        ys = map(lambda device: device.position.y, devices)
        self.ax.plot(list(xs), list(ys), shape, markersize=size, alpha=alpha)

    def draw_items(self, items: list, shape, size: int):
        xs = map(lambda item: item.x, items)
        ys = map(lambda item: item.y, items)
        self.ax.plot(list(xs), list(ys), shape, markersize=size)

    def draw_mobile_sink_rvps(self, mobile_sink: MobileSink, color: str, shape: str):
        for rvp in mobile_sink.rvps:
            self.ax.plot([mobile_sink.position.x, rvp.x], [mobile_sink.position.y, rvp.y], color + shape)

    def draw_circle(self, mobile_sink: MobileSink, color: str):
        radius = plt.Circle((mobile_sink.position.x, mobile_sink.position.y), mobile_sink.coverage_radius, color=color,
                            alpha=0.4)
        self.ax.add_patch(radius)

    def random_color(self) -> str:
        return random.choice(self.colors)

    def run(self, name: str) -> None:
        # props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        # self.ax.text(0.05, 0.95, 'sensor.\nUAV.\npath.', transform=self.ax.transAxes, fontsize=11,
        #              verticalalignment='top', bbox=props)
        for mobile_sink in self.mobile_sinks:
            color = self.random_color()
            # self.draw_items(items=mobile_sink.rvps, shape=color + '^', size=9)
            # self.draw_mobile_sink_rvps(mobile_sink=mobile_sink, color=color, shape=shape)
            self.ax.plot(mobile_sink.position.x, mobile_sink.position.y, color + '^', markersize=11)
            self.draw_items(items=[mobile_sink.position, *mobile_sink.rvps], shape=color + '--.', size=8)
            self.draw_circle(mobile_sink=mobile_sink, color=color)
        self.draw_devices(devices=self.sensors, shape='.r', size=7)
        self.draw_devices(devices=self.base_stations, shape='p', size=20, alpha=0.8)
        plt.grid()
        plt.savefig(name + '.png')
