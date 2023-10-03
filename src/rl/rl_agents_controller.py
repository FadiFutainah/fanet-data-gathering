from typing import List
from dataclasses import dataclass, field

from src.rl.data_collecting.data_collecting_agent import DataCollectingAgent
from src.rl.data_forwarding.data_forwarding_agent import DataForwardingAgent

from src.environment.core.environment import Environment


@dataclass
class RLAgentController:
    forwarding_agents: List[DataForwardingAgent]
    collecting_agents: List[DataCollectingAgent]
    state_size: int
    action_size: int
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
            while not self.environment.has_ended() and steps <= self.max_steps:
                steps += 1
                print('\r> DQN: Episode {} / {}, step: {} / {}'.format(episode + 1, self.num_of_episodes, steps,
                                                                       self.max_steps), end='')
                self.environment.step()
                for agent in self.collecting_agents:
                    agent.take_random_collecting_action()
                for agent in self.forwarding_agents:
                    if agent.is_busy():
                        continue
                    agent.step(episode)
            for agent in self.forwarding_agents:
                agent.update_samples(force_update=True)
                agent.replay()
                agent.update_target_network()
                agent.save_weights(episode)
            for agent in self.forwarding_agents:
                agent.update_epsilon()
                agent.episodes_rewards.append(agent.episode_return)
        for agent in self.forwarding_agents:
            agent.save_reward_as_a_plot()
