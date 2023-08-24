from dataclasses import dataclass, field
from typing import Any, List

from src.environment.core.environment import Environment
from src.environment.devices.uav import UAV


@dataclass
class Agent:
    action_size: int
    state_size: int
    env: Environment
    uav_indices: List[int]
    steps: int = field(init=False, default=0)
    episodes_rewards: List = field(init=False, default_factory=list)
    uavs: List[UAV] = field(init=False)

    def init_uavs(self):
        self.uavs = [self.env.uavs[i] for i in self.uav_indices]

    def step(self, encoded_action: int, index: int):
        pass

    def get_reward(self) -> float:
        pass

    def get_current_state(self) -> Any:
        pass

    def run(self) -> None:
        pass

    def get_available_actions(self, index: int):
        pass

    def reset_environment(self):
        self.env.reset()
