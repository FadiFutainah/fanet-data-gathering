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

    def run(self):
        for episode in range(self.num_of_episodes):
            self.environment.reset()
            for uav, forwarding_agent, collecting_agent in zip(self.environment.uavs, self.forwarding_agents,
                                                               self.collecting_agents):
                forwarding_agent.initialize_for_episode(uav)
                collecting_agent.uav = uav
            steps = 0
            total_reward = 0
            logging.info(f'started {episode} >>>>>>>>>>>>>>>> ')
            while not self.environment.has_ended() and steps <= self.max_steps:
                print(f'\r>Episode: {episode + 1} / {self.num_of_episodes}, Step: {steps} / {self.max_steps}', end='')
                steps += 1
                self.environment.step()
                for agent in self.collecting_agents:
                    agent.take_random_collecting_action()
                for agent in self.forwarding_agents:
                    agent.step(episode)
            for agent in self.forwarding_agents:
                agent.update_samples(force_update=True)
                agent.replay()
                agent.update_target_network()
                agent.save_weights(episode)
            for agent in self.forwarding_agents:
                agent.update_epsilon()
                total_reward += agent.episode_return
                agent.episodes_rewards.append(agent.episode_return)
            self.episodes_rewards.append(total_reward)
        for agent in self.forwarding_agents:
            self.save_reward_as_a_plot(rewards=agent.episodes_rewards, name=f'agent of {agent}')
        self.save_reward_as_a_plot(rewards=self.episodes_rewards, name=f'all agents')

    @staticmethod
    def save_reward_as_a_plot(rewards: List, chunk_size=1, name: str = 'none'):
        y_points = np.array([])
        for chunk in range(len(rewards) // chunk_size):
            avg = np.sum(rewards[chunk * chunk_size: chunk * chunk_size + chunk_size]) / chunk_size
            y_points = np.append(y_points, avg)
        x_points = np.arange(0, len(rewards) // chunk_size)
        plt.plot(x_points, y_points)
        plt.savefig(f'data/output/{name}.png')
