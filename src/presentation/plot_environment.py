import random
import logging
from typing import List, Any
from dataclasses import dataclass, field

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from src.environment.devices.uav import UAV
from src.environment.utils.vector import Vector
from src.environment.devices.sensor import Sensor
from src.environment.devices.device import Device
from src.environment.core.environment import Environment


def get_random_color():
    return random.choice(['g', 'c', 'm', 'y'])


@dataclass
class UAVRenderObject:
    position: Any = None
    range: Any = None
    color: str = field(init=False, default_factory=get_random_color)

    def update(self, position: Vector, range: int) -> None:
        self.position = position
        self.range = range


@dataclass
class PlotEnvironment:
    env: Environment
    ani: Any = field(init=False)
    uav_render_object_list: List = field(init=False)
    sensors_render_objects: Any = field(init=False)
    way_points_render_objects: Any = field(init=False)
    base_stations_render_objects: Any = field(init=False)

    def __post_init__(self) -> None:
        matplotlib.use('TkAgg')
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.init_plot()
        self.uav_render_object_list = []
        for _ in self.env.uavs:
            self.uav_render_object_list.append(UAVRenderObject())

    def init_plot(self) -> None:
        plt.xlim(-50, self.env.land_width + 50)
        plt.ylim(-50, self.env.land_height + 50)
        plt.grid()

    @staticmethod
    def save_on_file(name: str) -> None:
        plt.savefig(name + '.png')

    @staticmethod
    def get_sensor_color(sensor: Sensor) -> str:
        if sensor.get_current_data_size() != 0:
            return 'red'
        return 'darkgray'

    def draw_devices(self, devices: List[Device], shape: str, size: int, colors: List[str], alpha: float = 1):
        xs = [device.position.x for device in devices]
        ys = [device.position.y for device in devices]
        return self.ax.scatter(xs, ys, s=[size] * len(devices), c=colors, alpha=alpha, marker=shape)

    def draw_sensors(self):
        sensors_colors = [self.get_sensor_color(sensor=sensor) for sensor in self.env.sensors]
        return self.draw_devices(devices=self.env.sensors, shape='.', size=135, alpha=0.7, colors=sensors_colors)

    def draw_base_stations(self):
        base_stations_colors = ['b'] * len(self.env.base_stations)
        return self.draw_devices(devices=self.env.base_stations, shape='^', size=600, alpha=0.4,
                                 colors=base_stations_colors)

    def draw_uav(self, uav: UAV, index: int) -> None:
        render_object = self.uav_render_object_list[index]
        p, = self.ax.plot(uav.position.x, uav.position.y, render_object.color + 'd', markersize=15, alpha=0.7)
        c = self.draw_circle(uav=uav, color=render_object.color)
        self.uav_render_object_list[index].update(position=p, range=c)
        self.way_points_render_objects = self.draw_items(items=uav.way_points, shape=render_object.color + '--o',
                                                         size=6)

    def draw_items(self, items: list, shape, size: int) -> Any:
        xs = [item.x for item in items]
        ys = [item.y for item in items]
        return self.ax.plot(xs, ys, shape, markersize=size)

    def draw_circle(self, uav: UAV, color: str):
        radius = plt.Circle((uav.position.x, uav.position.y), uav.network_model.coverage_radius, color=color, alpha=0.2)
        return self.ax.add_patch(radius)

    def draw_all(self) -> None:
        for index, uav in enumerate(self.env.uavs):
            self.draw_uav(uav, index)
        self.sensors_render_objects = self.draw_sensors()
        self.base_stations_render_objects = self.draw_base_stations()

    def remove_all(self) -> None:
        self.sensors_render_objects.remove()
        self.base_stations_render_objects.remove()
        for line in self.way_points_render_objects:
            line.remove()
        for i in range(len(self.env.uavs)):
            self.uav_render_object_list[i].range.remove()
            self.uav_render_object_list[i].position.remove()

    def render(self, i) -> None:
        if self.env.time_step > 0:
            self.remove_all()
        if self.env.has_ended():
            # logging.info(f'ended at time step {i}')
            self.ani.event_source.stop()
            plt.close()
        self.draw_all()
        self.env.step()

    def run(self) -> None:
        self.ani = FuncAnimation(self.fig, self.render, frames=300, repeat=False, interval=700)
        plt.show()
