from typing import List
from dataclasses import dataclass

from src.environment.devices.base_station import BaseStation
from src.environment.devices.uav import UAV


@dataclass
class DataForwardingState:
    uav: UAV
    uavs: List[UAV]
    neighbouring_uavs: List[UAV]
    base_stations: List[BaseStation]
    neighbouring_base_stations: List[BaseStation]

    @staticmethod
    def get_empty_state():
        return [0] * 8

    def get(self):
        state = []
        uav_positions = []
        base_stations = []
        for uav in self.uavs:
            if uav in self.neighbouring_uavs:
                uav_positions.append(uav.current_way_point)
            else:
                uav_positions.append(-1)
        for base_station in self.base_stations:
            if base_station in self.neighbouring_uavs:
                base_stations.append(base_station.id)
            else:
                base_stations.append(-1)
        state.append(self.uav.current_way_point)
        state.extend(uav_positions)
        state.extend(base_stations)
        state.append(self.uav.consumed_energy)
        state.append(self.uav.num_of_collected_packets)
        state.append(self.uav.get_occupancy_percentage())
        return state
