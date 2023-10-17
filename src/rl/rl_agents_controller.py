import logging
from typing import List
from dataclasses import dataclass, field

import numpy as np
from matplotlib import pyplot as plt

from src.rl.data_collecting.data_collecting_agent import DataCollectingAgent
from src.rl.data_forwarding.data_forwarding_agent import DataForwardingAgent

from src.environment.core.environment import Environment


@dataclass
class RLAgentController:
    forwarding_agents: List[DataForwardingAgent]
    collecting_agents: List[DataCollectingAgent]
    environment: Environment
    num_of_episodes: int
    max_steps: int
    steps: int = field(init=False, default=0)
    episodes_rewards: List = field(init=False, default_factory=list)

    def __post_init__(self):
        for agent in self.forwarding_agents:
            agent.inject_environment_object(environment=self.environment)

    def run_forwarding_agents(self):
        for episode in range(self.num_of_episodes):
            self.environment.reset()
            for uav, forwarding_agent, collecting_agent in zip(self.environment.uavs, self.forwarding_agents,
                                                               self.collecting_agents):
                forwarding_agent.initialize_for_episode(uav)
                collecting_agent.initialize_for_episode(uav)
                forwarding_agent.log.append(f'episode: {episode + 1} >>>>>>>>>>>>>>>>>> ')
            steps = 0
            total_reward = 0
            while not self.environment.has_ended() and steps <= self.max_steps:
                print(f'\r>Episode: {episode + 1} / {self.num_of_episodes}, Step: {steps} / {self.max_steps} ', end='')
                steps += 1
                for agent in self.collecting_agents:
                    agent.take_random_collecting_action()
                for agent in self.forwarding_agents:
                    agent.step(episode)
                self.environment.step()
            for agent in self.forwarding_agents:
                agent.update_samples(force_update=True)
                agent.replay()
                agent.update_target_network()
                agent.save_weights(episode)
                total_reward += agent.episode_return
                agent.episodes_rewards.append(agent.episode_return)
            self.episodes_rewards.append(total_reward)
        agents_rewards = [agent.episodes_rewards for agent in self.forwarding_agents]
        self.save_reward_as_a_plot(rewards_list=agents_rewards, name='agents rewards')
        self.save_reward_as_a_plot(rewards_list=[self.episodes_rewards], name='agents total reward')
        for agent in self.forwarding_agents:
            agent.print_log()

    def test_agents_policy(self):
        self.environment.reset()
        for uav, forwarding_agent, collecting_agent in zip(self.environment.uavs, self.forwarding_agents,
                                                           self.collecting_agents):
            forwarding_agent.initialize_for_episode(uav)
            collecting_agent.uav = uav
        steps = 0
        while not self.environment.has_ended() and steps <= self.max_steps:
            steps += 1
            for agent in self.collecting_agents:
                agent.take_random_collecting_action()
            for agent in self.forwarding_agents:
                agent.step_for_testing()
            self.environment.step()
        for agent in self.forwarding_agents:
            agent.update_policy_samples(force_update=True)
        agents_rewards = [agent.episodes_rewards for agent in self.forwarding_agents]
        print(agents_rewards)

    @staticmethod
    def save_reward_as_a_plot(rewards_list: List[List], chunk_size=1, name: str = 'none'):
        for rewards in rewards_list:
            y_points = np.array([])
            for chunk in range(len(rewards) // chunk_size):
                avg = np.sum(rewards[chunk * chunk_size: chunk * chunk_size + chunk_size]) / chunk_size
                y_points = np.append(y_points, avg)
            x_points = np.arange(0, len(rewards) // chunk_size)
            plt.plot(x_points, y_points)
        plt.savefig(f'data/output/{name}.png')
        plt.cla()
