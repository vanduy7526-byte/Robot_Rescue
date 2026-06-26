# main.py
import tkinter as tk
from tkinter import ttk
from config import *
from models.map_grid import MapGrid

# Nhập các class từ package ui
from ui.renderer import MapRenderer
from ui.panel import LogPanel

# Nhập thuật toán
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

        # === CỘT TRÁI (Điều khiển & Bản đồ) ===
        self.left_frame = tk.Frame(self.main_frame, bg="#ECF0F1")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        # 1. Khu vực Bảng điều khiển
        self.control_frame = tk.LabelFrame(self.left_frame, text=" Bảng Điều Khiển ",
                                           font=("Segoe UI", 11, "bold"), bg="#ECF0F1", fg="#2C3E50", padx=10, pady=10)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 15))

        self.algo_var = tk.StringVar()
        algo_list = ["BFS", "A-Star", "Simulated Annealing", "AND-OR Search"]
        self.algo_combobox = ttk.Combobox(self.control_frame, textvariable=self.algo_var, values=algo_list,
                                          state="readonly", font=("Segoe UI", 11), width=18)
        self.algo_combobox.current(0)
        self.algo_combobox.pack(side=tk.LEFT, padx=(0, 10), ipady=3)

        self.btn_run = tk.Button(self.control_frame, text="CHẠY", font=("Segoe UI", 10, "bold"), bg="#27AE60",
                                 fg="white", cursor="hand2", command=self.start_auto_play)
        self.btn_run.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=3)

        self.btn_pause = tk.Button(self.control_frame, text="TẠM DỪNG", font=("Segoe UI", 10, "bold"), bg="#F39C12",
                                   fg="white", cursor="hand2", command=self.toggle_pause, state=tk.DISABLED)
        self.btn_pause.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=3)

        self.btn_step = tk.Button(self.control_frame, text="STEP", font=("Segoe UI", 10, "bold"), bg="#9B59B6",
                                  fg="white", cursor="hand2", command=self.manual_step, state=tk.NORMAL)
        self.btn_step.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=3)

        self.btn_reset = tk.Button(self.control_frame, text="RESET", font=("Segoe UI", 10, "bold"), bg="#E74C3C",
                                   fg="white", cursor="hand2", command=self.reset_map)
        self.btn_reset.pack(side=tk.RIGHT, fill=tk.X, expand=True, ipady=3)

        # 2. Bảng Chỉ số Đo lường
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

        # 3. Khu vực Canvas (Gắn UI Renderer vào đây)
        self.canvas_frame = tk.Frame(self.left_frame, bg="#3A506B", padx=2, pady=2)
        self.canvas_frame.pack(side=tk.TOP)
        self.renderer = MapRenderer(self.canvas_frame)

        # === CỘT PHẢI (Gắn UI Panel Log vào đây) ===
        self.log_panel = LogPanel(self.main_frame)

        # --- KHỞI TẠO DỮ LIỆU ---
        self.my_map = MapGrid()
        self.start_pos = (1, 4)
        self.goal_pos = (8, 4)

        self.setup_mock_map()
        self.renderer.draw_grid(self.my_map)

        self.log_panel.add_log(">> HỆ THỐNG KHỞI ĐỘNG THÀNH CÔNG.")
        self.log_panel.add_log(">> Sẵn sàng mô phỏng. Vui lòng chọn thuật toán.")

    def setup_mock_map(self):
        wall_lines = [
            (4, 1, 4, 2), (4, 6, 4, 8),
            (7, 3, 9, 3), (7, 3, 7, 5),
        ]
        for x1, y1, x2, y2 in wall_lines:
            if x1 == x2:
                for y in range(min(y1, y2), max(y1, y2) + 1): self.my_map.add_element(x1, y, WALL)
            elif y1 == y2:
                for x in range(min(x1, x2), max(x1, x2) + 1): self.my_map.add_element(x, y1, WALL)
        self.my_map.add_element(self.start_pos[0], self.start_pos[1], ROBOT)
        self.my_map.add_element(self.goal_pos[0], self.goal_pos[1], VICTIM)

    # === CÁC HÀM ĐIỀU KHIỂN NÚT BẤM ===
    def toggle_pause(self):
        if not self.is_running: return
        if self.is_paused:
            self.is_paused = False
            self.btn_pause.config(text="TẠM DỪNG", bg="#F39C12")
            self.var_status.set("Trạng thái: Đang chạy")
            self.log_panel.add_log(">> [TIẾP TỤC MÔ PHỎNG]")
            self.animate_step()
        else:
            self.is_paused = True
            self.btn_pause.config(text="TIẾP TỤC", bg="#3498DB")
            self.var_status.set("Trạng thái: Đang tạm dừng")
            self.log_panel.add_log(">> [ĐÃ TẠM DỪNG MÔ PHỎNG]")
            if self.after_id is not None:
                self.root.after_cancel(self.after_id)
                self.after_id = None

    def manual_step(self):
        if not self.is_running:
            self.start_auto_play(start_paused=True)
        else:
            self.animate_step(force_step=True)

    def reset_map(self):
        self.is_running = False
        self.is_paused = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.btn_run.config(state=tk.NORMAL)
        self.btn_pause.config(state=tk.DISABLED, text="TẠM DỪNG", bg="#F39C12")
        self.btn_step.config(state=tk.NORMAL)
        self.algo_combobox.config(state="readonly")

        self.var_status.set("Trạng thái: SẴN SÀNG")
        self.var_algo_display.set("Thuật toán: ---")
        self.var_explored.set("Số ô đã duyệt: 0")
        self.var_path.set("Độ dài đường đi: 0 bước")

        self.log_panel.clear()
        self.log_panel.add_log(">> ĐÃ DỪNG THUẬT TOÁN. Đã làm sạch bản đồ.")
        self.renderer.draw_grid(self.my_map)

    def start_auto_play(self, start_paused=False):
        selected_algo = self.algo_var.get()
        self.btn_run.config(state=tk.DISABLED)
        self.btn_pause.config(state=tk.NORMAL, text="TIẾP TỤC" if start_paused else "TẠM DỪNG",
                              bg="#3498DB" if start_paused else "#F39C12")
        self.btn_step.config(state=tk.NORMAL)
        self.algo_combobox.config(state=tk.DISABLED)

        self.var_status.set("Trạng thái: Đang tạm dừng (Step)" if start_paused else "Trạng thái: Đang chạy")
        self.var_path.set("Độ dài đường đi: Đang tìm...")
        self.var_algo_display.set(f"Thuật toán: {selected_algo.upper()}")
        self.log_panel.add_log("-" * 40)
        self.log_panel.add_log(f">> ĐANG CHẠY: {selected_algo.upper()}...")

        if selected_algo == "BFS":
            self.path, self.history = bfs_search(self.my_map, self.start_pos, self.goal_pos)
        elif selected_algo == "A-Star":
            self.path, self.history = astar_search(self.my_map, self.start_pos, self.goal_pos)
        elif selected_algo == "Simulated Annealing":
            self.path, self.history = simulated_annealing(self.my_map, self.start_pos, self.goal_pos)
        elif selected_algo == "AND-OR Search":
            self.path, self.history = and_or_graph_search(self.my_map, self.start_pos, self.goal_pos)

        self.is_running = True
        self.is_paused = start_paused
        self.step_index = 0

        if start_paused:
            self.animate_step(force_step=True)
        else:
            self.animate_step()

    # === LOGIC ĐỒ HỌA MÔ PHỎNG TỪNG BƯỚC ===
    def animate_step(self, force_step=False):
        if not self.is_running: return

        if self.is_paused and not force_step: return

        if self.step_index < len(self.history):
            node = self.history[self.step_index]
            x, y = node['state']
            current_algo = self.algo_var.get()

            self.var_explored.set(f"Số ô/nhánh đã duyệt: {self.step_index + 1} / {len(self.history)}")

            if current_algo == "AND-OR Search" and 'message' in node:
                if (x, y) != self.start_pos and (x, y) != self.goal_pos:
                    if node['type'] == 'OR':
                        self.renderer.color_cell(x, y, "#F39C12")
                    elif node['type'] == 'INFO':
                        self.renderer.color_cell(x, y, "#E74C3C")
                self.log_panel.add_log(node['message'])
            else:
                g_cost = 0
                temp_node = node
                while temp_node.get('parent') is not None:
                    g_cost += 1
                    temp_node = temp_node['parent']

                if (x, y) != self.start_pos and (x, y) != self.goal_pos:
                    self.renderer.color_cell(x, y, self.renderer.get_gradient_color(g_cost))

                h_cost = abs(x - self.goal_pos[0]) + abs(y - self.goal_pos[1])
                f_cost = g_cost + h_cost
                coord_str = f"({x}, {y})"

                if current_algo == "A-Star":
                    self.log_panel.add_log(f" > Duyệt: {coord_str:<8} | g={g_cost:<3} h={h_cost:<3} f={f_cost}")
                elif current_algo == "Simulated Annealing":
                    T_val, p_val, rand_val = node.get('T', 0), node.get('p', 0), node.get('rand', 0)
                    if p_val == 1.0:
                        self.log_panel.add_log(f" > Duyệt: {coord_str:<8} | T={T_val:>6.2f} | Tự động nhận")
                    else:
                        self.log_panel.add_log(
                            f" > Duyệt: {coord_str:<8} | T={T_val:>6.2f} | p={p_val:.3f} > rand={rand_val:.3f}")
                else:
                    self.log_panel.add_log(f" > Duyệt: {coord_str:<8} | Chi phí (g): {g_cost}")
            # --------------------------------------------------

            self.step_index += 1

            if not self.is_paused:
                self.after_id = self.root.after(30, self.animate_step)
        else:
            self.draw_final_path()
            self.is_running = False
            self.btn_pause.config(state=tk.DISABLED)
            self.btn_step.config(state=tk.DISABLED)

    def draw_final_path(self):
        if not self.path:
            self.var_status.set("Trạng thái: VÔ NGHIỆM")
            self.log_panel.add_log(">> THẤT BẠI: Không tìm thấy kế hoạch an toàn.")
            return

        self.var_status.set("Trạng thái: HOÀN THÀNH")
        self.log_panel.add_log("-" * 40)

        if self.algo_var.get() == "AND-OR Search":
            self.var_path.set("Kế hoạch: Đã lập sơ đồ dự phòng")
            self.log_panel.add_log(">> ĐÃ LẬP XONG KẾ HOẠCH DỰ PHÒNG CHO KHÓI MÙ!")
            edges = set()

            def extract_edges(plan, current_state):
                if not plan: return
                sub_plans = plan[1]
                for next_state, sub_plan in sub_plans.items():
                    edges.add((current_state, next_state))
                    extract_edges(sub_plan, next_state)

            extract_edges(self.path, self.start_pos)
            self.renderer.draw_and_or_edges(edges)
        else:
            self.var_path.set(f"Độ dài đường đi: {len(self.path)} bước")
            self.log_panel.add_log(f">> Tổng số bước (Path Cost): {len(self.path)} bước.")
            self.renderer.draw_standard_path(self.path)


if __name__ == "__main__":
    root = tk.Tk()
    app = RescueApp(root)
    root.mainloop()