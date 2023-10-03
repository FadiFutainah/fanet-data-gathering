import random
import math

import numpy as np

from dataclasses import dataclass, field
from typing import List

from src.agents.data_collecting_agent import DataCollectingAgent
from src.agents.data_forwarding_agent import DataForwardingAgent, DataForwardingActionObject, DataForwardingState
from src.environment.core.environment import Environment
from src.environment.devices.base_station import BaseStation
from src.environment.devices.device import Device
from src.environment.devices.uav import UAV


@dataclass
class DataForwardingAgentsController:
    environment: Environment
    forwarding_agents: List[DataForwardingAgent]
    collecting_agents: List[DataCollectingAgent]
    num_of_episodes: int
    max_steps: int
    k: float
    max_energy: float
    beta: float
    max_delay: float
    active_forwarding_agents: List[DataForwardingAgent] = field(init=False, default_factory=list)
    # active_collecting_agents: list[DataCollectingAgent] = field(init=False, default_factory=list)

    def get_available_targets(self, agent) -> list[Device]:
        # if not agent.uav.is_active(UAVTask.FORWARD) or not agent.uav.memory_model.has_data():
        if not agent.uav.memory_model.has_data():
            return []
        base_stations = self.environment.get_in_range(agent.uav, device_type=BaseStation)
        if len(base_stations) != 0:
            return base_stations
        return self.environment.get_in_range(agent.uav, device_type=UAV)

    def get_available_forwarding_agents(self):
        available_agents = []
        for agent in self.forwarding_agents:
            if agent.is_busy():
                continue
            agent.forward_targets = self.get_available_targets(agent)
            if len(agent.forward_targets) > 0:
                available_agents.append(agent)
        return available_agents

    def take_forwarding_action(self, agent):
        if agent.action < len(self.environment.base_stations):
            target = self.environment.base_stations[agent.action]
        else:
            target = self.environment.uavs[agent.action - len(self.environment.base_stations)]
            target.assign_receiving_data_task()
        assert agent.uav.in_range(target), f'{agent.uav} must be in range of the {target} {agent.action}'
        agent.uav.assign_forward_data_task(data_to_forward=agent.uav.memory_model.memory.current_size,
                                           forward_data_target=target)
        agent.reward_object = DataForwardingActionObject(time_sent=self.environment.time_step,
                                                         packets_sent=agent.uav.memory_model.read_data())
        self.active_forwarding_agents.append(agent)

    def get_delay_penalty(self, delay: float) -> float:
        return 1 / (1 + math.exp(-self.k * (delay - self.max_delay)))

    def get_energy_penalty(self, energy: float) -> float:
        return 1 / (1 + math.exp(-self.k * (energy - self.max_energy)))

    def get_pdr_reward(self, pdr: float):
        return self.beta * pdr

    # def get_data_variance(self, uav: UAV):
    #     return self.environment.get_data_way_points_variance(uav)

    def get_packet_received_time(self, packet):
        for base_station in self.environment.base_stations:
            time_received = base_station.get_packet_received_time(packet)
            if time_received is not None:
                return time_received
        return -1

    def update_agents_rewards(self):
        for agent in self.forwarding_agents:
            if len(agent.episode_experiences) == 0:
                continue
            agent.episode_experiences[len(agent.episode_experiences) - 1][3] = DataForwardingState.get_empty_state()
            for experience in agent.episode_experiences:
                reward_object = experience[2]
                for packet in reward_object.packets_sent:
                    time_received = self.get_packet_received_time(packet)
                    if time_received != -1:
                        reward_object.num_of_packets_received += 1
                        reward_object.delay_time += time_received - reward_object.time_sent
                # experience[2] = reward_object.calculate_value()
                if len(reward_object.packets_sent) == 0:
                    pdr = 0
                else:
                    pdr = reward_object.num_of_packets_received / len(reward_object.packets_sent)
                # consumed_energy = agent.uav.consumed_energy
                if reward_object.num_of_packets_received == 0:
                    end_to_end_delay = 0
                else:
                    end_to_end_delay = reward_object.delay_time / reward_object.num_of_packets_received
                pdr_reward = self.get_pdr_reward(pdr)
                # consumed_energy_penalty = self.get_energy_penalty(consumed_energy)
                delay_penalty = self.get_delay_penalty(end_to_end_delay)
                agent.current_reward = pdr_reward - delay_penalty
                experience[2] = agent.current_reward

    def get_available_collecting_agents(self) -> List:
        return [agent for agent in self.collecting_agents if agent.need_collecting_task()]

    def get_available_actions(self, agent) -> List[int]:
        actions = []
        if type(agent.forward_targets[0]) is BaseStation:
            for base_station in agent.forward_targets:
                actions.append(self.environment.base_stations.index(base_station))
        else:
            for uav in agent.forward_targets:
                actions.append(self.environment.uavs.index(uav) + len(self.environment.base_stations))
        # print(agent.uav, actions)
        return actions

    def get_current_action(self, agent):
        if np.random.rand() < agent.epsilon:
            actions = self.get_available_actions(agent)
            return random.choice(actions)
        else:
            return np.argmax(agent.model.predict(np.array(agent.current_state.get()), verbose=0)[0])

    def run_multi_agents(self):
        for episode in range(self.num_of_episodes):
            self.environment.reset()
            for uav, agent in zip(self.environment.uavs, self.forwarding_agents):
                agent.initialize_for_episode(uav)
            for uav, agent in zip(self.environment.uavs, self.collecting_agents):
                agent.initialize_for_episode(uav)
            # for agent in self.collecting_agents:
            #     agent.initialize_for_episode()
            steps = 0
            while not self.environment.has_ended() and steps <= self.max_steps:
                steps += 1
                print('\r> DQN: Episode {} / {}, step: {} / {}'.format(episode + 1, self.num_of_episodes, steps,
                                                                       self.max_steps), end='')
                # self.update_agents_rewards()
                self.environment.step()
                forwarding_agents = self.get_available_forwarding_agents()
                collecting_agents = self.get_available_collecting_agents()
                for agent in collecting_agents:
                    agent.take_random_collecting_action()
                for agent in forwarding_agents:
                    agent.steps += 1
                    agent.current_state = agent.get_current_state(
                        uavs_in_range=self.environment.get_in_range(agent.uav, device_type=UAV),
                        uavs=self.environment.uavs,
                        neighbouring_base_stations=self.environment.get_in_range(agent.uav, device_type=BaseStation),
                        base_stations=self.environment.base_stations)
                    agent.action = self.get_current_action(agent)
                    self.take_forwarding_action(agent)
                    agent.add_experience()
                # for agent in forwarding_agents:
                #     agent.replay()
                #     agent.update_target_network()
                #     agent.save_weights(episode)
            self.update_agents_rewards()
            for agent in self.forwarding_agents:
                agent.update_epsilon()
            #     agent.episodes_rewards.append(agent.episode_return)
            for agent in self.forwarding_agents:
                for experience in agent.episode_experiences:
                    agent.remember(experience)
                    agent.replay()
                    agent.update_target_network()
                    # agent.save_weights(episode)
                    agent.episodes_rewards.append(experience[2])
        for agent in self.forwarding_agents:
            agent.save_reward_as_a_plot()
