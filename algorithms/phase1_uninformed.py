from collections import deque
from models.node import get_moves, trace_path

def bfs_search(map_grid, start_pos, goal_pos):
    start_node = {'state': tuple(start_pos), 'parent': None}
    queue = deque([start_node])
    visited = {tuple(start_pos)}
    history = []

    while queue:
        current = queue.popleft()
        history.append(current)

        if current['state'] == tuple(goal_pos):
            return trace_path(current), history

        for move in get_moves(current['state'], map_grid):
            if move not in visited:
                visited.add(move)
                next_node = {'state': move, 'parent': current}
                queue.append(next_node)

    return [], history

def dfs_search(map_grid, start_pos, goal_pos):
    start_node = {'state': tuple(start_pos), 'parent': None}
    stack = [start_node]
    visited = {tuple(start_pos)}
    history = []

    while stack:
        current = stack.pop()
        history.append(current)

        if current['state'] == tuple(goal_pos):
            return trace_path(current), history

        for move in get_moves(current['state'], map_grid):
            if move not in visited:
                visited.add(move)
                next_node = {'state': move, 'parent': current}
                stack.append(next_node)

    return [], history