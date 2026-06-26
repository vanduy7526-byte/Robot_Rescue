# algorithms/phase5_local.py
import math
import random
from algorithms.phase2_informed import manhattan_distance
from models.node import get_moves, trace_path

def simulated_annealing(map_grid, start_pos, goal_pos):
    goal = tuple(goal_pos)
    start = {'state': tuple(start_pos), 'parent': None, 'path_cost': 0, 'T': 100.0, 'p': 1.0, 'rand': 0.0}

    T = 100.0
    T_min = 0.01
    alpha = 0.95

    current = start
    history = [current]

    while T > T_min:
        if current['state'] == goal:
            return trace_path(current), history

        actions = get_moves(current['state'], map_grid)
        if not actions:
            break

        random_action = random.choice(actions)
        next_state_node = {
            'state': tuple(random_action),
            'parent': current,
            'path_cost': current['path_cost'] + 1
        }

        current_h = manhattan_distance(current['state'], goal)
        next_h = manhattan_distance(next_state_node['state'], goal)
        delta = next_h - current_h

        if delta < 0:
            current = next_state_node
            current['T'] = T
            current['p'] = 1.0
            current['rand'] = 0.0
            history.append(current)
        else:
            try:
                p = math.exp(-delta / T)
            except OverflowError:
                p = 0

            rand_val = random.random()
            if rand_val < p:
                current = next_state_node
                current['T'] = T
                current['p'] = p
                current['rand'] = rand_val
                history.append(current)

        T = alpha * T

    return [], history

def steepest_ascent_hill_climbing(map_grid, start_pos, goal_pos):
    # Thành viên B sẽ làm thuật toán này ở đây
    return [], []