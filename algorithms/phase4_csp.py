import random

def backtracking_search(map_grid, start_pos, goal_pos):
    variables = ['Nạn nhân A', 'Nạn nhân B', 'Nạn nhân C', 'Nạn nhân D']
    domains = {var: [1, 0] for var in variables}
    csp = {'variables': variables, 'domains': domains, 'max_kits': 2}
    history = []
    step_info = {'count': 1}

    # Sinh ngẫu nhiên trạng thái nạn nhân
    victim_statuses = {var: random.choice(['Nặng', 'Nhẹ']) for var in variables}
    status_str = " | ".join([f"{k.split()[-1]}: {v}" for k, v in victim_statuses.items()])

    # B1: Khởi tạo
    history.append({
        'message': f"=== CHẠY THUẬT TOÁN BACKTRACKING ===\n[Khám lâm sàng]: {status_str}\nB1: Khởi tạo\n- Assignment = {{}}\n" + "-" * 30,
        'assignment': {}, 'focus': None, 'status': 'init', 'victim_statuses': victim_statuses
    })

    def is_complete(assignment):
        return len(assignment) == len(variables)

    def select_unassigned_variable(variables, assignment):
        for var in variables:
            if var not in assignment: return var
        return None

    def get_consistency_check(var, value, assignment, csp):
        temp = assignment.copy()
        temp[var] = value

        status = victim_statuses[var]

        if value == 1:  # Nếu Robot ĐỊNH CỨU
            if status == 'Nhẹ':
                return False, "(Do nạn nhân chỉ bị thương nhẹ, không cần túi y tế)"
            if sum(temp.values()) > csp['max_kits']:
                return False, "(Do đã sử dụng hết 2 túi y tế)"

        elif value == 0:  # Nếu Robot ĐỊNH BỎ QUA
            pass  # Luôn hợp lệ (Bỏ qua vì nhẹ, hoặc bỏ qua vì nặng nhưng hết thuốc)

        return True, ""

    def format_assign(assignment):
        items = [f"{k}={'Cứu' if v == 1 else 'Bỏ qua'}" for k, v in assignment.items()]
        return "{" + ", ".join(items) + "}"

    def recursive_backtracking(assignment):
        if is_complete(assignment): return assignment

        var = select_unassigned_variable(csp['variables'], assignment)
        step_info['count'] += 1
        c_step = step_info['count']

        history.append({
            'message': f"B{c_step}: Chọn biến {var} (Tình trạng: {victim_statuses[var]})",
            'assignment': assignment.copy(), 'focus': var, 'status': 'checking', 'victim_statuses': victim_statuses
        })

        for i, value in enumerate(csp['domains'][var]):
            val_str = "Cứu" if value == 1 else "Bỏ qua"
            prefix = "- Gán giá trị cho" if i == 0 else "- Thử giá trị khác:"
            temp_assign = assignment.copy()
            temp_assign[var] = value

            history.append({
                'message': f"{prefix} {var} = {val_str}",
                'assignment': temp_assign, 'focus': var, 'status': 'checking', 'victim_statuses': victim_statuses
            })

            is_valid, reason = get_consistency_check(var, value, assignment, csp)

            if is_valid:
                history.append({
                    'message': "- Kiểm tra ràng buộc => Thỏa",
                    'assignment': temp_assign, 'focus': var, 'status': 'valid', 'victim_statuses': victim_statuses
                })
                assignment[var] = value
                history.append({
                    'message': f"- Assignment = {format_assign(assignment)}\n" + "-" * 30,
                    'assignment': assignment.copy(), 'focus': None, 'status': 'init', 'victim_statuses': victim_statuses
                })

                result = recursive_backtracking(assignment)
                if result != "failure": return result

                step_info['count'] += 1
                history.append({
                    'message': f"B{step_info['count']}: QUAY LUI (Backtrack)\n- Phát hiện ngõ cụt, gỡ bỏ {var} = {val_str}\n" + "-" * 30,
                    'assignment': assignment.copy(), 'focus': var, 'status': 'backtrack',
                    'victim_statuses': victim_statuses
                })
                del assignment[var]
            else:
                history.append({
                    'message': f"- Kiểm tra ràng buộc => Vi phạm {reason}",
                    'assignment': temp_assign, 'focus': var, 'status': 'invalid', 'victim_statuses': victim_statuses
                })

        return "failure"

    final_assignment = recursive_backtracking({})
    if final_assignment != "failure":
        history.append({
            'message': "=> HOÀN THÀNH THUẬT TOÁN\n--- KẾT THÚC ---",
            'assignment': final_assignment, 'focus': None, 'status': 'init', 'victim_statuses': victim_statuses
        })

    return [], history

def forward_checking_search(map_grid, start_pos, goal_pos):
    variables = ['Nạn nhân A', 'Nạn nhân B', 'Nạn nhân C', 'Nạn nhân D']
    domains = {var: [1, 0] for var in variables}
    csp = {'variables': variables, 'domains': domains, 'max_kits': 2}
    history = []
    step_info = {'count': 1}

    # Sinh ngẫu nhiên trạng thái nạn nhân
    victim_statuses = {var: random.choice(['Nặng', 'Nhẹ']) for var in variables}
    status_str = " | ".join([f"{k.split()[-1]}: {v}" for k, v in victim_statuses.items()])

    history.append({
        'message': f"=== CHẠY THUẬT TOÁN FORWARD CHECKING ===\n[Khám lâm sàng]: {status_str}\nB1: Khởi tạo\n- Assignment = {{}}\n" + "-" * 30,
        'assignment': {}, 'focus': None, 'status': 'init', 'victim_statuses': victim_statuses
    })

    def is_complete(assignment):
        return len(assignment) == len(variables)

    def select_unassigned_variable(variables, assignment):
        for var in variables:
            if var not in assignment:
                return var
        return None

    def get_consistency_check(var, value, assignment, csp):
        temp = assignment.copy()
        temp[var] = value
        status = victim_statuses[var]

        if value == 1:  # Cứu
            if status == 'Nhẹ':
                return False, "(Do nạn nhân chỉ bị thương nhẹ, không cần túi y tế)"
            if sum(temp.values()) > csp['max_kits']:
                return False, "(Do đã sử dụng hết 2 túi y tế)"
        # value == 0 luôn hợp lệ
        return True, ""

    # Forward Checking: kiểm tra các biến chưa gán, loại bỏ giá trị vi phạm
    def forward_check(var, value, assignment, domains):
        new_domains = {v: list(domains[v]) for v in domains}
        # Gán tạm
        temp_assign = assignment.copy()
        temp_assign[var] = value
        # Xóa giá trị không hợp lệ cho các biến chưa gán
        for unassigned in variables:
            if unassigned not in assignment and unassigned != var:
                # Thử từng giá trị trong miền
                for val in list(new_domains[unassigned]):
                    # Kiểm tra ràng buộc với phép gán hiện tại + giá trị thử
                    # (chỉ kiểm tra ràng buộc liên quan đến số túi y tế và tình trạng)
                    # Đơn giản: nếu val == 1 và tổng số túi dùng > max_kits thì loại
                    # Nếu val == 1 và nạn nhân nhẹ thì loại (nhưng đây là ràng buộc cục bộ)
                    # Ta kiểm tra toàn cục:
                    temp_check = temp_assign.copy()
                    temp_check[unassigned] = val
                    if sum(temp_check.values()) > csp['max_kits']:
                        new_domains[unassigned].remove(val)
                    elif val == 1 and victim_statuses[unassigned] == 'Nhẹ':
                        new_domains[unassigned].remove(val)
                    # Ngoài ra, nếu val == 0 thì luôn hợp lệ (không cần kiểm tra)
                # Nếu miền rỗng => thất bại
                if not new_domains[unassigned]:
                    return False, new_domains
        return True, new_domains

    def format_assign(assignment):
        items = [f"{k}={'Cứu' if v == 1 else 'Bỏ qua'}" for k, v in assignment.items()]
        return "{" + ", ".join(items) + "}"

    def recursive_forward_checking(assignment, domains):
        if is_complete(assignment):
            return assignment

        var = select_unassigned_variable(csp['variables'], assignment)
        step_info['count'] += 1
        c_step = step_info['count']

        history.append({
            'message': f"B{c_step}: Chọn biến {var} (Tình trạng: {victim_statuses[var]})",
            'assignment': assignment.copy(), 'focus': var, 'status': 'checking',
            'victim_statuses': victim_statuses
        })

        for value in domains[var]:
            val_str = "Cứu" if value == 1 else "Bỏ qua"
            prefix = "- Gán giá trị cho" if domains[var].index(value) == 0 else "- Thử giá trị khác:"
            temp_assign = assignment.copy()
            temp_assign[var] = value

            history.append({
                'message': f"{prefix} {var} = {val_str}",
                'assignment': temp_assign, 'focus': var, 'status': 'checking',
                'victim_statuses': victim_statuses
            })

            # Kiểm tra ràng buộc cục bộ
            is_valid, reason = get_consistency_check(var, value, assignment, csp)
            if not is_valid:
                history.append({
                    'message': f"- Kiểm tra ràng buộc => Vi phạm {reason}",
                    'assignment': temp_assign, 'focus': var, 'status': 'invalid',
                    'victim_statuses': victim_statuses
                })
                continue

            # Forward Checking
            fc_ok, new_domains = forward_check(var, value, assignment, domains)
            if not fc_ok:
                history.append({
                    'message': f"- Forward Checking => Phát hiện miền rỗng cho biến khác. Cắt nhánh.",
                    'assignment': temp_assign, 'focus': var, 'status': 'invalid',
                    'victim_statuses': victim_statuses
                })
                continue

            history.append({
                'message': f"- Forward Checking => OK. Miền còn lại: { {v: new_domains[v] for v in new_domains if v != var} }",
                'assignment': temp_assign, 'focus': var, 'status': 'valid',
                'victim_statuses': victim_statuses
            })

            assignment[var] = value
            history.append({
                'message': f"- Assignment = {format_assign(assignment)}\n" + "-" * 30,
                'assignment': assignment.copy(), 'focus': None, 'status': 'init',
                'victim_statuses': victim_statuses
            })

            result = recursive_forward_checking(assignment, new_domains)
            if result != "failure":
                return result

            step_info['count'] += 1
            history.append({
                'message': f"B{step_info['count']}: QUAY LUI (Backtrack)\n- Phát hiện ngõ cụt, gỡ bỏ {var} = {val_str}\n" + "-" * 30,
                'assignment': assignment.copy(), 'focus': var, 'status': 'backtrack',
                'victim_statuses': victim_statuses
            })
            del assignment[var]

        return "failure"

    final_assignment = recursive_forward_checking({}, {v: list(domains[v]) for v in domains})
    if final_assignment != "failure":
        history.append({
            'message': "=> HOÀN THÀNH THUẬT TOÁN (Forward Checking)\n--- KẾT THÚC ---",
            'assignment': final_assignment, 'focus': None, 'status': 'init',
            'victim_statuses': victim_statuses
        })

    return [], history