from dataclasses import dataclass, field
from typing import List, Any

import matplotlib
import matplotlib.pyplot as plt

from environment.devices.device import Device
from environment.devices.uav import UAV
from environment.devices.sensor import Sensor
from environment.core.environment import Environment
from environment.plot.uav_render_object import UavRenderObject


@dataclass
class PlotEnvironment:
    env: Environment
    uav_render_object_list: List = field(init=False)
    sensors_render_objects: Any = field(init=False)

    def __post_init__(self) -> None:
        matplotlib.use('TkAgg')
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.init_plot()
        self.uav_render_object_list = []
        for _ in self.env.uavs:
            self.uav_render_object_list.append(UavRenderObject())

    def init_plot(self) -> None:
        plt.xlim(-50, self.env.land_width + 50)
        plt.ylim(-50, self.env.land_height + 50)

    @staticmethod
    def save_on_file(name: str) -> None:
        plt.savefig(name + '.png')

    @staticmethod
    def get_sensor_color(sensor: Sensor) -> str:
        if sensor.memory.has_data():
            return 'red'
        return 'darkgray'

    def draw_devices(self, devices: List[Device], shape: str, size: int, colors: List[str], alpha: float = 1):
        xs = [device.position.x for device in devices]
        ys = [device.position.y for device in devices]
        return self.ax.scatter(xs, ys, s=[size] * len(devices), c=colors, alpha=alpha, marker=shape)

    def draw_sensors(self):
        sensors_colors = [self.get_sensor_color(sensor=sensor) for sensor in self.env.sensors]
        return self.draw_devices(devices=self.env.sensors, shape='.', size=135, alpha=0.6, colors=sensors_colors)

    def draw_base_stations(self):
        base_stations_colors = ['b'] * len(self.env.base_stations)
        self.draw_devices(devices=self.env.base_stations, shape='^', size=600, alpha=0.4, colors=base_stations_colors)

    def draw_uav(self, uav: UAV, index: int) -> None:
        render_object = self.uav_render_object_list[index]
        p, = self.ax.plot(uav.position.x, uav.position.y, render_object.color + 'd', markersize=15, alpha=0.7)
        c = self.draw_circle(uav=uav, color=render_object.color)
        self.uav_render_object_list[index].update(position=p, range=c)
        self.draw_items(items=[uav.position, *uav.way_points], shape=render_object.color + '--o', size=6)

    def remove_sensors(self):
        self.sensors_render_objects.remove()

    def draw_items(self, items: list, shape, size: int) -> None:
        xs = [item.x for item in items]
        ys = [item.y for item in items]
        self.ax.plot(xs, ys, shape, markersize=size)

    def draw_circle(self, uav: UAV, color: str):
        radius = plt.Circle((uav.position.x, uav.position.y), uav.network.coverage_radius, color=color, alpha=0.2)
        return self.ax.add_patch(radius)

    def draw_all(self) -> None:
        for index, uav in enumerate(self.env.uavs):
            self.draw_uav(uav, index)
        self.sensors_render_objects = self.draw_sensors()
        self.draw_base_stations()

    def remove_all(self) -> None:
        self.remove_sensors()
        for i in range(len(self.env.uavs)):
            self.uav_render_object_list[i].range.remove()
            self.uav_render_object_list[i].position.remove()

    def render(self) -> None:
        self.draw_all()
        plt.grid()
        plt.show()
        self.remove_all()
