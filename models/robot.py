# models/robot.py

class Robot:
    def __init__(self, start_pos, initial_energy=100, medical_kits=3):
        """
        Khởi tạo Robot cứu hộ với các thông số cơ bản
        """
        self.position = tuple(start_pos)
        self.energy = initial_energy
        self.medical_kits = medical_kits
        self.is_active = True

    def move_to(self, new_pos, energy_cost=1):
        """
        Cập nhật vị trí của Robot và trừ đi năng lượng.
        Trả về False nếu Robot hết năng lượng không thể di chuyển tiếp.
        """
        if self.energy >= energy_cost:
            self.position = tuple(new_pos)
            self.energy -= energy_cost
            if self.energy <= 0:
                self.is_active = False
            return True
        else:
            self.is_active = False
            return False

    def use_medical_kit(self):
        """
        Sử dụng túi y tế để cứu nạn nhân.
        """
        if self.medical_kits > 0:
            self.medical_kits -= 1
            return True
        return False

    def get_status_string(self):
        """
        Trả về chuỗi trạng thái để in ra giao diện Log
        """
        return f"Năng lượng: {self.energy}% | Túi y tế: {self.medical_kits}"