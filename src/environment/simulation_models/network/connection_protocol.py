import logging
import random
from dataclasses import dataclass


@dataclass
class ConnectionProtocol:
    """
    Encapsulates the connection protocols attributes like speed and checksum validation logic in simple data_loss_rate
    and connection speed.
    to simulate the data encryption simply create a connection protocol with high connection_slow_down value.
    all the variables are number refers to the number of data packets.
    """
    data_loss_percentage: float
    data_loss_probability: float
    initialization_data_size: int

    def calculate_data_loss(self, data_size: int) -> int:
        rand = random.randint(1, 100) / 100
        data = 0
        if rand <= self.data_loss_probability / 100:
            # logging.warning(f'data loss of size {self.data_loss_percentage * data_size} happened')
            data = (1 - self.data_loss_percentage / 100) * data_size
        return data
