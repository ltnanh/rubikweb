import copy

# Trục xoay (Turn Axis)
U, R, F, D, L, B = range(6)

# 18 Bước xoay cơ bản (Move)
Ux1, Ux2, Ux3, Rx1, Rx2, Rx3, Fx1, Fx2, Fx3, Dx1, Dx2, Dx3, Lx1, Lx2, Lx3, Bx1, Bx2, Bx3 = range(18)

# Vị trí 8 viên góc (Corner)
URF, UFL, ULB, UBR, DFR, DLF, DBL, DRB = range(8)

# Vị trí 12 viên cạnh (Edge)
UR, UF, UL, UB, DR, DF, DL, DB, FR, FL, BL, BR = range(12)


CORNER_MOVE_MATRIX = [
    # Mặt U
    [{'c': UBR, 'o': 0}, {'c': URF, 'o': 0}, {'c': UFL, 'o': 0}, {'c': ULB, 'o': 0}, {'c': DFR, 'o': 0}, {'c': DLF, 'o': 0}, {'c': DBL, 'o': 0}, {'c': DRB, 'o': 0}],
    # Mặt R
    [{'c': DFR, 'o': 2}, {'c': UFL, 'o': 0}, {'c': ULB, 'o': 0}, {'c': URF, 'o': 1}, {'c': DRB, 'o': 1}, {'c': DLF, 'o': 0}, {'c': DBL, 'o': 0}, {'c': UBR, 'o': 2}],
    # Mặt F
    [{'c': UFL, 'o': 1}, {'c': DLF, 'o': 2}, {'c': ULB, 'o': 0}, {'c': UBR, 'o': 0}, {'c': URF, 'o': 2}, {'c': DFR, 'o': 1}, {'c': DBL, 'o': 0}, {'c': DRB, 'o': 0}],
    # Mặt D
    [{'c': URF, 'o': 0}, {'c': UFL, 'o': 0}, {'c': ULB, 'o': 0}, {'c': UBR, 'o': 0}, {'c': DLF, 'o': 0}, {'c': DBL, 'o': 0}, {'c': DRB, 'o': 0}, {'c': DFR, 'o': 0}],
    # Mặt L
    [{'c': URF, 'o': 0}, {'c': ULB, 'o': 1}, {'c': DBL, 'o': 2}, {'c': UBR, 'o': 0}, {'c': DFR, 'o': 0}, {'c': UFL, 'o': 2}, {'c': DLF, 'o': 1}, {'c': DRB, 'o': 0}],
    # Mặt B
    [{'c': URF, 'o': 0}, {'c': UFL, 'o': 0}, {'c': UBR, 'o': 1}, {'c': DRB, 'o': 2}, {'c': DFR, 'o': 0}, {'c': DLF, 'o': 0}, {'c': ULB, 'o': 2}, {'c': DBL, 'o': 1}]
]

# Tương tự với Cạnh, đổi sang {'e': UB, 'o': 0, 'oA': 1}
EDGE_MOVE_MATRIX = [ 
    # Mặt U
    [{'e': UB, 'o': 0}, {'e': UR, 'o': 0}, {'e': UF, 'o': 0}, {'e': UL, 'o': 0}, {'e': DR, 'o': 0}, {'e': DF, 'o': 0}, {'e': DL, 'o': 0}, {'e': DB, 'o': 0}, {'e': FR, 'o': 0}, {'e': FL, 'o': 0}, {'e': BL, 'o': 0}, {'e': BR, 'o': 0}],
    # Mặt R
    [{'e': FR, 'o': 0}, {'e': UF, 'o': 0}, {'e': UL, 'o': 0}, {'e': UB, 'o': 0}, {'e': BR, 'o': 0}, {'e': DF, 'o': 0}, {'e': DL, 'o': 0}, {'e': DB, 'o': 0}, {'e': DR, 'o': 0}, {'e': FL, 'o': 0}, {'e': BL, 'o': 0}, {'e': UR, 'o': 0}],
    # Mặt F
    [{'e': UR, 'o': 0}, {'e': FL, 'o': 1}, {'e': UL, 'o': 0}, {'e': UB, 'o': 0}, {'e': DR, 'o': 0}, {'e': FR, 'o': 1}, {'e': DL, 'o': 0}, {'e': DB, 'o': 0}, {'e': UF, 'o': 1}, {'e': DF, 'o': 1}, {'e': BL, 'o': 0}, {'e': BR, 'o': 0}],
    # Mặt D
    [{'e': UR, 'o': 0}, {'e': UF, 'o': 0}, {'e': UL, 'o': 0}, {'e': UB, 'o': 0}, {'e': DF, 'o': 0}, {'e': DL, 'o': 0}, {'e': DB, 'o': 0}, {'e': DR, 'o': 0}, {'e': FR, 'o': 0}, {'e': FL, 'o': 0}, {'e': BL, 'o': 0}, {'e': BR, 'o': 0}],
    # Mặt L
    [{'e': UR, 'o': 0}, {'e': UF, 'o': 0}, {'e': BL, 'o': 0}, {'e': UB, 'o': 0}, {'e': DR, 'o': 0}, {'e': DF, 'o': 0}, {'e': FL, 'o': 0}, {'e': DB, 'o': 0}, {'e': FR, 'o': 0}, {'e': UL, 'o': 0}, {'e': DL, 'o': 0}, {'e': BR, 'o': 0}],
    # Mặt B
    [{'e': UR, 'o': 0}, {'e': UF, 'o': 0}, {'e': UL, 'o': 0}, {'e': BR, 'o': 1}, {'e': DR, 'o': 0}, {'e': DF, 'o': 0}, {'e': DL, 'o': 0}, {'e': BL, 'o': 1}, {'e': FR, 'o': 0}, {'e': FL, 'o': 0}, {'e': UB, 'o': 1}, {'e': DB, 'o': 1}]
]

FACTORIALS = [1, 1, 2, 6, 24, 120, 720, 5040]



class RubikCube:
    #Initial is create a complete cube  
    def __init__(self):
        self.corners = [{'c': i, 'o': 0} for i in range(8)]
        self.edges = [{'e': i, 'o': 0} for i in range(12)]






    def verify(self):
        edge_pieces = set(e['e'] for e in self.edges)
        if len(edge_pieces) != 12 or -1 in edge_pieces:
            raise ValueError("Edge structure error: Missing, duplicate, or invalid piece colors.")
            
        corner_pieces = set(c['c'] for c in self.corners)
        if len(corner_pieces) != 8 or -1 in corner_pieces:
            raise ValueError("Corner structure error: Missing, duplicate, or invalid piece colors.")

        edge_o_sum = sum(e['o'] for e in self.edges)
        if edge_o_sum % 2 != 0:
            raise ValueError("Edge flip error: Some edges are flipped incorrectly.")

        corner_o_sum = sum(c['o'] for c in self.corners)
        if corner_o_sum % 3 != 0:
            raise ValueError("Corner twist error: Some corners are twisted incorrectly.")

        edge_inv = 0
        for i in range(11):
            for j in range(i + 1, 12):
                if self.edges[i]['e'] > self.edges[j]['e']:
                    edge_inv += 1

        corner_inv = 0
        for i in range(7):
            for j in range(i + 1, 8):
                if self.corners[i]['c'] > self.corners[j]['c']:
                    corner_inv += 1

        if (edge_inv % 2) != (corner_inv % 2):
            raise ValueError("Permutation parity error: Unsolvable state due to illegal piece swaps.")
            
        return True






    @staticmethod
    def corn_mult(a, b):
        """Nhân (kết hợp) hai ma trận góc: prod = a * b"""
        prod = [{'c': 0, 'o': 0} for _ in range(8)]
        for co in range(8):
            target_cubie_id_in_b = b[co]['c']
            prod[co]['c'] = a[target_cubie_id_in_b]['c']
            
            ori_a = a[target_cubie_id_in_b]['o']
            ori_b = b[co]['o']
            
            # Chỉ cần xử lý trường hợp ori < 3 vì các ma trận xoay và trạng thái gốc không tạo ra ori >= 3
            ori = ori_a + ori_b
            if ori >= 3: ori -= 3
            prod[co]['o'] = ori
        return prod

    @staticmethod
    def edge_mult(a, b):
        """Nhân (kết hợp) hai ma trận cạnh: prod = a * b"""
        prod = [{'e': 0, 'o': 0} for _ in range(12)] # 'oA' đã được loại bỏ
        for ed in range(12):
            target_cubie_id_in_b = b[ed]['e']
            prod[ed]['e'] = a[target_cubie_id_in_b]['e']
            
            ori = b[ed]['o'] + a[target_cubie_id_in_b]['o']
            if ori >= 2: ori -= 2 # Hướng cạnh chỉ có 0 hoặc 1
            prod[ed]['o'] = ori
        return prod


    def move_cubie(self, move_index):
        """Hàm này tự tính toán cho các cú xoay x2 (180 độ) và x3 (xoay ngược) bằng cách nhân lặp lại ma trận xoay 90 độ chuẩn."""
        axis = move_index // 3  # Lấy ra trục mặt (0:U, 1:R, 2:F, 3:D, 4:L, 5:B)
        power = move_index % 3  # Lấy số lần xoay (0: 90 độ, 1: 180 độ, 2: 270 độ ngược)

        # Trích xuất ma trận xoay thô 90 độ của mặt tương ứng
        raw_corner_move = CORNER_MOVE_MATRIX[axis]
        raw_edge_move = EDGE_MOVE_MATRIX[axis]

        # Khởi tạo ma trận tích lũy dựa theo số lần xoay (power)
        final_corner_move = copy.deepcopy(raw_corner_move)
        final_edge_move = copy.deepcopy(raw_edge_move)

        # Nếu xoay 180 độ (power=1) hoặc 270 độ (power=2), ta nhân dồn ma trận thô vào
        for _ in range(power):
            final_corner_move = self.corn_mult(raw_corner_move, final_corner_move)
            final_edge_move = self.edge_mult(raw_edge_move, final_edge_move)

        # Áp dụng ma trận biến đổi cuối cùng lên cấu trúc hiện tại của khối Rubik
        self.corners = self.corn_mult(self.corners, final_corner_move)
        self.edges = self.edge_mult(self.edges, final_edge_move)






    #Nén định hướng của 8 viên góc thành 1 con số từ 0 đến 2186 (3^7 - 1).Bỏ qua viên cuối cùng (DRB) vì hướng của nó bị ràng buộc bởi 7 viên trước.
    def get_corner_orientation_coord(self):
        s = 0
        for co in range(7):
            s = 3 * s + self.corners[co]['o']
        return s
    
    #Nén định hướng của 12 viên cạnh thành 1 con số từ 0 đến 2047 (2^11 - 1).Bỏ qua viên cuối cùng (BR) vì hướng chẵn lẻ bị ràng buộc bởi 11 viên trước.
    def get_edge_orientation_coord(self):
        s = 0
        for ed in range(11):
            s = 2 * s + self.edges[ed]['o']
        return s


    #Nén vị trí của 4 viên cạnh tầng giữa (FR, FL, BL, BR) thành 1 con số từ 0 đến 494.Hàm này tính toán tổ hợp C(12, 4) = 495 để xem 4 viên này đang nằm ở những ô đỗ nào.
    def get_ud_slice_coord(self):
        # Hàm tính tổ hợp C(n, k) nhanh
        def n_choose_k(n, k):
            if k < 0 or k > n: return 0
            if k == 0 or k == n: return 1
            if k > n // 2: k = n - k
            res = 1
            for i in range(1, k + 1):
                res = res * (n - i + 1) // i
            return res

        coord = 0
        k = 3  # Chúng ta có 4 viên cạnh tầng giữa (chỉ số đếm từ 3 xuống 0)
        
        # Quét ngược từ vị trí ô đỗ BR (11) về UR (0)
        for ed in range(11, -1, -1):
            # Kiểm tra xem viên đang đỗ tại ô 'ed' có phải là 1 trong 4 viên tầng giữa gốc không
            # 4 viên cạnh tầng giữa gốc có ID là: FR(8), FL(9), BL(10), BR(11)
            if self.edges[ed]['e'] >= 8:
                coord += n_choose_k(ed, k + 1)
                k -= 1
        # Trả về 494 - coord để trạng thái đã giải (coord=494) trở thành 0.
        return 494 - coord
    
    
    #Giải nén số tọa độ từ 0..2186 để đặt lại hướng cho 8 viên góc
    def set_corner_orientation_coord(self, coord: int):
        ori_sum = 0
        # Giải nén ngược từ vị trí ô đỗ số 6 về 0
        for co in range(6, -1, -1):
            ori = coord % 3
            self.corners[co]['o'] = ori
            ori_sum += ori
            coord //= 3
        # Viên cuối cùng (DRB - chỉ số 7) chịu ràng buộc bảo toàn hướng
        self.corners[7]['o'] = (3 - ori_sum % 3) % 3


    #Giải nén số tọa độ từ 0..2047 để đặt lại hướng cho 12 viên cạnh
    def set_edge_orientation_coord(self, coord: int):
        ori_sum = 0
        # Giải nén ngược từ vị trí ô đỗ số 10 về 0
        for ed in range(10, -1, -1):
            ori = coord % 2
            self.edges[ed]['o'] = ori
            ori_sum += ori
            coord //= 2
        # Viên cuối cùng (BR - chỉ số 11) chịu ràng buộc bảo toàn hướng chẵn lẻ
        self.edges[11]['o'] = (2 - ori_sum % 2) % 2



    #Giải nén số tọa độ từ 0..494 để xếp 4 viên tầng giữa vào đúng vị trí 
    def set_ud_slice_coord(self, coord: int):
        # Chuyển đổi ngược lại từ tọa độ mới (đích 0) về tọa độ cũ (đích 494)
        coord = 494 - coord

        # Khởi tạo toàn bộ 12 cạnh là trống (-1)
        for ed in range(12):
            self.edges[ed]['e'] = -1
            
        def n_choose_k(n, k):
            if k < 0 or k > n: return 0
            if k == 0 or k == n: return 1
            if k > n // 2: k = n - k
            res = 1
            for i in range(1, k + 1): res = res * (n - i + 1) // i
            return res

        k = 3
        # Xếp 4 viên tầng giữa (ID: 8, 9, 10, 11) vào các vị trí ô đỗ theo toán tổ hợp
        for ed in range(11, -1, -1):
            val = n_choose_k(ed, k + 1)
            if coord >= val:
                coord -= val
                self.edges[ed]['e'] = 8 + k # Đặt viên tầng giữa vào
                k -= 1
        
        # Điền nốt các viên cạnh còn lại (0..7) vào những vị trí trống còn lại
        current_edge = 0
        for ed in range(12):
            if self.edges[ed]['e'] == -1:
                self.edges[ed]['e'] = current_edge
                current_edge += 1






    #Nén hoán vị của 8 viên góc thành số từ 0 đến 40319
    def get_corner_permutation_coord(self):
        coord = 0
        for i in range(7):
            smaller = 0
            for j in range(i + 1, 8):
                if self.corners[j]['c'] < self.corners[i]['c']:
                    smaller += 1
            coord += smaller * FACTORIALS[7 - i]
        return coord


    
    def set_corner_permutation_coord(self, coord: int):
        available = list(range(8))
        for i in range(7):
            fact = FACTORIALS[7 - i]
            idx = coord // fact
            self.corners[i]['c'] = available.pop(idx)
            coord %= fact
        self.corners[7]['c'] = available[0]
        for i in range(8): 
            self.corners[i]['o'] = 0


    #Nén hoán vị của 8 viên cạnh mặt U/D (vị trí 0..7) thành số từ 0 đến 40319
    def get_edge8_permutation_coord(self):
        coord = 0
        for i in range(7):
            smaller = 0
            for j in range(i + 1, 8):
                if self.edges[j]['e'] < self.edges[i]['e']:
                    smaller += 1
            coord += smaller * FACTORIALS[7 - i]
        return coord


    def set_edge8_permutation_coord(self, coord: int):
        available = list(range(8))
        for i in range(7):
            fact = FACTORIALS[7 - i]
            idx = coord // fact
            self.edges[i]['e'] = available.pop(idx)
            coord %= fact
        self.edges[7]['e'] = available[0]
        for i in range(8): 
            self.edges[i]['o'] = 0


    #Nén hoán vị của 4 viên cạnh tầng giữa (vị trí 8..11) thành số từ 0 đến 23
    def get_edge4_permutation_coord(self):
        perm = [self.edges[i]['e'] - 8 for i in range(8, 12)]
        coord = 0
        for i in range(3):
            smaller = 0
            for j in range(i + 1, 4):
                if perm[j] < perm[i]:
                    smaller += 1
            coord += smaller * FACTORIALS[3 - i]
        return coord


    def set_edge4_permutation_coord(self, coord: int):
        available = list(range(8, 12))  # ID của các viên là 8, 9, 10, 11
        for i in range(3):
            fact = FACTORIALS[3 - i]
            idx = coord // fact
            self.edges[8 + i]['e'] = available.pop(idx)
            coord %= fact
        self.edges[11]['e'] = available[0]

        # Đặt 8 viên cạnh còn lại vào vị trí gốc của chúng
        for i in range(8):
            self.edges[i]['e'] = i

        # Reset hướng của tất cả các cạnh
        for i in range(12):
            self.edges[i]['o'] = 0