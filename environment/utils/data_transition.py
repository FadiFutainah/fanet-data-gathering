import logging

from environment.devices.device import Device


class DataTransition:
    def __init__(self, source: Device, destination: Device, data_size: int, created_time: int) -> None:
        self.source = source
        self.data_size = data_size
        self.destination = destination
        self.created_time = created_time
        logging.info(f'data transition: at {created_time} '
                     f'from {type(source).__name__}{source.id} to {type(destination).__name__}{destination.id} '
                     f'with {data_size} packets ')

    def __str__(self):
        return f'at time step {self.created_time}: {self.source} -> {self.destination}: size {self.data_size}'
