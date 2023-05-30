from environment.devices.device import Device


class DataTransition:
    def __init__(self, source: Device, destination: Device, number_of_packets: int, created_time: int) -> None:
        self.source = source
        self.destination = destination
        self.created_time = created_time
        self.number_of_packets = number_of_packets
