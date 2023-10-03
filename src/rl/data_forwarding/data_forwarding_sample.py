from dataclasses import dataclass, field
from typing import List

from src.environment.simulation_models.memory.data_packet import DataPacket
from src.rl.data_forwarding.data_forwarding_state import DataForwardingState


@dataclass
class DataForwardingSample:
    created_time: int
    state: DataForwardingState
    action: int
    data_packets: List[DataPacket]
    next_state: DataForwardingState = None
    reward: float = None

    def has_completed(self) -> bool:
        return self.reward is not None and self.next_state is not None

    def update_next_state(self, state: DataForwardingState) -> None:
        self.next_state = state

    def update_reward(self, reward):
        self.reward = reward

    def get_num_of_arrived_packets(self) -> int:
        num = 0
        for data_packet in self.data_packets:
            if data_packet.arrival_time == 0:
                num += 1
        return num
