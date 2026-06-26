import heapq
from models.node import get_moves, trace_path


def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def astar_search(map_grid, start_pos, goal_pos):
    goal = tuple(goal_pos)
    start_node = {'state': tuple(start_pos), 'parent': None, 'g': 0, 'f': manhattan_distance(start_pos, goal)}

    count = 0
    open_set = [(start_node['f'], count, start_node)]
    g_score = {tuple(start_pos): 0}
    history = []

    while open_set:
        _, _, current = heapq.heappop(open_set)
        history.append(current)

        if current['state'] == goal:
            return trace_path(current), history

        for move in get_moves(current['state'], map_grid):
            tentative_g = current['g'] + 1
            if tentative_g < g_score.get(move, float('inf')):
                g_score[move] = tentative_g
                h = manhattan_distance(move, goal)
                next_node = {'state': move, 'parent': current, 'g': tentative_g, 'f': tentative_g + h}
                count += 1
                heapq.heappush(open_set, (next_node['f'], count, next_node))

    return [], history

def greedy_best_first_search(map_grid, start_pos, goal_pos):
    goal = tuple(goal_pos)
    start_node = {'state': tuple(start_pos), 'parent': None, 'h': manhattan_distance(start_pos, goal)}
    count = 0
    open_set = [(start_node['h'], count, start_node)]
    visited = {tuple(start_pos)}
    history = []

    while open_set:
        _, _, current = heapq.heappop(open_set)
        history.append(current)

        if current['state'] == goal:
            return trace_path(current), history

        for move in get_moves(current['state'], map_grid):
            if move not in visited:
                visited.add(move)
                h = manhattan_distance(move, goal)
                next_node = {'state': move, 'parent': current, 'h': h}
                count += 1
                heapq.heappush(open_set, (h, count, next_node))

    return [], history
