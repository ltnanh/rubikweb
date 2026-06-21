import pickle
import os
import time
from RubikCube import RubikCube
import sys 
from RubikCUbeFacelet import FaceletCube
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__)))) 


FACTORIALS = [1, 1, 2, 6, 24, 120, 720, 5040]

MOVE_NAMES = ["U", "U2", "U'", "R", "R2", "R'", "F", "F2", "F'", "D", "D2", "D'", "L", "L2", "L'", "B", "B2", "B'"]
MOVE_MAP = {name: i for i, name in enumerate(MOVE_NAMES)}

# Tập 10 lệnh hợp lệ của Phase 2 (Cấm R1, R3, F1, F3, L1, L3, B1, B3)
PHASE2_MOVES = [0, 1, 2, 4, 7, 9, 10, 11, 13, 16]


def is_move_redundant_phase2(move: int, path: list) -> bool:
    if not path:
        return False

    move_axis = move // 3
    last_move_axis = path[-1] // 3

    # Quy tắc 1: A-A
    if move_axis == last_move_axis:
        return True

    # Quy tắc 2: A-B-A
    if len(path) >= 2:
        penultimate_move_axis = path[-2] // 3
        if move_axis == penultimate_move_axis and abs(last_move_axis - move_axis) == 3:
            return True
            
    # Quy tắc 3: A-B (đối diện)
    if abs(last_move_axis - move_axis) == 3:
        if move_axis < last_move_axis:
            return True

    return False



def get_phase2_compressed_index(c_perm: int, e_perm: int) -> int:
    return c_perm * 20160 + (e_perm // 2)


# --- BẢNG DỊCH CHUYỂN SIÊU NHỎ CHO 4 VIÊN TẦNG GIỮA (24 Trạng thái) ---
def build_edge4_move_table():
    def get_e4(perm):
        coord = 0
        for i in range(3):
            smaller = 0
            for j in range(i + 1, 4):
                if perm[j] < perm[i]: smaller += 1
            coord += smaller * FACTORIALS[3 - i]
        return coord

    def set_e4(coord):
        avail = [0, 1, 2, 3]
        perm = []
        for i in range(3):
            fact = FACTORIALS[3 - i]
            perm.append(avail.pop(coord // fact))
            coord %= fact
        perm.append(avail[0])
        return perm

    table = [[0] * 18 for _ in range(24)]
    for i in range(24):
        for m in PHASE2_MOVES:
            p = set_e4(i)
            if m == 4:   p[0], p[3] = p[3], p[0] # R2 swaps FR(0) and BR(3)
            elif m == 7: p[0], p[1] = p[1], p[0] # F2 swaps FR(0) and FL(1)
            elif m == 13: p[1], p[2] = p[2], p[1] # L2 swaps FL(1) and BL(2)
            elif m == 16: p[2], p[3] = p[3], p[2] # B2 swaps BL(2) and BR(3)
            # U, D không ảnh hưởng tầng giữa
            table[i][m] = get_e4(p)
    return table


edge4_move = build_edge4_move_table()

TABLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),  'table'))
with open(os.path.join(TABLE_DIR, "corner_perm_move_table.pkl"), "rb") as f:
    corner_move = pickle.load(f)
with open(os.path.join(TABLE_DIR, "edge8_perm_move_table.pkl"), "rb") as f:
    edge8_move = pickle.load(f)
with open(os.path.join(TABLE_DIR, "phase2_pruning_table.pkl"), "rb") as f:
    phase2_pruning = bytearray(f.read())





def search_phase2(c_perm: int, e8_perm: int, e4_perm: int, g: int, bound: int, path: list) -> int:
    idx = get_phase2_compressed_index(c_perm, e8_perm)
    h = phase2_pruning[idx]
    f = g + h
    
    if f > bound: return f
        
    if h == 0:
        # Kiểm tra nốt 4 viên tầng giữa đã đúng thứ tự chưa
        if e4_perm == 0:
            return -1 # THÀNH CÔNG 
            
    min_over_bound = float('inf')
    
    # Chỉ thử 10 bước hợp lệ của Phase 2
    for move in PHASE2_MOVES:
        if is_move_redundant_phase2(move, path):
            continue
        
        next_c = corner_move[c_perm][move]
        next_e8 = edge8_move[e8_perm][move]
        next_e4 = edge4_move[e4_perm][move]
        
        path.append(move)
        result = search_phase2(next_c, next_e8, next_e4, g + 1, bound, path)
        
        if result == -1: return -1
        if result < min_over_bound: min_over_bound = result
            
        path.pop()
        
    return min_over_bound




def solve_phase2(cube: RubikCube, max_length: int = 18) -> list:
    c_perm = cube.get_corner_permutation_coord()
    e8_perm = cube.get_edge8_permutation_coord()
    e4_perm = cube.get_edge4_permutation_coord()
    
    bound = phase2_pruning[get_phase2_compressed_index(c_perm, e8_perm)]
    path = []
    
    # Chặn ngay nếu bound cơ sở đã lớn hơn giới hạn cho phép
    if bound > max_length:
        return None
        
    start_time = time.time()
    
    while True:
        if bound > max_length: 
            return None
            
        result = search_phase2(c_perm, e8_perm, e4_perm, 0, bound, path)
        
        if result == -1:
            solution = [MOVE_NAMES[m] for m in path]
            if max_length >= 18: # Chỉ in log cho lần giải tối ưu đầu tiên để tránh spam log
                print(f"Done phase 2 in {time.time() - start_time:.3f} s")
            return solution
            
        bound = result
