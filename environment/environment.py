from environment.environment_builder import EnvironmentBuilder


class Environment(EnvironmentBuilder):
    def __init__(self, sensors: list, mobile_sinks: list, base_stations: list, height: float, width: float):
        super().__init__()
        self.height = height
        self.width = width
        self.sensors = sensors
        self.mobile_sinks = mobile_sinks
        self.base_stations = base_stations
