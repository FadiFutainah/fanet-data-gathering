import logging

from environment.devices.device import Device


class DataTransition:
    def __init__(self, source: Device, destination: Device, data_size: int, created_time: int) -> None:
        self.source = source
        self.data_size = data_size
        self.destination = destination
        self.created_time = created_time
        logging.info(f'completed transition: at {created_time} '
                     f'from {source} to {destination} '
                     f'with {data_size} packets ')

    def __str__(self):
        return f'at time step {self.created_time}: {self.source} -> {self.destination}: size {self.data_size}'
