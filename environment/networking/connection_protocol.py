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
    latency: int
    data_loss: int
    data_loss_rate: int
    initialization_data_size: int

    def calculate_error(self) -> int:
        rand = random.randint(1, 100)
        data = 0
        if rand <= self.data_loss_rate:
            logging.warning(f'data loss of size {self.data_loss} happened')
            data = self.data_loss
        return data
