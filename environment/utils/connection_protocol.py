import logging
import random


class ConnectionProtocol:
    """
    Encapsulates the connection protocols attributes like speed and checksum validation logic in simple data_loss_rate
    and connection speed.
    To simulate the data encryption simply create a connection protocol with high connection_slow_down value.
    """

    def __init__(self, data_loss_rate: int, connection_slow_down: int, data_loss: int) -> None:
        self.data_loss_rate = data_loss_rate
        self.connection_slow_down = connection_slow_down
        self.data_loss = data_loss

    def use(self, data: int) -> int:
        data -= self.connection_slow_down
        rand = random.randint(1, 100)
        if rand <= self.data_loss_rate:
            logging.warning(f'data loss of size {self.data_loss} happened')
            data -= self.data_loss
        return data


TCP = ConnectionProtocol(data_loss_rate=2, connection_slow_down=128, data_loss=16)
SMDP = ConnectionProtocol(data_loss_rate=10, connection_slow_down=64, data_loss=32)
UDP = ConnectionProtocol(data_loss_rate=35, connection_slow_down=16, data_loss=128)
