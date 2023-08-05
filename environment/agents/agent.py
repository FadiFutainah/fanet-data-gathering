from dataclasses import dataclass, field
from typing import Any, List

from environment.core.environment import Environment


@dataclass
class Agent:
    action_size: int
    state_size: int
    env: Environment
    uav_index: int
    steps: int = field(init=False)
    episodes_rewards: List = field(init=False, default_factory=list)

    def __post_init__(self):
        self.uav = self.env.uavs[self.uav_index]
        self.steps = 0

    def step(self, encoded_action: int):
        pass

    def get_reward(self) -> float:
        pass

    def get_current_state(self) -> Any:
        pass

    def run(self) -> None:
        pass

    def get_available_actions(self):
        pass

    def reset_environment(self):
        self.env.reset()
