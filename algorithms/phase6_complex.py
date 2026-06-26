from models.node import get_moves
from collections import deque
from config import WALL

def make_move(current_node, new_pos):
    return {
        'state': tuple(new_pos),
        'parent': current_node,
        'path_cost': current_node.get('path_cost', 0) + 1
    }


def and_or_graph_search(map_grid, start_pos, goal_pos):
    goal = tuple(goal_pos)
    start = {'state': tuple(start_pos), 'path_cost': 0, 'parent': None}
    history = []
    memo = {}

    def get_non_deterministic_results(state_node, action):
        correct_node = make_move(state_node, action)
        correct_node['branch_type'] = "Nhánh đúng"
        results = [correct_node]

        valid_moves = get_moves(state_node['state'], map_grid)
        other_moves = [m for m in valid_moves if tuple(m) != tuple(action)]
        if other_moves:
            slip_action = other_moves[0]
            slip_node = make_move(state_node, slip_action)
            slip_node['branch_type'] = "Nhánh sai"
            results.append(slip_node)

        return results

    def or_search(state_node, path_states, depth):
        current_state = state_node['state']
        indent = "  " * depth

        # 1. KIỂM TRA BỘ NHỚ TRƯỚC KHI TÍNH TOÁN
        if current_state in memo:
            result = memo[current_state]
            status = "Kế hoạch Thất bại" if result == "failure" else "Đã có Kế hoạch"
            history.append({
                'type': 'INFO',
                'state': current_state,
                'message': f"{indent}* [ĐÃ DUYỆT TRƯỚC ĐÓ] {current_state} -> {status}. Bỏ qua tính lại!"
            })
            return result

        history.append({
            'type': 'OR',
            'state': current_state,
            'message': f"{indent}[OR] Đang ở: {current_state}"
        })

        # 2. KIỂM TRA ĐÍCH
        if current_state == goal:
            history.append({
                'type': 'SUCCESS',
                'state': current_state,
                'message': f"{indent}  => ĐÃ TỚI ĐÍCH AN TOÀN!"
            })
            memo[current_state] = []  # Ghi nhớ: Tới đích thì kế hoạch là rỗng
            return []

        # 3. KIỂM TRA VÒNG LẶP / GIỚI HẠN SÂU
        if current_state in path_states or depth > 10:
            history.append({
                'type': 'FAIL',
                'state': current_state,
                'message': f"{indent}  => Cắt nhánh (Lặp vòng / Quá sâu)"
            })
            # KHÔNG ghi nhớ (memo) lỗi này vì đây là lỗi do đi đường vòng,
            # đi đường khác ngắn hơn có thể vẫn tới được.
            return "failure"

        # 4. DUYỆT CÁC HÀNH ĐỘNG
        actions = get_moves(current_state, map_grid)
        for action in actions:
            result_states = get_non_deterministic_results(state_node, action)

            history.append({
                'type': 'AND',
                'state': current_state,
                'message': f"{indent}> [AND] Di chuyển sang: {tuple(action)}"
            })

            for s in result_states:
                b_type = s.get('branch_type', 'Nhánh đúng')
                history.append({
                    'type': 'INFO',
                    'state': current_state,
                    'message': f"{indent}    + {b_type}: {s['state']}"
                })

            plan = and_search(result_states, path_states + [current_state], depth)

            # Nếu tìm được kế hoạch an toàn
            if plan != "failure":
                memo[current_state] = [action, plan]  # Ghi nhớ KẾT QUẢ TỐT
                return [action, plan]

        # Nếu thử mọi cách đều chết
        memo[current_state] = "failure"  # Ghi nhớ KẾT QUẢ XẤU
        return "failure"

    def and_search(states, path_states, depth):
        plans = {}
        indent = "  " * depth

        for s_node in states:
            s_state = s_node['state']
            b_type = s_node.get('branch_type', 'Nhánh đúng')

            history.append({
                'type': 'INFO',
                'state': s_state,
                'message': f"{indent}  [Xét nhánh rủi ro] Rơi vào: {s_state} ({b_type})"
            })

            plan_s = or_search(s_node, path_states, depth + 1)

            if plan_s == "failure":
                history.append({
                    'type': 'FAIL',
                    'state': s_state,
                    'message': f"{indent}  => {b_type} thất bại! HỦY TOÀN BỘ lệnh đi này."
                })
                return "failure"

            plans[s_state] = plan_s

        return plans

    final_plan = or_search(start, [], 0)

    if final_plan == "failure":
        return [], history

    return final_plan, history

def sensorless_search(map_grid, start_pos, goal_pos):
    """
    Tìm kiếm không cảm biến (belief state) sử dụng BFS.
    Mỗi belief là một tập hợp các vị trí có thể của robot.
    Hành động là một trong 4 hướng.
    """
    goal = tuple(goal_pos)
    start_belief = frozenset([tuple(start_pos)])
    goal_belief = frozenset([goal])

    # Hàng đợi BFS: (belief, path_actions, parent_belief, action)
    queue = deque()
    queue.append((start_belief, [], None, None))
    visited = {start_belief}
    history = []

    # Hàm chuyển trạng thái belief theo một hướng
    def transition(belief, direction):
        new_belief = set()
        dx, dy = direction
        for (x, y) in belief:
            nx, ny = x + dx, y + dy
            # Kiểm tra hợp lệ
            if 0 <= nx < len(map_grid.grid[0]) and 0 <= ny < len(map_grid.grid):
                if map_grid.grid[ny][nx] != WALL:  # WALL import từ config
                    new_belief.add((nx, ny))
                else:
                    # Nếu không thể di chuyển, đứng yên
                    new_belief.add((x, y))
            else:
                new_belief.add((x, y))
        return frozenset(new_belief)

    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # Lên, Xuống, Trái, Phải

    while queue:
        belief, actions, parent_belief, action = queue.popleft()
        history.append({
            'belief': set(belief),
            'actions': actions,
            'action': action,
            'parent_belief': parent_belief
        })

        # Kiểm tra nếu belief chỉ chứa goal (chắc chắn đến đích)
        if belief == goal_belief or belief == frozenset([goal]):
            # Xây dựng đường đi (các vị trí dự kiến)
            path = [start_pos]
            # Tái tạo path từ actions
            current_pos = start_pos
            for act in actions:
                dx, dy = act
                nx, ny = current_pos[0] + dx, current_pos[1] + dy
                if 0 <= nx < len(map_grid.grid[0]) and 0 <= ny < len(map_grid.grid) and map_grid.grid[ny][nx] != WALL:
                    current_pos = (nx, ny)
                # Nếu không hợp lệ thì đứng yên (nhưng trong kế hoạch vẫn ghi vị trí cũ)
                path.append(current_pos)
            return path, history

        # Mở rộng các hành động
        for dir_vec in directions:
            new_belief = transition(belief, dir_vec)
            if new_belief not in visited:
                visited.add(new_belief)
                new_actions = actions + [dir_vec]
                queue.append((new_belief, new_actions, belief, dir_vec))

    return [], history