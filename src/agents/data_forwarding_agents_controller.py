import math
from dataclasses import dataclass

from src.agents.data_forwarding_agent import DataForwardingAgent
from src.environment.core.environment import Environment
from src.environment.devices.base_station import BaseStation
from src.environment.devices.device import Device
from src.environment.devices.uav import UAV, UAVTask


@dataclass
class DataForwardingAgentsController:
    environment: Environment
    agents: list[DataForwardingAgent]
    num_of_episodes: int
    max_steps: int
    active_agents: list[DataForwardingAgent]
    k: float
    max_energy: float
    beta: float
    max_delay: float

    def get_available_targets(self, agent) -> list[Device]:
        if not agent.uav.is_active(UAVTask.FORWARD) or not agent.uav.memory_model.has_data():
            return []
        base_stations = self.environment.get_in_range(agent.uav, device_type=BaseStation)
        if len(base_stations) != 0:
            return base_stations
        return self.environment.get_in_range(agent.uav, device_type=UAV)

    def get_available_agents(self):
        available_agents = []
        for agent in self.agents:
            if agent.has_forward_task():
                continue
            agent.forward_targets = self.get_available_targets(agent)
            if len(agent.forward_targets) > 0:
                available_agents.append(agent)
        return available_agents

    def take_action(self, agent):
        if agent.action < len(self.environment.base_stations):
            target = self.environment.base_stations[agent.current_action]
        else:
            target = self.environment.uavs[agent.current_action - len(self.environment.base_stations)]
        agent.uav.assign_forward_data_task(data_to_forward=agent.uav.memory_model.memory.current_size,
                                           forward_data_target=target)
        self.active_agents.append(agent)

    def get_delay_penalty(self, delay: float) -> float:
        return 1 / (1 + math.exp(-self.k * (delay - self.max_delay)))

    def get_energy_penalty(self, energy: float) -> float:
        return 1 / (1 + math.exp(-self.k * (energy - self.max_energy)))

    def get_pdr_reward(self, pdr: float):
        return self.beta * pdr

    def update_agents_rewards(self):
        agents = [agent for agent in self.active_agents if not agent.has_forward_task()]
        for agent in agents:
            self.active_agents.remove(agent)
            pdr = agent.uav.pdr
            consumed_energy = agent.uav.consumed_energy
            end_to_end_delay = agent.uav.end_to_end_delay
            pdr_reward = self.get_pdr_reward(pdr)
            consumed_energy_penalty = self.get_energy_penalty(consumed_energy)
            delay_penalty = self.get_delay_penalty(end_to_end_delay)
            agent.current_reward = pdr_reward - delay_penalty - consumed_energy_penalty

    def run_multi_agents(self):
        for episode in range(self.num_of_episodes):
            self.environment.reset()
            for agent in self.agents:
                agent.initialize_for_episode()
            steps = 0
            while not self.environment.has_ended() and steps <= self.max_steps:
                steps += 1
                self.update_agents_rewards()
                agents = self.get_available_agents()
                for agent in agents:
                    agent.steps += 1
                    agent.current_state = agent.get_current_state(
                        uavs_in_range=self.environment.get_in_range(agent.uav, device_type=UAV),
                        uavs=self.environment.uavs)
                    agent.action = agent.get_current_action()
                    agent.update_experience()
                    self.take_action(agent)
                for agent in agents:
                    agent.replay()
                    agent.update_target_network()
                    agent.save_weights(episode)
            for agent in self.agents:
                agent.update_epsilon()
                agent.episodes_rewards.append(agent.episode_return)
