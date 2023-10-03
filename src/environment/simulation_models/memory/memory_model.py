from dataclasses import dataclass
from typing import List

from src.environment.core.globals import multiply_by_speed_rate
from src.environment.simulation_models.memory.memory import Memory
from src.environment.simulation_models.memory.data_packet import DataPacket


@dataclass
class MemoryModel:
    sending_buffer: Memory
    receiving_buffer: Memory
    memory: Memory

    def has_data(self) -> bool:
        return self.memory.has_data()

    def move_to_buffer_queue(self, data_size: int) -> None:
        data_size = min(data_size, self.sending_buffer.io_speed)
        self.memory.move_to(other=self.sending_buffer, data_size=data_size)

    def get_occupancy(self) -> float:
        return round(self.memory.current_size / self.memory.size, 2)

    def move_to_memory(self) -> None:
        if not self.receiving_buffer.has_data():
            return
        speed = min(self.receiving_buffer.io_speed, self.memory.io_speed)
        self.receiving_buffer.move_to(other=self.memory, data_size=speed)

    def fetch_data(self, data_size: int) -> List[DataPacket]:
        if not self.sending_buffer.has_data(data_size):
            remaining_data = data_size - self.sending_buffer.current_size
            remaining_data = min(remaining_data, self.sending_buffer.io_speed)
            self.move_to_buffer_queue(remaining_data)
        return self.sending_buffer.fetch_data(data_size)

    def store_data(self, data_packets: List[DataPacket], overwrite: bool = False) -> None:
        self.receiving_buffer.store_data(data_packets, overwrite)

    def store_data_in_memory(self, data_packets: List[DataPacket], overwrite: bool = False) -> None:
        self.memory.store_data(data_packets, overwrite)

    def step(self, time):
        self.move_to_memory()
        self.sending_buffer.decrease_packets_life_time(time)
        self.receiving_buffer.decrease_packets_life_time(time)

    def read_data(self) -> List[DataPacket]:
        return self.memory.read_data()

    def get_available_to_send(self) -> int:
        return self.sending_buffer.current_size

    def get_available_to_receive(self) -> int:
        return self.receiving_buffer.get_available()
