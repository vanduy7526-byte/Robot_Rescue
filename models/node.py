from config import GRID_WIDTH, GRID_HEIGHT, WALL

def get_moves(state, map_grid):
    """Lấy các ô lân cận hợp lệ không phải tường"""
    x, y = state
    moves = []
    # Thử 4 hướng di chuyển: Lên, Xuống, Trái, Phải
    directions = [(x, y-1), (x, y+1), (x-1, y), (x+1, y)]
    for nx, ny in directions:
        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
            if map_grid.grid[ny][nx] != WALL:
                moves.append((nx, ny))
    return moves

def trace_path(node):
    """Truy vết ngược từ nút đích về nút gốc để lấy đường đi tổng thể"""
    path = []
    current = node
    while current is not None:
        path.append(current['state'])
        current = current['parent']
    return path[::-1]