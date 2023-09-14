from copy import copy

import tensorflow as tf

from dataclasses import dataclass, field
import random

from typing import List, Any

import numpy as np

from src.environment.core.environment import Environment
from src.environment.devices.base_station import BaseStation
from src.environment.devices.uav import UAV, UAVTask


@dataclass
class DataForwardingState:
    uav: UAV
    uavs: List[UAV]
    neighbouring_uavs: List[UAV]

    def get(self):
        state = []
        uav_positions = []
        for uav in self.uavs:
            if uav in self.neighbouring_uavs:
                uav_positions.append(uav.current_way_point)
            else:
                uav_positions.append(-1)
        state.append(self.uav.current_way_point)
        state.extend(uav_positions)
        state.append(self.uav.consumed_energy)
        state.append(self.uav.num_of_collected_packets)
        state.append(self.uav.get_occupancy_percentage())
        return [state]


@dataclass
class DataForwardingAgent:
    state_size: int
    action_size: int
    uav: UAV
    env: Environment
    steps: int = field(init=False, default=0)
    episodes_rewards: List = field(init=False, default_factory=list)
    max_delay: float
    max_energy: float
    beta: float
    gamma_e: float
    """ represents the maximum penalty for exceeding the max_energy """
    lambda_d: float
    """ represents the maximum penalty for exceeding the max_delay """
    k: float
    """ describes the steepness of the sigmoid function """
    forward_targets: list = field(init=False, default_factory=list)
    model: Any
    current_reward: float
    memory: list
    wins: int = 0
    episode_return: int = 0
    last_state: DataForwardingState = None
    current_state: DataForwardingState = None
    action: int = -1
    reward: int = 0

    def initialize_for_episode(self):
        self.steps = 0
        self.episode_return = 0

    def update_episode_return(self):
        self.episode_return += self.current_reward

    def get_current_state(self, uavs_in_range: list, uavs: list):
        return DataForwardingState(self.uav, uavs_in_range, uavs)

    def get_available_actions(self) -> List[int]:
        if self.forward_targets[0] is BaseStation:
            actions = [i for i in range(len(self.forward_targets))]
        else:
            actions = [self.action_size - 1 - i for i in range(len(self.forward_targets))]
        return actions

    def get_current_action(self):
        if np.random.rand() < self.epsilon:
            actions = self.get_available_actions()
            return random.choice(actions)
        else:
            return np.argmax(self.model.predict(np.array([self.current_state]), verbose=0)[0])

    def update_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def update_reward(self, reward):
        self.reward = reward
        self.episode_return += reward

    def update_experience(self):
        if self.last_state is None:
            self.last_state = self.current_state
            return
        if self.reward is None:
            return
        experience = (self.last_state, self.action, self.reward, self.current_state)
        self.memory.append(experience)

    def update_epsilon(self):
        pass

    def has_forward_task(self) -> bool:
        return self.uav.is_active(UAVTask.FORWARD)

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
            Q2 = self.gamma * np.max(self.target_model.predict(x2, verbose=0), axis=1)
            for i, (s, a, r, s2) in enumerate(experience_sample):
                # y[i][a] = r
                y[i][a] = r + Q2[i]
            self.model.fit(x, y, batch_size=self.batch_size, epochs=1, verbose=0)
            for layer in self.model.layers:
                for weight in layer.weights:
                    weight_name = weight.name.replace(':', '_')
                    tf.summary.histogram(weight_name, weight, step=self.steps)

    def step(self, action: int, index: int):
        uav = self.env.uavs[index]
        if action.type == 0:
            target = self.env.base_stations[action]
        else:
            target = self.env.uavs[action]
        uav.forward_data_target = target
        self.env.run()
        return self.get_current_state(index), self.get_reward(index), self.env.has_ended()
