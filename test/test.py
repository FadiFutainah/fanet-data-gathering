from queue import PriorityQueue
from typing import Generator, Any

from simpy import Environment, Event

state = 'ready'


def task_exec(env: Environment, i: int) -> Generator[Event, Any, Any]:
    global state
    state = 'busy'
    print(f'task executing {env.now} {i}')
    yield env.timeout(2)
    print(f'task executed {env.now} {i}')
    state = 'ready'


def controller_run(env: Environment):
    while True:
        # take_action()
        env.process(task_exec(env, 0))
        yield env.timeout(0.5)


env = Environment()
env.process(controller_run(env))

# for i in range(5):
#     env.run(until=i + 1)
#     env.render()


def do_task():
    pass
    # do_something_to_edit_data()
    # dt = calculate_task_time()
    # take_time(dt)


def run_sensor():
    pass
    # for task in tasks:
    #     processes.add(do_task(task))


def run_sensors():
    pass
    # for sensor in sensors:
    #     run_sensor(sensor)


def run_environment():
    pass
    # while not ended:
    #     run_uavs()
    #     run_sensors()
    #     run_base_stations()


def real_run():
    env.run(until=999)


q = PriorityQueue()
q.put(3)
q.put(1)
q.put(2)
print(q.get())
print(q.get())
print(q.get())
