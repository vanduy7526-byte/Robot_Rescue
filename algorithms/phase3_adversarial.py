from config import WALL
from collections import deque

def minimax_search(map_grid, start_pos, goal_pos, fire_start_pos):
    history = []
    MAX_DEPTH = 4

    robot_pos = start_pos
    fire_pos = fire_start_pos
    path = [robot_pos]
    turn = 1

    def get_valid_moves(pos):
        moves = []
        x, y = pos
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(map_grid.grid[0]) and 0 <= ny < len(map_grid.grid):
                if map_grid.grid[ny][nx] != WALL:
                    moves.append((nx, ny))
        return moves

    # BƯỚC 1: TIỀN XỬ LÝ - TẠO BẢN ĐỒ KHOẢNG CÁCH THỰC TẾ (BFS)
    dist_map = {}
    queue = deque([(goal_pos, 0)])
    visited = set([goal_pos])
    while queue:
        curr, d = queue.popleft()
        dist_map[curr] = d
        for move in get_valid_moves(curr):
            if move not in visited:
                visited.add(move)
                queue.append((move, d + 1))

    # BƯỚC 2: IN LUẬT CHƠI RA NHẬT KÝ ĐẦU TIÊN
    intro_message = (
        "1. Tốc độ: Robot đi 1 bước/lượt. Lửa lan 1 bước/2 lượt.\n"
        "2. Cách tính điểm:\n"
        "   + Cứu được người: Nhận ngay +9999 điểm.\n"
        "   + Bị lửa thiêu rụi: Nhận ngay -9999 điểm.\n"
        "   + Khi di chuyển 1 ô: Điểm = 1000 - (Khoảng cách tới đích x20) + (Khoảng cách né lửa x5).\n"
        "   + Nếu robot định dẫm lại đường cũ, trừ 200 điểm\n"
        "=================================================="
    )
    history.append({
        'message': intro_message,
        'robot_pos': robot_pos, 'fire_pos': fire_pos
    })

    # HÀM HEURISTIC
    def heuristic_value(r_pos, f_pos, current_imagined_path, real_path):
        dist_to_goal = dist_map.get(r_pos, 999)
        dist_to_fire = abs(r_pos[0] - f_pos[0]) + abs(r_pos[1] - f_pos[1])

        score = 1000 - (dist_to_goal * 20) + (dist_to_fire * 5)

        for step in current_imagined_path:
            if step in real_path:
                score -= 200
        return score

    # MINIMAX
    def minimax(r_pos, f_pos, depth, is_maximizing, current_imagined_path):
        if r_pos == f_pos: return -9999, None
        if r_pos == goal_pos: return 9999, None
        if depth == 0:
            score = heuristic_value(r_pos, f_pos, current_imagined_path, path)
            return score, None

        if is_maximizing:
            best_value = -float('inf')
            valid_moves = get_valid_moves(r_pos)
            best_move = valid_moves[0] if valid_moves else None
            for move in valid_moves:
                val, _ = minimax(move, f_pos, depth - 1, False, current_imagined_path + [move])
                if val > best_value:
                    best_value, best_move = val, move
            return best_value, best_move
        else:
            best_value = float('inf')
            valid_moves = get_valid_moves(f_pos)
            best_move = valid_moves[0] if valid_moves else None
            for move in valid_moves:
                val, _ = minimax(r_pos, move, depth - 1, True, current_imagined_path)
                if val < best_value:
                    best_value, best_move = val, move
            return best_value, best_move

    # ================= VÒNG LẶP TRÒ CHƠI THỰC TẾ =================
    while True:
        history.append({
            'message': f"\n======= LƯỢT {turn} ========\n"
                       f"Vị trí hiện tại: Robot{robot_pos} và Lửa{fire_pos}\n"
                       f"Robot đang tính toán nước đi...",
            'robot_pos': robot_pos, 'fire_pos': fire_pos
        })

        best_score, best_move = minimax(robot_pos, fire_pos, MAX_DEPTH, True, [])

        if not best_move:
            history.append(
                {'message': "Robot đã bị ép góc và không còn đường nào để đi.", 'robot_pos': robot_pos,
                 'fire_pos': fire_pos})
            break

        robot_pos = best_move
        path.append(robot_pos)

        # Log di chuyển của Robot
        history.append({
            'message': f"Robot di chuyển tới {robot_pos}: {best_score} điểm",
            'robot_pos': robot_pos, 'fire_pos': fire_pos,
            'commit_robot': robot_pos
        })

        if robot_pos == goal_pos:
            history.append(
                {'message': "\nRobot đã cứu được nạn nhân!", 'robot_pos': robot_pos, 'fire_pos': fire_pos})
            break
        if robot_pos == fire_pos:
            history.append(
                {'message': "\nRobot bị lửa thiêu...", 'robot_pos': robot_pos,
                 'fire_pos': fire_pos})
            break

        # BƯỚC ĐI CỦA LỬA
        if turn % 2 != 0:
            fire_moves = get_valid_moves(fire_pos)
            if fire_moves:
                best_fire = min(fire_moves, key=lambda m: abs(m[0] - robot_pos[0]) + abs(m[1] - robot_pos[1]))
                fire_pos = best_fire
                history.append({
                    'message': f"Lửa lan rộng sang {fire_pos}",
                    'robot_pos': robot_pos, 'fire_pos': fire_pos,
                    'commit_fire': fire_pos
                })
        else:
            history.append({
                'message': f"Lửa đang đứng yên, chưa lan rộng",
                'robot_pos': robot_pos, 'fire_pos': fire_pos
            })

        if robot_pos == fire_pos:
            history.append(
                {'message': "\nRobot bị lửa thiêu...", 'robot_pos': robot_pos, 'fire_pos': fire_pos})
            break

        turn += 1
        if turn > 60:
            history.append(
                {'message': "\nHai bên giằng co quá lâu.", 'robot_pos': robot_pos, 'fire_pos': fire_pos})
            break
    return path, history

def alpha_beta_search(map_grid, start_pos, goal_pos, fire_start_pos):
    history = []
    MAX_DEPTH = 4

    robot_pos = start_pos
    fire_pos = fire_start_pos
    path = [robot_pos]
    turn = 1

    def get_valid_moves(pos):
        moves = []
        x, y = pos
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(map_grid.grid[0]) and 0 <= ny < len(map_grid.grid):
                if map_grid.grid[ny][nx] != WALL:
                    moves.append((nx, ny))
        return moves

    # BFS dist_map
    dist_map = {}
    queue = deque([(goal_pos, 0)])
    visited = set([goal_pos])
    while queue:
        curr, d = queue.popleft()
        dist_map[curr] = d
        for move in get_valid_moves(curr):
            if move not in visited:
                visited.add(move)
                queue.append((move, d + 1))

    intro_message = (
        "1. Tốc độ: Robot đi 1 bước/lượt. Lửa lan 1 bước/2 lượt.\n"
        "2. Cách tính điểm:\n"
        "   + Cứu được người: Nhận ngay +9999 điểm.\n"
        "   + Bị lửa thiêu rụi: Nhận ngay -9999 điểm.\n"
        "   + Khi di chuyển 1 ô: Điểm = 1000 - (Khoảng cách tới đích x20) + (Khoảng cách né lửa x5).\n"
        "   + Nếu robot định dẫm lại đường cũ, trừ 200 điểm\n"
        "=================================================="
    )
    history.append({
        'message': intro_message,
        'robot_pos': robot_pos, 'fire_pos': fire_pos
    })

    def heuristic_value(r_pos, f_pos, current_imagined_path, real_path):
        dist_to_goal = dist_map.get(r_pos, 999)
        dist_to_fire = abs(r_pos[0] - f_pos[0]) + abs(r_pos[1] - f_pos[1])
        score = 1000 - (dist_to_goal * 20) + (dist_to_fire * 5)
        for step in current_imagined_path:
            if step in real_path:
                score -= 200
        return score

    # Alpha-Beta
    def alpha_beta(r_pos, f_pos, depth, is_maximizing, alpha, beta, current_imagined_path):
        if r_pos == f_pos:
            return -9999, None
        if r_pos == goal_pos:
            return 9999, None
        if depth == 0:
            return heuristic_value(r_pos, f_pos, current_imagined_path, path), None

        if is_maximizing:
            best_value = -float('inf')
            valid_moves = get_valid_moves(r_pos)
            best_move = valid_moves[0] if valid_moves else None
            for move in valid_moves:
                val, _ = alpha_beta(move, f_pos, depth - 1, False, alpha, beta,
                                    current_imagined_path + [move])
                if val > best_value:
                    best_value, best_move = val, move
                alpha = max(alpha, best_value)
                if alpha >= beta:
                    break
            return best_value, best_move
        else:
            best_value = float('inf')
            valid_moves = get_valid_moves(f_pos)
            best_move = valid_moves[0] if valid_moves else None
            for move in valid_moves:
                val, _ = alpha_beta(r_pos, move, depth - 1, True, alpha, beta,
                                    current_imagined_path)
                if val < best_value:
                    best_value, best_move = val, move
                beta = min(beta, best_value)
                if alpha >= beta:
                    break
            return best_value, best_move

    while True:
        history.append({
            'message': f"\n======= LƯỢT {turn} ========\n"
                       f"Vị trí hiện tại: Robot{robot_pos} và Lửa{fire_pos}\n"
                       f"Robot đang tính toán với Alpha-Beta...",
            'robot_pos': robot_pos, 'fire_pos': fire_pos
        })

        best_score, best_move = alpha_beta(robot_pos, fire_pos, MAX_DEPTH, True, -float('inf'), float('inf'), [])

        if not best_move:
            history.append(
                {'message': "Robot đã bị ép góc và không còn đường nào để đi.",
                 'robot_pos': robot_pos, 'fire_pos': fire_pos})
            break

        robot_pos = best_move
        path.append(robot_pos)

        history.append({
            'message': f"Robot di chuyển tới {robot_pos}: {best_score} điểm",
            'robot_pos': robot_pos, 'fire_pos': fire_pos,
            'commit_robot': robot_pos
        })

        if robot_pos == goal_pos:
            history.append(
                {'message': "\nRobot đã cứu được nạn nhân!",
                 'robot_pos': robot_pos, 'fire_pos': fire_pos})
            break
        if robot_pos == fire_pos:
            history.append(
                {'message': "\nRobot bị lửa thiêu...",
                 'robot_pos': robot_pos, 'fire_pos': fire_pos})
            break

        # Lửa di chuyển (mỗi 2 lượt)
        if turn % 2 != 0:
            fire_moves = get_valid_moves(fire_pos)
            if fire_moves:
                best_fire = min(fire_moves, key=lambda m: abs(m[0] - robot_pos[0]) + abs(m[1] - robot_pos[1]))
                fire_pos = best_fire
                history.append({
                    'message': f"Lửa lan rộng sang {fire_pos}",
                    'robot_pos': robot_pos, 'fire_pos': fire_pos,
                    'commit_fire': fire_pos
                })
        else:
            history.append({
                'message': f"Lửa đang đứng yên, chưa lan rộng",
                'robot_pos': robot_pos, 'fire_pos': fire_pos
            })

        if robot_pos == fire_pos:
            history.append(
                {'message': "\nRobot bị lửa thiêu...",
                 'robot_pos': robot_pos, 'fire_pos': fire_pos})
            break

        turn += 1
        if turn > 60:
            history.append(
                {'message': "\nHai bên giằng co quá lâu.",
                 'robot_pos': robot_pos, 'fire_pos': fire_pos})
            break

    return path, history