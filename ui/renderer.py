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

    def draw_victims_labels(self, victims_dict):
        for name, pos in victims_dict.items():
            px = pos[0] * CELL_SIZE + CELL_SIZE // 2
            py = pos[1] * CELL_SIZE + CELL_SIZE // 2
            label = name.split()[-1]
            self.canvas.create_text(px, py, text=label, fill="white", font=("Segoe UI", 12, "bold"))

    # === HÀM VẼ TRỰC QUAN RIÊNG CHO CSP MÀ BẠN BỊ THIẾU ===
    def draw_csp_state(self, victims_dict, assignment, focus, status, victim_statuses):
        """Tô màu và vẽ hiệu ứng cho các nạn nhân dựa trên log của CSP"""
        for name, pos in victims_dict.items():
            px1, py1 = pos[0] * CELL_SIZE, pos[1] * CELL_SIZE
            px2, py2 = px1 + CELL_SIZE, py1 + CELL_SIZE

            # 1. Xác định màu gốc dựa trên Mức độ nghiêm trọng
            fill_color = "#E74C3C" # Mặc định là Đỏ (Nặng)
            if victim_statuses and name in victim_statuses:
                if victim_statuses[name] == 'Nhẹ':
                    fill_color = "#F39C12" # Cam/Vàng (Nhẹ)

            # 2. Xóa đè màu nếu Robot đã ra quyết định
            if name in assignment:
                if assignment[name] == 1:
                    fill_color = "#00B894" # Cứu -> Xanh lục
                else:
                    fill_color = "#636E72" # Bỏ qua -> Xám

            self.canvas.create_rectangle(px1, py1, px2, py2, fill=fill_color, outline="#13293D")
            label = name.split()[-1]
            self.canvas.create_text(px1 + CELL_SIZE//2, py1 + CELL_SIZE//2, text=label, fill="white", font=("Segoe UI", 12, "bold"))

            # 3. Hiệu ứng đang xét (Viền Vàng, Gạch chéo...)
            if name == focus:
                if status == 'checking':
                    self.canvas.create_rectangle(px1+3, py1+3, px2-3, py2-3, outline="#FDCB6E", width=4)
                elif status == 'valid':
                    self.canvas.create_rectangle(px1+3, py1+3, px2-3, py2-3, outline="#00CEC9", width=4)
                elif status == 'invalid':
                    self.canvas.create_line(px1+5, py1+5, px2-5, py2-5, fill="#13293D", width=4)
                    self.canvas.create_line(px1+5, py2-5, px2-5, py1+5, fill="#13293D", width=4)
                elif status == 'backtrack':
                    self.canvas.create_rectangle(px1+3, py1+3, px2-3, py2-3, outline="#D63031", width=4, dash=(4,4))

    def get_gradient_color(self, cost, max_cost=40):
        cost = min(cost, max_cost)
        ratio = cost / max_cost
        r, g, b = int(200 + (75 - 200) * ratio), int(255 + (0 - 255) * ratio), int(255 + (130 - 255) * ratio)
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