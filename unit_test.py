from src.environment.devices.base_station import BaseStation
from src.environment.devices.sensor import Sensor
from src.environment.devices.uav import UAV
from src.environment.utils.vector import Vector
from src.environment.simulation_models.memory.memory import Memory
from src.environment.simulation_models.memory.memory_model import MemoryModel
from src.environment.simulation_models import ConnectionProtocol
from src.environment.simulation_models import NetworkModel

from copy import deepcopy

buffer1 = Memory(size=1024, io_speed=20)
buffer2 = Memory(size=1024, io_speed=40)
buffer3 = Memory(size=1024, io_speed=60)
buffer4 = Memory(size=1024, io_speed=100)

memory_model = MemoryModel(memory=Memory(size=2000, io_speed=30), sending_buffer=buffer3,
                           receiving_buffer=buffer2)

protocol = ConnectionProtocol(data_loss_percentage=0.3, data_loss_probability=0.3, initialization_data_size=1)

network_model = NetworkModel(center=Vector(0, 0, 0), bandwidth=4096, coverage_radius=30, protocol=protocol)

uav = UAV(position=Vector(0, 0, 0), velocity=Vector(1, 1, 2), acceleration=Vector(0, 0, 0), id=1,
          memory_model=deepcopy(memory_model), network_model=deepcopy(network_model), num_of_collected_packets=0,
          energy=0, way_points=[Vector(0, 0, 0)])

base_station = BaseStation(position=Vector(0, 0, 0), velocity=Vector(1, 0, 0), acceleration=Vector(0, 0, 0), id=1,
                           memory_model=deepcopy(memory_model), network_model=deepcopy(network_model),
                           num_of_collected_packets=0, energy=0)

sensor = Sensor(position=Vector(0, 0, 0), velocity=Vector(1, 0, 0), acceleration=Vector(0, 0, 0), id=1,
                memory_model=deepcopy(memory_model), network_model=deepcopy(network_model), num_of_collected_packets=0,
                energy=0, data_collecting_rate=1000, packet_size=1, packet_life_time=1000)
sensor2 = deepcopy(sensor)

# move
# uav.move_to_next_position()
# print(uav.position)
# uav.move_to_next_position()
# print(uav.position)
# uav.move_to_next_position()
# print(uav.position)

# collect from sensors
sensors = [sensor]
uavs = [uav]
base_stations = [base_station]
print(sensor.get_current_data_size())
print(sensor2.get_current_data_size())
sensor.collect_data(current_time=1)
sensor.collect_data(current_time=1)
sensor.collect_data(current_time=1)
sensor.collect_data(current_time=1)
sensor2.collect_data(current_time=1)

print(sensor.get_current_data_size())
print(sensor2.get_current_data_size())

uav.assign_collection_data_task(0, 30)


def get_in_range(uav: UAV, device_type: type):
    neighbours = []
    if device_type == UAV:
        lookup_list = uavs
    elif device_type == Sensor:
        lookup_list = sensors
    else:
        lookup_list = base_stations
    for device in lookup_list:
        if uav != device and uav.in_range(device):
            neighbours.append(device)
    return neighbours


print('======================')
print(uav.get_current_data_size())
uav.collect_data(get_in_range(uav, Sensor))
print(uav.get_current_data_size())

# forward between uav and uav

# forward between uav and basestation
