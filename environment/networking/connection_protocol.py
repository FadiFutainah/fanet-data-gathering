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


protocol1 = ConnectionProtocol(data_loss_rate=1, latency=128, data_loss=16, initialization_data_size=10)
protocol2 = ConnectionProtocol(data_loss_rate=35, latency=16, data_loss=128, initialization_data_size=10)
protocol3 = ConnectionProtocol(data_loss_rate=10, latency=64, data_loss=32, initialization_data_size=10)
