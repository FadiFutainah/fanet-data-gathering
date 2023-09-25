# for agent in collecting_agents:
#     self.active_collecting_agents.remove(agent)
#     consumed_energy = agent.uav.consumed_energy
#     data_variance = self.get_data_variance(agent.uav)
#     agent.current_reward = self.a * consumed_energy + self.b * data_variance
