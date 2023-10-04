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
            for uav, agent in zip(self.environment.uavs, self.forwarding_agents):
                agent.initialize_for_episode(uav)
            steps = 0
            total_reward = 0
            while not self.environment.has_ended() and steps <= self.max_steps:
                steps += 1

                self.environment.step()
                for agent in self.collecting_agents:
                    agent.take_random_collecting_action()
                for agent in self.forwarding_agents:
                    if agent.is_busy():
                        continue
                    agent.step(episode)
                    print(f'\r> Agent: {agent} - Episode: {episode + 1} / {self.num_of_episodes} - Step: {steps} / {self.max_steps}')
                    # print('\r> DQN: Episode {} / {}, step: {} / {}'.format(episode + 1, self.num_of_episodes, steps,
                    #                                                        self.max_steps), end='')
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
            self.save_reward_as_a_plot(rewards=agent.episodes_rewards, name='results-of-agent-{self}-{id(self)}')
        self.save_reward_as_a_plot(rewards=self.episodes_rewards, name=f'results-of-all-agents-{id(self)}')

    @staticmethod
    def save_reward_as_a_plot(rewards: List, chunk_size=1, name: str = 'none'):
        y_points = np.array([])
        for chunk in range(len(rewards) // chunk_size):
            avg = np.sum(rewards[chunk * chunk_size: chunk * chunk_size + chunk_size]) / chunk_size
            y_points = np.append(y_points, avg)
        x_points = np.arange(0, len(rewards) // chunk_size)
        plt.plot(x_points, y_points)
        plt.savefig(f'data/output/f{name}.png')
