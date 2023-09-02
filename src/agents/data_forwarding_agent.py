import math

from src.agents.agent import Agent

from dataclasses import dataclass
from typing import List

from src.environment.devices.uav import UAV


@dataclass
class DataForwardingState:
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
        # state.append(self.uav.energy)
        state.append(self.uav.num_of_collected_packets)
        state.append(self.uav.get_occupancy_percentage())
        return [state]


@dataclass
class DataForwardingAction:
    device_index: int

    def get(self):
        return self.device_index


@dataclass
class DataForwardingAgent(Agent):
    max_delay: float
    max_energy: float
    max_queue_length: float
    beta: float
    gamma_e: float
    """ represents the maximum penalty for exceeding the max_energy """
    lambda_d: float
    """ represents the maximum penalty for exceeding the max_delay """
    k: float
    """ describes the steepness of the sigmoid function """

    def get_delay_penalty(self, delay: float) -> float:
        return 1 / (1 + math.exp(-self.k * (delay - self.max_delay)))

    def get_energy_penalty(self, energy: float) -> float:
        return 1 / (1 + math.exp(-self.k * (energy - self.max_energy)))

    def get_reward(self, index: int):
        delay = self.env.calculate_e2e_delay(index)
        # energy = self.env.calculate_consumed_energy(index)
        pdr = self.env.calculate_pdr()
        delay_penalty = self.lambda_d * self.get_delay_penalty(delay)
        # energy_penalty = self.gamma_e * self.get_energy_penalty(energy)
        pdr_penalty = pdr * self.beta
        # return pdr_penalty - energy_penalty - delay_penalty
        return pdr_penalty - delay_penalty

    def reset_environment(self, index: int):
        self.env.reset()
        return self.get_current_state(index)

    def get_current_state(self, index: int):
        state = DataForwardingState(self.env.uavs[index], self.env.get_uavs_in_range(index))
        return state.get_state()

    def get_available_actions(self, index: int) -> List[DataForwardingAction]:
        actions = []
        uav = self.env.uavs[index]
        if not uav.memory_model.has_data():
            return []
        base_stations = self.env.get_base_stations_in_range(index)
        if len(base_stations) > 0:
            for i in range(len(base_stations)):
                actions.append(DataForwardingAction(index=i, type=0))
        else:
            uavs = self.env.get_uavs_in_range(index)
            for i in range(len(uavs)):
                actions.append(DataForwardingAction(index=i, type=1))
        return actions

    def step(self, encoded_action: int, index: int):
        action = DataForwardingAction.decode_action(encoded_action)
        uav = self.env.uavs[index]
        if action.type == 0:
            target = self.env.base_stations[action.index]
        else:
            target = self.env.uavs[action.index]
        uav.forward_data_target = target
        self.env.run()
        return self.get_current_state(index), self.get_reward(index), self.env.has_ended()
