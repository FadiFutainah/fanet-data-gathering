import os
from dataclasses import dataclass

from data.file_manager import FileManager
from environment.agents.dqn_agent import DQNAgent
from environment.plot.plot_environment import PlotEnvironment


@dataclass
class EnvironmentController:
    @staticmethod
    def run_solution(id: int) -> None:
        file = FileManager(id)
        environment = file.load_environment()
        plot_environment = PlotEnvironment(env=environment)
        plot_environment.run()

    @staticmethod
    def run_dqn_agent(solution_id: int) -> None:
        file = FileManager(solution_id)
        env = file.load_environment()
        agents = []
        for index, uav in enumerate(env.uavs):
            agent = DQNAgent(num_of_episodes=100, action_size=(len(env.uavs) - 1) + len(env.base_stations),
                             state_size=16, lambda_d=10, max_delay=1000, max_steps=50, max_energy=10000,
                             max_queue_length=3000, memory_max_size=uav.memory.current_size, uav_index=index,
                             batch_size=32, sigma_q=10, epsilon_min=0.03, epsilon=1, epsilon_decay=0.001,
                             gamma_e=uav.energy, gamma=0.001, k=1, env=env, alpha=0.001, tau=0.1, beta=0.4)
            agents.append(agent)
        for agent in agents:
            agent.run()

    @staticmethod
    def run_all_solution() -> None:
        for i in range(len(os.listdir('./data/input'))):
            file = FileManager(i)
            environment = file.load_environment()
            plot = PlotEnvironment(env=environment)
            plot.render(i)

    def init_agents(self):
        pass
