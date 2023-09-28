# for agent in collecting_agents:
#     self.active_collecting_agents.remove(agent)
#     consumed_energy = agent.uav.consumed_energy
#     data_variance = self.get_data_variance(agent.uav)
#     agent.current_reward = self.a * consumed_energy + self.b * data_variance

# class Bla:
#     def __init__(self):
#         self.value = 1
#
#     def __hash__(self):
#         print('hash :', hash(self.value))
#         return hash(self.value)
#
#
# a = Bla()
# b = Bla()
#
# d = dict()
# d[a] = 2
# d[b] = 3
#
# print(d[a])
# print(d[b])
# print(len(d))


# psudecode:
#     action = agent.choose_action()
#     agent.do_action(action)
#     agent.add_to_waiting_for_acknowladgement(experience)
#     agent.do_other_stuff()
#
#     for experience in waiting_for_acknowladgement():
#         if controller.check_for_acknowladgement(experience) is not None:
#             experience.reward = get_reward(experience)
#             memory.append(experience)
#
