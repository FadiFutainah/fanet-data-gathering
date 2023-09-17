from src.environment.devices.base_station import BaseStation
from src.environment.devices.sensor import Sensor
from src.environment.devices.uav import UAV, WayPoint
from src.environment.simulation_models.energy.energy_model import EnergyModel
from src.environment.simulation_models.memory.data_packet import DataPacket
from src.environment.utils.vector import Vector
from src.environment.simulation_models.memory.memory import Memory
from src.environment.simulation_models.memory.memory_model import MemoryModel
from src.environment.simulation_models.network.connection import ConnectionProtocol
from src.environment.simulation_models.network.network_model import NetworkModel

from copy import deepcopy

buffer1 = Memory(size=102400, io_speed=2000)
buffer2 = Memory(size=102400, io_speed=4000)
buffer3 = Memory(size=102400, io_speed=6000)
buffer4 = Memory(size=102400, io_speed=10000)

memory_model1 = MemoryModel(memory=Memory(size=200000, io_speed=3000), sending_buffer=buffer3,
                            receiving_buffer=buffer2)

memory_model2 = MemoryModel(memory=Memory(size=100000, io_speed=3000), sending_buffer=buffer3,
                            receiving_buffer=buffer2)

memory_model3 = MemoryModel(memory=Memory(size=200000, io_speed=30000), sending_buffer=buffer3,
                            receiving_buffer=buffer2)

memory_model4 = MemoryModel(memory=Memory(size=200000, io_speed=30000), sending_buffer=buffer3,
                            receiving_buffer=buffer2)
energy_model = EnergyModel(e_elec=1, c=1, delta=1, scale=1,
                           distance_threshold=1,
                           power_amplifier_for_fs=1,
                           power_amplifier_for_amp=1)
protocol = ConnectionProtocol(data_loss_percentage=3, data_loss_probability=3, initialization_data_size=950)

network_model = NetworkModel(center=Vector(0, 0, 0), bandwidth=1000, coverage_radius=30, protocol=protocol)

uav1 = UAV(position=Vector(0, 0, 0), velocity=Vector(1, 1, 2), acceleration=Vector(0, 0, 0), id=1,
           memory_model=deepcopy(memory_model1), network_model=deepcopy(network_model), num_of_collected_packets=0,
           consumed_energy=0, way_points=[WayPoint(position=Vector(0, 0, 0))], energy_model=energy_model)

uav2 = deepcopy(uav1)
uav3 = deepcopy(uav1)

base_station = BaseStation(position=Vector(0, 0, 0), velocity=Vector(1, 0, 0), acceleration=Vector(0, 0, 0), id=1,
                           memory_model=deepcopy(memory_model1), network_model=deepcopy(network_model),
                           num_of_collected_packets=0, consumed_energy=0, energy_model=energy_model)

sensor = Sensor(position=Vector(0, 0, 0), velocity=Vector(1, 0, 0), acceleration=Vector(0, 0, 0), id=1,
                memory_model=deepcopy(memory_model2), network_model=deepcopy(network_model), num_of_collected_packets=0,
                consumed_energy=0, data_collecting_rate=1000, packet_size=1, packet_life_time=1000, energy_model=energy_model)
sensor2 = deepcopy(sensor)
sensor3 = deepcopy(sensor)
sensor4 = deepcopy(sensor)
# from enum import Enum
#
# from src.environment.utils.priority_queue import PriorityQueue


# move
# uav.move_to_next_position()
# print(uav.position)
# uav.move_to_next_position()
# print(uav.position)
# uav.move_to_next_position()
# print(uav.position)

# collect from sensors

sensors = [sensor, sensor2, sensor3, sensor4]
uavs = [uav1, uav2]
base_stations = [base_station]

# print('s1:', sensor.get_current_data_size())
# print('s2:', sensor2.get_current_data_size())
# sensor.collect_data(current_time=1)
# sensor4.collect_data(current_time=1)
# sensor.collect_data(current_time=1)
# sensor.collect_data(current_time=1)
# sensor2.collect_data(current_time=1)
# sensor3.collect_data(current_time=1)
#
# print('s1:', sensor.get_current_data_size())
# print('s2:', sensor2.get_current_data_size())

# uav1.add_way_point(position=Vector(0, 0, 0))
# uav1.assign_collection_rate(0, 1000)
# uav1.assign_collect_data_task(0)


# def get_in_range(uav: UAV, device_type: type):
#     neighbours = []
#     if device_type == UAV:
#         lookup_list = uavs
#     elif device_type == Sensor:
#         lookup_list = sensors
#     else:
#         lookup_list = base_stations
#     for device in lookup_list:
#         if uav != device and uav.in_range(device):
#             neighbours.append(device)
#     return neighbours


#
#
# print('======================')
# uav1.step(current_time=2)
# uav2.step(current_time=2)
# uav3.step(current_time=2)
# print('u1:', uav1.get_current_data_size())
# uav1.collect_data(get_in_range(uav1, Sensor))
# uav1.step(current_time=2)
# uav2.step(current_time=2)
# uav3.step(current_time=2)
# print('u1:', uav1.get_current_data_size())

# forward between uav and uav

uav1.store_data_in_memory([DataPacket(size=10, life_time=10, arrival_time=1)] * 50)
uav2.store_data_in_memory([DataPacket(size=10, life_time=10, arrival_time=1)] * 50)

uav1.assign_forward_data_task(forward_data_target=uav2, data_to_forward=50)
uav2.assign_forward_data_task(forward_data_target=uav3, data_to_forward=50)

uav2.assign_receiving_data_task()
uav3.assign_receiving_data_task()

print('u1:', uav1.get_current_data_size())
print('u2:', uav2.get_current_data_size())
print('u3:', uav3.get_current_data_size())

print('- - - - - - - - - - - - - - - - - - -')

uav1.forward_data()

uav1.step(current_time=2)
uav2.step(current_time=2)
uav3.step(current_time=2)

print('u1:', uav1.get_current_data_size())
print('u2:', uav2.get_current_data_size())
print('u3:', uav3.get_current_data_size())

print('- - - - - - - - - - - - - - - - - - -')

uav2.forward_data(time_step=1)

uav1.step(current_time=2)
uav2.step(current_time=2)
uav3.step(current_time=2)

print('u1:', uav1.get_current_data_size())
print('u2:', uav2.get_current_data_size())
print('u3:', uav3.get_current_data_size())

# forward between uav and basestation
# uav1.store_data_in_memory([DataPacket(size=10, life_time=10, arrival_time=1)] * 100)
# uav1.assign_forward_data_task(forward_data_target=base_station, data_to_forward=1000)
# task = uav1.tasks[-1]
# print(uav1.get_current_data_size())
# print(base_station.get_current_data_size())
# if task == UAVTask.FORWARD:
#     uav1.forward_data()
# elif task == UAVTask.MOVE:
#     uav1.update_velocity()
#     uav1.move_to_next_position()
# print('Forward')
# base_station.step(current_time=2)
# print(uav1.get_current_data_size())
# print(base_station.get_current_data_size())

# class UAVTask(Enum):
#     FORWARD = 0
#     RECEIVE = 1
#     COLLECT = 2
#     MOVE = 3
#
#     def __lt__(self, other):
#         return self.value < other.value
#
#
# x = PriorityQueue()
# x.push(UAVTask.MOVE)
# x.push(UAVTask.FORWARD)
# x.push(UAVTask.RECEIVE)
#
# print(x.pop())
