import math
import random
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

from typing import List, Any
from dataclasses import dataclass, field

from src.environment.devices.device import Device
from src.environment.devices.uav import UAV, UAVTask
from src.environment.core.environment import Environment
from src.environment.devices.base_station import BaseStation

from src.rl.data_forwarding.data_forwarding_state import DataForwardingState
from src.rl.data_forwarding.data_forwarding_sample import DataForwardingSample


@dataclass
class DataForwardingAgent:
    action_size: int
    uav: UAV
    steps: int = field(init=False, default=0)
    episodes_rewards: List = field(init=False, default_factory=list)
    samples: List[DataForwardingSample] = field(init=False, default_factory=list)
    model: Any = field(init=False)
    target_model: Any = field(init=False)
    memory: List = field(init=False, default_factory=list)
    epsilon: float
    epsilon_min: float
    epsilon_decay: float
    target_update_freq: int
    checkpoint_freq: int
    checkpoint_path: str
    gamma: float
    batch_size: int
    state_dim: int
    k: float
    beta: float
    max_delay: float
    max_energy: float
    environment: Environment = None
    current_reward: float = 0
    episode_return: int = 0

    def __post_init__(self):
        self.model = self.create_model()
        self.target_model = tf.keras.models.clone_model(self.model)

    def inject_environment_object(self, environment: Environment) -> None:
        if self.environment is not None:
            return
        self.environment = environment

    def get_available_actions(self) -> List[int]:
        forward_targets = self.get_available_targets()
        actions = [-1]
        if type(forward_targets[0]) is BaseStation:
            for base_station in forward_targets:
                actions.append(self.environment.base_stations.index(base_station))
        else:
            for uav in forward_targets:
                actions.append(self.environment.uavs.index(uav) + len(self.environment.base_stations))
        return actions

    def choose_action(self, state):
        if np.random.rand() < self.epsilon:
            actions = self.get_available_actions()
            return random.choice(actions)
        else:
            return np.argmax(self.model.predict(np.array(state.get()), verbose=0)[0])

    def take_forwarding_action(self, action):
        if action == -1:
            return []
        if action < len(self.environment.base_stations):
            target = self.environment.base_stations[action]
        else:
            target = self.environment.uavs[action - len(self.environment.base_stations)]
            target.assign_receiving_data_task()
        assert self.uav.in_range(target), f'{self.uav} must be in range of the {target} {action}'
        self.uav.assign_forward_data_task(data_to_forward=self.uav.memory_model.memory.current_size,
                                          forward_data_target=target)
        return self.uav.memory_model.read_data()

    def create_model(self):
        num_units = 24
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.Dense(num_units, input_dim=self.state_dim, activation='relu'))
        model.add(tf.keras.layers.Dense(num_units, activation='relu'))
        model.add(tf.keras.layers.Dense(self.action_size))
        model.compile(loss='mse', optimizer=tf.keras.optimizers.Adam())
        return model

    def get_available_targets(self) -> list[Device]:
        if not self.uav.memory_model.has_data():
            return []
        base_stations = self.environment.get_in_range(self.uav, device_type=BaseStation)
        if len(base_stations) != 0:
            return base_stations
        return self.environment.get_in_range(self.uav, device_type=UAV)

    def save_reward_as_a_plot(self):
        chunk_size = 1
        y_points = np.array([])
        for chunk in range(len(self.episodes_rewards) // chunk_size):
            avg = np.sum(self.episodes_rewards[chunk * chunk_size: chunk * chunk_size + chunk_size]) / chunk_size
            y_points = np.append(y_points, avg)
        x_points = np.arange(0, len(self.episodes_rewards) // chunk_size)
        plt.plot(x_points, y_points)
        plt.savefig(f'data/output/results-of-agent-{self}-{id(self)}.png')

    def initialize_for_episode(self, uav: UAV) -> None:
        self.uav = uav
        self.steps = 0
        self.episode_return = 0
        self.samples.clear()

    def update_episode_return(self):
        self.episode_return += self.current_reward

    def get_current_state(self, uavs_in_range: list, uavs: list, base_stations: list, neighbouring_base_stations: list):
        return DataForwardingState(uav=self.uav, neighbouring_uavs=uavs_in_range, uavs=uavs,
                                   neighbouring_base_stations=neighbouring_base_stations, base_stations=base_stations)

    def update_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def update_reward(self, reward):
        self.episode_return += reward

    def get_delay_penalty(self, delay: float) -> float:
        return 1 / (1 + math.exp(-self.k * (delay - self.max_delay)))

    def get_energy_penalty(self, energy: float) -> float:
        return 1 / (1 + math.exp(-self.k * (energy - self.max_energy)))

    def get_pdr_reward(self, pdr: float):
        return self.beta * pdr

    def update_samples(self, force_update: bool = False):
        if len(self.samples) > 1:
            self.samples[-2].update_next_state(self.samples[-1].state)
        for sample in self.samples:
            arrived_packets = sample.get_num_of_arrived_packets()
            if force_update or arrived_packets > 0.8 * len(sample.data_packets):
                reward = self.calculate_reward(sample)
                self.episode_return += reward
                sample.update_reward(reward)
                self.remember(sample)
        self.samples = [sample for sample in self.samples if not sample.has_completed()]

    def add_sample(self, sample):
        self.samples.append(sample)

    def remember(self, sample):
        self.memory.append(sample)

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

    def calculate_reward(self, sample: DataForwardingSample) -> float:
        arrived_packets = 0
        end_to_end_delay = 0
        consumed_energy = 0
        for data_packet in sample.data_packets:
            if data_packet.arrival_time == 0:
                continue
            arrived_packets += 1
            end_to_end_delay += data_packet.arrival_time - sample.created_time
        if len(sample.data_packets) == 0:
            pdr = 0
        else:
            pdr = arrived_packets / len(sample.data_packets)
            consumed_energy = self.uav.consumed_energy
        if arrived_packets == 0:
            end_to_end_delay = 0
        else:
            end_to_end_delay /= arrived_packets
        pdr_reward = self.get_pdr_reward(pdr)
        consumed_energy_penalty = self.get_energy_penalty(consumed_energy)
        delay_penalty = self.get_delay_penalty(end_to_end_delay)
        # TODO: add consumed energy penalty to the reward equation
        return pdr_reward - delay_penalty

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

    def step(self, episode: int):
        self.steps += 1
        current_state = self.get_current_state(
            uavs_in_range=self.environment.get_in_range(self.uav, device_type=UAV),
            uavs=self.environment.uavs,
            neighbouring_base_stations=self.environment.get_in_range(self.uav, device_type=BaseStation),
            base_stations=self.environment.base_stations)
        action = self.choose_action(current_state)
        data_packets = self.take_forwarding_action(action)
        sample = DataForwardingSample(created_time=self.environment.time_step, state=current_state,
                                      action=action, data_packets=data_packets)
        self.add_sample(sample)
        self.replay()
        self.update_target_network()
        self.save_weights(episode)
        self.update_samples()
