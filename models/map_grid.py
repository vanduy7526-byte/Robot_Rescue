from config import GRID_WIDTH, GRID_HEIGHT, EMPTY

class MapGrid:
    def __init__(self):
        self.grid = [[EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    def add_element(self, x, y, element_type):
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            self.grid[y][x] = element_type