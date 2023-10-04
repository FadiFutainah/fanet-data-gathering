import csv

# Define the input and output file names
input_file = 'data/input/test_sample_10/way_points.csv'
output_file = 'data/input/test_sample_8/way_points2.csv'

# Open the input CSV file for reading and the output CSV file for writing
with open(input_file, mode='r') as input_csvfile, open(output_file, mode='w', newline='') as output_csvfile:
    # Create a CSV reader and writer objects
    csv_reader = csv.DictReader(input_csvfile)
    fieldnames = csv_reader.fieldnames

    # Create a CSV writer with the same fieldnames as the input file
    csv_writer = csv.DictWriter(output_csvfile, fieldnames=fieldnames)

    # Write the header row to the output file
    csv_writer.writeheader()

    # Process each row in the input file and write the modified data to the output file
    for row in csv_reader:
        # Convert 'x' and 'y' values to integers and multiply them by 50
        x = int(row['x']) * 500
        y = int(row['y']) * 500

        # Update the row with the multiplied values
        row['x'] = x
        row['y'] = y

        # Write the updated row to the output file
        csv_writer.writerow(row)

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
