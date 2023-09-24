from collections import deque
import random
import numpy as np
import tensorflow as tf
from matplotlib import pyplot as plt
from dataclasses import dataclass, field

@dataclass
class Environment:
    x: float
    y: float
    grid: np.ndarray = field(init=False)

    # cell types(1, 0, 5, 9)

    def __post_init__(self):
        self.init_grid()

    def init_grid(self):
        self.grid = np.array([
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1],
            [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1],
            [1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1],
            [1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 9, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            ])


    def reset(self):
        self.x = 1
        self.y = 1
        self.init_grid()
        return [self.y, self.x]

    def get_available_actions(self):
        return 0, 1, 2, 3

    def move(self, y, x):
        done = False
        next_state = None
        reward = 0
        if self.grid[y][x] == 9:
            done = True
            next_state = [y, x]
            reward = 100
        if self.grid[y][x] == 1:
            next_state = [self.y, self.x]
            reward = -0.5
        if self.grid[y][x] == 0:
            next_state = [y, x]
        self.grid[self.y][self.x] = 0
        self.y = next_state[0]
        self.x = next_state[1]
        self.grid[self.y][self.x] = 5
        return next_state, reward, done

    def step(self, action):
        if action == 0:
            return self.move(self.y, self.x + 1)
        if action == 1:
            return self.move(self.y, self.x - 1)
        if action == 2:
            return self.move(self.y + 1, self.x)
        if action == 3:
            return self.move(self.y - 1, self.x)

env = Environment(1, 1)
height = 17
width = 18
# ==================================
steps = 0
action_size: int = 4
state_size: int = height * width
max_steps: int = 170
num_of_episodes: int = 300
# ==================================
epsilon: float = 1.0
epsilon_decay: float = 0.995
epsilon_min: float = 0.01
epsilon_max: float = 1.0
gamma: float = 0.95
alpha: float = 0.001
agent_rewards = []
# ==================================
buffer_size: int = 2000
batch_size: int = 32
tau: float = 0.125
memory = deque(maxlen=buffer_size)
# ==================================
memo = np.zeros((height, width, action_size))
# ==================================
state_dim = 2
target_update_freq = 20
checkpoint_freq = 25
model = tf.keras.Sequential()
num_units = 24
model.add(tf.keras.layers.Dense(num_units, input_dim=state_dim, activation="relu"))
model.add(tf.keras.layers.Dense(num_units, activation="relu"))
model.add(tf.keras.layers.Dense(action_size))
model.compile(loss="mse", optimizer=tf.keras.optimizers.Adam())
target_model = tf.keras.models.clone_model(model)

def get_available_actions():
    return env.get_available_actions()

def get_next_state(move):
    return env.step(move)

def reset_environment():
    return env.reset()

wins = 0
for episode in range(num_of_episodes):
    tf.summary.scalar("epsilon", epsilon, step=episode)
    episode_return = 0
    state = env.reset()
    done = False
    steps = 0
    while not done and steps <= max_steps:
        steps += 1
        print("\r> DQN: Episode {}/{}, Step {}, epsilon {}, state{}, Return {}".format(
            episode + 1, num_of_episodes, steps, epsilon, state, episode_return), end="")

        if np.random.rand() < epsilon:
            actions = get_available_actions()
            action = random.choice(actions)
        else:
            action = np.argmax(model.predict(np.array([state]), verbose=0)[0])

        state_new, reward, done = env.step(action)
        episode_return += reward
        if done:
            wins += 1
        memory.append((state,action,reward,state_new,done))

        if len(memory) > batch_size:
            experience_sample = random.sample(memory, batch_size)
            x = np.array([e[0] for e in experience_sample])

            y = model.predict(x, verbose=0)
            x2 = np.array([e[3] for e in experience_sample])
            Q2 = gamma*np.max(target_model.predict(x2, verbose=0), axis=1)
            for i,(s,a,r,s2,d) in enumerate(experience_sample):
                y[i][a] = r
                if not d:
                    y[i][a] += Q2[i]

            model.fit(x, y, batch_size=batch_size, epochs=1, verbose=0)

            for layer in model.layers:
                for weight in layer.weights:
                    weight_name = weight.name.replace(':', '_')
                    tf.summary.histogram(weight_name, weight, step=steps)

        if steps % target_update_freq == 0:
            target_model.set_weights(model.get_weights())

        # if steps % checkpoint_freq == 0:
        #     model.save_weights("{}/weights-{:08d}-{:08d}".format(
        #         checkpoint_path, episode, steps))

        state = state_new

    epsilon = max(epsilon_min, epsilon * epsilon_decay)

    tf.summary.scalar("return", episode_return, step=episode)
    tf.summary.flush()
    agent_rewards.append(episode_return)
    # if (steps - 1) % checkpoint_freq != 0:
    #     model.save_weights("{}/weights-{:08d}-{:08d}".format(
    #         'checkpoint_path', episode, steps - 1))
print()

chunk_size = 2
y_points = np.array([])
for chunk in range(num_of_episodes // chunk_size):
    avg = np.sum(agent_rewards[chunk * chunk_size: chunk * chunk_size + chunk_size]) / chunk_size
    y_points = np.append(y_points, avg)
x_points = np.arange(0, num_of_episodes // chunk_size)
plt.plot(x_points, y_points)
# plt.savefig(f'{project_dir}/results1020.png')
plt.show()