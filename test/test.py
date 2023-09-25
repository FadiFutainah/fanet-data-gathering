# for agent in collecting_agents:
#     self.active_collecting_agents.remove(agent)
#     consumed_energy = agent.uav.consumed_energy
#     data_variance = self.get_data_variance(agent.uav)
#     agent.current_reward = self.a * consumed_energy + self.b * data_variance

class Bla:
    def __init__(self):
        self.value = 1

    def __hash__(self):
        print('hash :', hash(self.value))
        return hash(self.value)


a = Bla()
b = Bla()

d = dict()
d[a] = 2
d[b] = 3

print(d[a])
print(d[b])
print(len(d))
