from dataclasses import dataclass, field

from environment.devices.device import Device
from environment.networking.connection_protocol import ConnectionProtocol


@dataclass
class Connection:
    speed: int
    target_data: int
    destination: Device
    protocol: ConnectionProtocol
    initialization_data_sent: int = field(init=False, default=0)

    def is_initialized(self) -> bool:
        return self.initialization_data_sent < self.protocol.initialization_data_size

    def run(self) -> int:
        if not self.is_initialized():
            return 0
