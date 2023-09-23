import sys
import pygame
import random
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('title', type=str, default='test_sample')
parser.add_argument('num_of_uavs', type=int)
parser.add_argument('num_of_sensors', type=int)
parser.add_argument('width', type=int)
parser.add_argument('height', type=int)
parser.add_argument('grid_size', type=int, default=10)
args = parser.parse_args()

GRID_SIZE = args.grid_size
GRID_WIDTH = args.width * GRID_SIZE
GRID_HEIGHT = args.height * GRID_SIZE
NUM_OF_UAVS = args.num_of_uavs

with open('data/generated/sensors', 'a') as f:
    f.write(f'{args.title}\n')

with open('data/generated/uavs', 'a') as f:
    f.write(f'{args.title}\n')

with open('data/generated/way_points', 'a') as f:
    f.write(f'{args.title}\n')

with open('data/generated/sensors', 'a') as f:
    for _ in range(args.num_of_sensors):
        x = random.uniform(1, args.width)
        y = random.uniform(1, args.height)
        f.write(f'{round(x, 1)},{round(y, 1)},0,0,0,0,0,0,0,0,2880,32,4,7\n')
pygame.init()

GRID_ROWS = GRID_HEIGHT // GRID_SIZE
GRID_COLS = GRID_WIDTH // GRID_SIZE

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((GRID_WIDTH, GRID_HEIGHT))
pygame.display.set_caption("Point Selection Tool")

selected_points = []

for uav_id in range(NUM_OF_UAVS):
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = mouse_x // GRID_SIZE
                grid_y = mouse_y // GRID_SIZE
                selected_points.append((grid_x, grid_y))
        screen.fill(WHITE)

        for row in range(GRID_ROWS):
            pygame.draw.line(screen, BLACK, (0, row * GRID_SIZE), (GRID_WIDTH, row * GRID_SIZE))
        for col in range(GRID_COLS):
            pygame.draw.line(screen, BLACK, (col * GRID_SIZE, 0), (col * GRID_SIZE, GRID_HEIGHT))

        for point in selected_points:
            pygame.draw.rect(screen, GREEN, (point[0] * GRID_SIZE, point[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        pygame.display.flip()

    with open('data/generated/way_points', 'a') as f:
        for point in selected_points:
            f.write(f'{uav_id + 1},{point[0]},{point[1]},0,0\n')
    with open('data/generated/uavs', 'a') as f:
        f.write(
            f'{selected_points[0][0]},{selected_points[0][1]},0,0,0,0,0,0,0,28800,10\n')
    selected_points.clear()

with open('data/generated/sensors', 'a') as f:
    f.write('= = = = = = = = = = = =\n')

with open('data/generated/uavs', 'a') as f:
    f.write('= = = = = = = = = = = =\n')

with open('data/generated/way_points', 'a') as f:
    f.write('= = = = = = = = = = = =\n')

pygame.quit()
sys.exit()
