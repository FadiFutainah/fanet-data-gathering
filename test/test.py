from copy import deepcopy
from typing import List

import pandas as pd

# from matplotlib 

data = pd.read_csv('rewards.csv')
rewards = []
# print(data.columns)
for column in data.columns:
    rewards.append(column)
        
episodes = range(len(rewards))

import matplotlib.pyplot as plt

print(rewards)
# plt.plot(episodes, rewards)
# plt.show()
