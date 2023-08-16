import random

with open('file.txt', 'w') as f:
    for _ in range(75):
        x = random.uniform(1, 100)
        y = random.uniform(1, 100)
        f.write(f'{round(x, 1)},{round(y, 1)},0,0,0,0,0,0,0,0,2880,32,128,32,1600,32,0,0,0,0,10,4,7\n')

