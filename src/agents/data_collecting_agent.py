import random
from dataclasses import dataclass, field
from typing import List

from src.environment.devices.uav import UAV, UAVTask


@dataclass
class DataCollectingState:
    uav: UAV
    uavs: List[UAV]
    neighbouring_uavs: List[UAV]

    def get(self):
        state = []
        uav_positions = []
        for uav in self.uavs:
            if uav in self.neighbouring_uavs:
                uav_positions.append(uav.current_way_point)
            else:
                uav_positions.append(-1)
        state.append(self.uav.current_way_point)
        state.extend(uav_positions)
        state.append(self.uav.consumed_energy)
        return [state]


@dataclass
class DataCollectingAction:
    collection_rate: int
    do_collect: bool

    def get(self):
        return self.collection_rate


@dataclass
class DataCollectingAgent:
    # action_size: int
    uav: UAV
    steps: int = field(init=False, default=0)
    # episodes_rewards: List = field(init=False, default_factory=list)
    # forward_targets: list = field(init=False, default_factory=list)
    # model: Any = field(init=False)
    # target_model: Any = field(init=False)
    # memory: list = field(init=False, default_factory=list)
    # epsilon: float
    # epsilon_min: float
    # epsilon_max: float
    # epsilon_decay: float
    # target_update_freq: int
    # checkpoint_freq: int
    # checkpoint_path: str
    # gamma: float
    # batch_size: int
    # state_dim: int
    # current_reward: float = 0
    # wins: int = 0
    episode_return: int = 0
    collection_rates: List = field(init=False)
    # last_state: DataForwardingState = None
    # current_state: DataForwardingState = None
    action: DataCollectingAction = None

    # reward: int = 0

    def __post_init__(self):
        self.collection_rates = [0] * len(self.uav.way_points)

    def initialize_for_episode(self):
        self.steps = 0
        self.episode_return = 0

    def has_collect_task(self):
        return self.uav.is_active(UAVTask.COLLECT)

    def need_collecting_task(self) -> bool:
        return self.uav.way_points[self.uav.current_way_point].collection_rate == 0

    def take_random_collecting_action(self):
        collection_rate = random.choice([32, 64, 128])
        do_collect = random.choice([0, 1])
        self.collection_rates[self.uav.current_way_point] = collection_rate
        self.action = DataCollectingAction(collection_rate=collection_rate, do_collect=bool(do_collect))
        self.uav.assign_collection_rate(self.uav.current_way_point, self.action.collection_rate)
        if self.action.do_collect:
            self.uav.assign_collect_data_task(self.uav.current_way_point)
        # self.active_collecting_agents.append(agent)
