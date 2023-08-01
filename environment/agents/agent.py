from dataclasses import dataclass
from typing import Any

from environment.core.environment import Environment


@dataclass
class Agent:
    num_of_episodes: int
    action_size: int
    state_size: int
    max_steps: int
    epsilon: float
    epsilon_decay: float
    epsilon_min: float
    gamma: float
    alpha: float
    env: Environment
    uav_index: int

    def __post_init__(self):
        self.uav = self.env.uavs[self.uav_index]

    def get_reward(self) -> float:
        pass

    def get_current_state(self) -> Any:
        pass

    def run(self) -> None:
        pass

    def reset_environment(self):
        self.env.reset()
