# main.py
import tkinter as tk
from tkinter import ttk
from config import *
from models.map_grid import MapGrid

# Import toàn bộ các pha thuật toán từ các module độc lập
from algorithms.phase1_uninformed import bfs_search
from algorithms.phase2_informed import astar_search
from algorithms.phase5_local import simulated_annealing
from algorithms.phase6_complex import and_or_graph_search


class RescueApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Cứu Hộ")
        self.root.state('zoomed')

        self.root.configure(bg="#ECF0F1")
        self.is_running = False
        self.is_paused = False
        self.after_id = None

        self.header = tk.Label(self.root, text="MÔ PHỎNG ROBOT CỨU HỘ",
                               font=("Segoe UI", 18, "bold"), bg="#2C3E50", fg="white", pady=12)
        self.header.pack(side=tk.TOP, fill=tk.X)

        self.main_frame = tk.Frame(self.root, bg="#ECF0F1")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # KHU VỰC TRÁI: ĐIỀU KHIỂN VÀ BẢN ĐỒ
        self.left_frame = tk.Frame(self.main_frame, bg="#ECF0F1")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        self.control_frame = tk.LabelFrame(self.left_frame, text=" Bảng Điều Khiển ",
                                           font=("Segoe UI", 11, "bold"), bg="#ECF0F1", fg="#2C3E50", padx=10, pady=10)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 15))

        self.algo_var = tk.StringVar()
        algo_list = ["BFS", "A-Star", "Simulated Annealing", "AND-OR Search"]

        self.algo_combobox = ttk.Combobox(self.control_frame, textvariable=self.algo_var, values=algo_list,
                                          state="readonly", font=("Segoe UI", 11), width=18)
        self.algo_combobox.current(0)
        self.algo_combobox.pack(side=tk.LEFT, padx=(0, 10), ipady=3)

        self.btn_run = tk.Button(self.control_frame, text="CHẠY", font=("Segoe UI", 10, "bold"),
                                 bg="#27AE60", fg="white", activebackground="#2ECC71", activeforeground="white",
                                 relief=tk.FLAT, cursor="hand2", command=self.start_auto_play)
        self.btn_run.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=3)

        self.btn_pause = tk.Button(self.control_frame, text="TẠM DỪNG", font=("Segoe UI", 10, "bold"),
                                   bg="#F39C12", fg="white", activebackground="#E67E22", activeforeground="white",
                                   relief=tk.FLAT, cursor="hand2", command=self.toggle_pause, state=tk.DISABLED)
        self.btn_pause.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=3)

        self.btn_reset = tk.Button(self.control_frame, text="RESET", font=("Segoe UI", 10, "bold"),
                                   bg="#E74C3C", fg="white", activebackground="#E74C3C", activeforeground="white",
                                   relief=tk.FLAT, cursor="hand2", command=self.reset_map)
        self.btn_reset.pack(side=tk.RIGHT, fill=tk.X, expand=True, ipady=3)

        # BẢNG CHỈ SỐ ĐO LƯỜNG
        self.metrics_frame = tk.Frame(self.left_frame, bg="#1E272E", padx=15, pady=10)
        self.metrics_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 15))

        self.var_status = tk.StringVar(value="Trạng thái: SẴN SÀNG")
        self.var_algo_display = tk.StringVar(value="Thuật toán: ---")
        self.var_explored = tk.StringVar(value="Số ô đã duyệt: 0")
        self.var_path = tk.StringVar(value="Độ dài đường đi: 0 bước")

        font_metric = ("Consolas", 11, "bold")
        tk.Label(self.metrics_frame, textvariable=self.var_status, font=font_metric, bg="#1E272E", fg="#00FFCC",
                 anchor="w").grid(row=0, column=0, sticky="w", padx=(0, 40), pady=5)
        tk.Label(self.metrics_frame, textvariable=self.var_algo_display, font=font_metric, bg="#1E272E", fg="#FFEA00",
                 anchor="w").grid(row=0, column=1, sticky="w", pady=5)
        tk.Label(self.metrics_frame, textvariable=self.var_explored, font=font_metric, bg="#1E272E", fg="#FF0055",
                 anchor="w").grid(row=1, column=0, sticky="w", padx=(0, 40), pady=5)
        tk.Label(self.metrics_frame, textvariable=self.var_path, font=font_metric, bg="#1E272E", fg="#00FFCC",
                 anchor="w").grid(row=1, column=1, sticky="w", pady=5)

        # Bản đồ Canvas
        self.canvas_width = GRID_WIDTH * CELL_SIZE
        self.canvas_height = GRID_HEIGHT * CELL_SIZE
        self.canvas_frame = tk.Frame(self.left_frame, bg="#3A506B", padx=2, pady=2)
        self.canvas_frame.pack(side=tk.TOP)
        self.canvas = tk.Canvas(self.canvas_frame, width=self.canvas_width, height=self.canvas_height, bg="#0B132B",
                                highlightthickness=0)
        self.canvas.pack()

        # KHU VỰC PHẢI: BẢNG LOG
        self.right_frame = tk.LabelFrame(self.main_frame, text=" Nhật Ký Hoạt Động ", font=("Segoe UI", 11, "bold"),
                                         bg="#ECF0F1", fg="#2C3E50", padx=10, pady=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.scrollbar = tk.Scrollbar(self.right_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text = tk.Text(self.right_frame, width=45, yscrollcommand=self.scrollbar.set, bg="#1E272E",
                                fg="#00D2D3", font=("Consolas", 11), relief=tk.FLAT, selectbackground="#485460")
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.log_text.yview)

        # --- KHỞI TẠO DỮ LIỆU ---
        # --- KHỞI TẠO DỮ LIỆU ---
        self.my_map = MapGrid()

        # Đặt Robot bên trái, Nạn nhân bên phải trên lưới 10x10
        self.start_pos = (1, 4)
        self.goal_pos = (8, 4)

        self.setup_mock_map()
        self.draw_grid()
        self.add_log(">> HỆ THỐNG KHỞI ĐỘNG THÀNH CÔNG.")
        self.add_log(">> Sẵn sàng mô phỏng. Vui lòng chọn thuật toán.")

    def setup_mock_map(self):
        wall_lines = [
            # Tường chẻ dọc ở giữa (chừa khe hở nhỏ)
            (4, 1, 4, 2),
            (4, 6, 4, 8),

            # Một vách ngăn chữ L che chắn nạn nhân
            (7, 3, 9, 3),
            (7, 3, 7, 5),
        ]

        for x1, y1, x2, y2 in wall_lines:
            if x1 == x2:
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    self.my_map.add_element(x1, y, WALL)
            elif y1 == y2:
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    self.my_map.add_element(x, y1, WALL)

        self.my_map.add_element(self.start_pos[0], self.start_pos[1], ROBOT)
        self.my_map.add_element(self.goal_pos[0], self.goal_pos[1], VICTIM)

    def draw_grid(self):
        self.canvas.delete("all")
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell_val = self.my_map.grid[y][x]
                color = COLORS.get(cell_val, "white")
                self.color_cell(x, y, color)

    def color_cell(self, x, y, color):
        x1, y1 = x * CELL_SIZE, y * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#13293D")

    def add_log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def toggle_pause(self):
        if not self.is_running: return
        if self.is_paused:
            self.is_paused = False
            self.btn_pause.config(text="TẠM DỪNG", bg="#F39C12")
            self.var_status.set("Trạng thái: Đang chạy")
            self.add_log(">> [TIẾP TỤC MÔ PHỎNG]")
            self.animate_step()
        else:
            self.is_paused = True
            self.btn_pause.config(text="TIẾP TỤC", bg="#3498DB")
            self.var_status.set("Trạng thái: Đang tạm dừng")
            self.add_log(">> [ĐÃ TẠM DỪNG MÔ PHỎNG]")
            if self.after_id is not None:
                self.root.after_cancel(self.after_id)
                self.after_id = None

    def reset_map(self):
        self.is_running = False
        self.is_paused = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.btn_run.config(state=tk.NORMAL)
        self.btn_pause.config(state=tk.DISABLED, text="TẠM DỪNG", bg="#F39C12")
        self.algo_combobox.config(state="readonly")
        self.var_status.set("Trạng thái: SẴN SÀNG")
        self.var_algo_display.set("Thuật toán: ---")
        self.var_explored.set("Số ô đã duyệt: 0")
        self.var_path.set("Độ dài đường đi: 0 bước")
        self.log_text.delete('1.0', tk.END)
        self.add_log(">> ĐÃ DỪNG THUẬT TOÁN. Đã làm sạch bản đồ.")
        self.draw_grid()

    def start_auto_play(self):
        selected_algo = self.algo_var.get()
        self.btn_run.config(state=tk.DISABLED)
        self.btn_pause.config(state=tk.NORMAL, text="TẠM DỪNG", bg="#F39C12")
        self.algo_combobox.config(state=tk.DISABLED)
        self.var_status.set("Trạng thái: Đang chạy")
        self.var_path.set("Độ dài đường đi: Đang tìm...")
        self.var_algo_display.set(f"Thuật toán: {selected_algo.upper()}")
        self.add_log("-" * 40)
        self.add_log(f">> ĐANG CHẠY: {selected_algo.upper()}...")

        if selected_algo == "BFS":
            self.path, self.history = bfs_search(self.my_map, self.start_pos, self.goal_pos)
        elif selected_algo == "A-Star":
            self.path, self.history = astar_search(self.my_map, self.start_pos, self.goal_pos)
        elif selected_algo == "Simulated Annealing":
            self.path, self.history = simulated_annealing(self.my_map, self.start_pos, self.goal_pos)
        elif selected_algo == "AND-OR Search":
            self.path, self.history = and_or_graph_search(self.my_map, self.start_pos, self.goal_pos)

        self.is_running = True
        self.is_paused = False
        self.step_index = 0
        self.animate_step()

    def get_gradient_color(self, cost, max_cost=40):
        cost = min(cost, max_cost)
        ratio = cost / max_cost
        r = int(200 + (75 - 200) * ratio)
        g = int(255 + (0 - 255) * ratio)
        b = int(255 + (130 - 255) * ratio)
        return f"#{r:02x}{g:02x}{b:02x}"

    def animate_step(self):
        if not self.is_running or self.is_paused: return

        if self.step_index < len(self.history):
            node = self.history[self.step_index]
            x, y = node['state']
            current_algo = self.algo_var.get()

            self.var_explored.set(f"Số ô/nhánh đã duyệt: {self.step_index + 1} / {len(self.history)}")

            if current_algo == "AND-OR Search" and 'message' in node:
                if (x, y) != self.start_pos and (x, y) != self.goal_pos:
                    if node['type'] == 'OR':
                        self.color_cell(x, y, "#F39C12")
                    elif node['type'] == 'INFO':
                        self.color_cell(x, y, "#E74C3C")
                self.add_log(node['message'])
            else:
                g_cost = 0
                temp_node = node
                while temp_node.get('parent') is not None:
                    g_cost += 1
                    temp_node = temp_node['parent']

                if (x, y) != self.start_pos and (x, y) != self.goal_pos:
                    self.color_cell(x, y, self.get_gradient_color(g_cost))

                h_cost = abs(x - self.goal_pos[0]) + abs(y - self.goal_pos[1])
                f_cost = g_cost + h_cost
                coord_str = f"({x}, {y})"

                if current_algo == "A-Star":
                    self.add_log(f" > Duyệt: {coord_str:<8} | g={g_cost:<3} h={h_cost:<3} f={f_cost}")
                elif current_algo == "Simulated Annealing":
                    T_val, p_val, rand_val = node.get('T', 0), node.get('p', 0), node.get('rand', 0)
                    if p_val == 1.0:
                        self.add_log(f" > Duyệt: {coord_str:<8} | T={T_val:>6.2f} | Tự động nhận (Tốt hơn)")
                    else:
                        self.add_log(
                            f" > Duyệt: {coord_str:<8} | T={T_val:>6.2f} | p={p_val:.3f} > rand={rand_val:.3f}")
                else:
                    self.add_log(f" > Duyệt: {coord_str:<8} | Chi phí (g): {g_cost}")

            self.step_index += 1
            self.after_id = self.root.after(30, self.animate_step)
        else:
            self.draw_final_path()
            self.is_running = False
            self.btn_pause.config(state=tk.DISABLED)

    def draw_final_path(self):
        if not self.path:
            self.var_status.set("Trạng thái: VÔ NGHIỆM")
            self.add_log(">> THẤT BẠI: Không tìm thấy kế hoạch an toàn.")
            return

        self.var_status.set("Trạng thái: HOÀN THÀNH")
        self.add_log("-" * 40)

        if self.algo_var.get() == "AND-OR Search":
            self.var_path.set("Kế hoạch: Đã lập sơ đồ dự phòng")
            self.add_log(">> ĐÃ LẬP XONG KẾ HOẠCH DỰ PHÒNG CHO KHÓI MÙ!")
            edges = set()

            def extract_edges(plan, current_state):
                if not plan: return
                sub_plans = plan[1]
                for next_state, sub_plan in sub_plans.items():
                    edges.add((current_state, next_state))
                    extract_edges(sub_plan, next_state)

            extract_edges(self.path, self.start_pos)
            for state_a, state_b in edges:
                px1, py1 = state_a[0] * CELL_SIZE + CELL_SIZE // 2, state_a[1] * CELL_SIZE + CELL_SIZE // 2
                px2, py2 = state_b[0] * CELL_SIZE + CELL_SIZE // 2, state_b[1] * CELL_SIZE + CELL_SIZE // 2
                self.canvas.create_line(px1, py1, px2, py2, fill="#E67E22", width=3, dash=(5, 3), joinstyle=tk.ROUND)
        else:
            self.var_path.set(f"Độ dài đường đi: {len(self.path)} bước")
            self.add_log(f">> Tổng số bước di chuyển (Path Cost): {len(self.path)} bước.")
            pixel_points = []
            for x, y in self.path:
                pixel_points.extend([x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2])
            self.canvas.create_line(pixel_points, fill="#B3A300", width=6, joinstyle=tk.ROUND, capstyle=tk.ROUND)
            self.canvas.create_line(pixel_points, fill=COLORS["PATH"], width=3, joinstyle=tk.ROUND, capstyle=tk.ROUND)


if __name__ == "__main__":
    root = tk.Tk()
    app = RescueApp(root)
    root.mainloop()