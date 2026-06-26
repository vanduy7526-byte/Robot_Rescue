# ui/renderer.py
import tkinter as tk
from config import *

class MapRenderer:
    def __init__(self, parent_frame):
        self.canvas_width = GRID_WIDTH * CELL_SIZE
        self.canvas_height = GRID_HEIGHT * CELL_SIZE
        self.canvas = tk.Canvas(parent_frame, width=self.canvas_width, height=self.canvas_height,
                                bg="#0B132B", highlightthickness=0)
        self.canvas.pack()

    def draw_grid(self, map_grid):
        self.canvas.delete("all")
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell_val = map_grid.grid[y][x]
                color = COLORS.get(cell_val, "white")
                self.color_cell(x, y, color)

    def color_cell(self, x, y, color):
        x1, y1 = x * CELL_SIZE, y * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#13293D")

    def get_gradient_color(self, cost, max_cost=40):
        cost = min(cost, max_cost)
        ratio = cost / max_cost
        r = int(200 + (75 - 200) * ratio)
        g = int(255 + (0 - 255) * ratio)
        b = int(255 + (130 - 255) * ratio)
        return f"#{r:02x}{g:02x}{b:02x}"

    def draw_and_or_edges(self, edges):
        for state_a, state_b in edges:
            px1, py1 = state_a[0] * CELL_SIZE + CELL_SIZE // 2, state_a[1] * CELL_SIZE + CELL_SIZE // 2
            px2, py2 = state_b[0] * CELL_SIZE + CELL_SIZE // 2, state_b[1] * CELL_SIZE + CELL_SIZE // 2
            self.canvas.create_line(px1, py1, px2, py2, fill="#E67E22", width=3, dash=(5, 3), joinstyle=tk.ROUND)

    def draw_standard_path(self, path):
        pixel_points = []
        for x, y in path:
            pixel_points.extend([x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2])
        self.canvas.create_line(pixel_points, fill="#B3A300", width=6, joinstyle=tk.ROUND, capstyle=tk.ROUND)
        self.canvas.create_line(pixel_points, fill=COLORS["PATH"], width=3, joinstyle=tk.ROUND, capstyle=tk.ROUND)