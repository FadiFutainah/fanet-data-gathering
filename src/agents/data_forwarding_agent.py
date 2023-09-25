import math

import tensorflow as tf

from dataclasses import dataclass, field
import random
from typing import List, Any

import numpy as np

from src.environment.devices.base_station import BaseStation
from src.environment.devices.uav import UAV, UAVTask
from src.environment.simulation_models.memory.data_packet import DataPacket


@dataclass
class ForwardingRewardObject:
    time_sent: int
    packets_sent: List[DataPacket]
    delay_time: int = 0
    num_of_packets_received: int = 0
    energy_consumed: int = 0

    def get_delay_penalty(self, delay: float) -> float:
        return 1 / (1 + math.exp(-self.k * (delay - self.max_delay)))

    def get_energy_penalty(self, energy: float) -> float:
        return 1 / (1 + math.exp(-self.k * (energy - self.max_energy)))

    def get_pdr_reward(self, pdr: float):
        return self.beta * pdr


@dataclass
class DataForwardingState:
    uav: UAV
    uavs: List[UAV]
    neighbouring_uavs: List[UAV]
    base_stations: List[BaseStation]
    neighbouring_base_stations: List[BaseStation]

    def get(self):
        state = []
        uav_positions = []
        base_stations = []
        for uav in self.uavs:
            if uav in self.neighbouring_uavs:
                uav_positions.append(uav.current_way_point)
            else:
                uav_positions.append(-1)
        for base_station in self.base_stations:
            if base_station in self.neighbouring_uavs:
                base_stations.append(base_station.id)
            else:
                base_stations.append(-1)
        state.append(self.uav.current_way_point)
        state.extend(uav_positions)
        state.extend(base_stations)
        state.append(self.uav.consumed_energy)
        state.append(self.uav.num_of_collected_packets)
        state.append(self.uav.get_occupancy_percentage())
        return state


@dataclass
class DataForwardingAgent:
    action_size: int
    uav: UAV
    steps: int = field(init=False, default=0)
    episodes_rewards: List = field(init=False, default_factory=list)
    forward_targets: list = field(init=False, default_factory=list)
    episode_experiences: list = field(init=False, default_factory=list)
    model: Any = field(init=False)
    target_model: Any = field(init=False)
    memory: list = field(init=False, default_factory=list)
    epsilon: float
    epsilon_min: float
    epsilon_max: float
    epsilon_decay: float
    target_update_freq: int
    checkpoint_freq: int
    checkpoint_path: str
    gamma: float
    batch_size: int
    state_dim: int
    current_reward: float = 0
    wins: int = 0
    episode_return: int = 0
    reward_object: ForwardingRewardObject = None
    current_state: DataForwardingState = None
    action: int = -1
    reward: int = 0

    def __post_init__(self):
        self.model = self.create_model()
        self.target_model = tf.keras.models.clone_model(self.model)

    def create_model(self):
        num_units = 24
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.Dense(num_units, input_dim=self.state_dim, activation='relu'))
        model.add(tf.keras.layers.Dense(num_units, activation='relu'))
        model.add(tf.keras.layers.Dense(self.action_size))
        model.compile(loss='mse', optimizer=tf.keras.optimizers.Adam())
        return model

    def initialize_for_episode(self, uav: UAV) -> None:
        self.steps = 0
        self.episode_return = 0
        self.uav = uav
        self.episode_experiences.clear()

    def update_episode_return(self):
        self.episode_return += self.current_reward

    def get_current_state(self, uavs_in_range: list, uavs: list, base_stations: list, neighbouring_base_stations: list):
        return DataForwardingState(uav=self.uav, neighbouring_uavs=uavs_in_range, uavs=uavs,
                                   neighbouring_base_stations=neighbouring_base_stations, base_stations=base_stations)

    def update_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def update_reward(self, reward):
        self.reward = reward
        self.episode_return += reward

    def add_experience(self):
        # the shape of experience is (s[i], a[i], r, s[i+1])
        # the shape of reward is (num_of_packets_sent, num_of_packets_received, time_sent, time_received)
        experience = (self.current_state.get(), self.action, self.reward_object, None)
        self.episode_experiences.append(experience)
        length = len(self.episode_experiences)
        if length > 1:
            self.episode_experiences[length - 2][3] = self.current_state.get()
        # self.memory.append(experience)

    def remember(self, experience):
        self.memory.append(experience)

    def has_forward_task(self) -> bool:
        return self.uav.is_active(UAVTask.FORWARD)

    def has_receiving_task(self) -> bool:
        return self.uav.is_active(UAVTask.RECEIVE)

    def is_busy(self) -> bool:
        return self.has_forward_task() or self.has_receiving_task() or self.uav.steps_to_move > 0

    def update_target_network(self):
        if self.steps % self.target_update_freq == 0:
            self.target_model.set_weights(self.model.get_weights())

    def save_weights(self, episode: int):
        if self.steps % self.checkpoint_freq == 0:
            self.model.save_weights("{}/weights-{:08d}-{:08d}".format(
                self.checkpoint_path, episode, self.steps))

    def replay(self):
        if len(self.memory) > self.batch_size:
            experience_sample = random.sample(self.memory, self.batch_size)
            x = np.array([e[0] for e in experience_sample])
            y = self.model.predict(x, verbose=0)
            x2 = np.array([e[3] for e in experience_sample])
            q2 = self.gamma * np.max(self.target_model.predict(x2, verbose=0), axis=1)
            for i, (s, a, r, s2) in enumerate(experience_sample):
                y[i][a] = r + q2[i]
            self.model.fit(x, y, batch_size=self.batch_size, epochs=1, verbose=0)
            for layer in self.model.layers:
                for weight in layer.weights:
                    weight_name = weight.name.replace(':', '_')
                    tf.summary.histogram(weight_name, weight, step=self.steps)
