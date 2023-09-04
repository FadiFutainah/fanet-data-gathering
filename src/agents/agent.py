from dataclasses import dataclass, field
from typing import Any, List

from src.environment.core.environment import Environment


@dataclass
class Agent:
    state_size: int
    action_size: int
    env: Environment
    steps: int = field(init=False, default=0)
    episodes_rewards: List = field(init=False, default_factory=list)

    def step(self, encoded_action: int, index: int):
        pass

    def get_reward(self, index: int) -> float:
        pass

    def get_current_state(self, index: int) -> Any:
        pass

    def get_available_actions(self, index: int):
        pass

    def reset_environment(self, index: int):
        self.env.reset()
