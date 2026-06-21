import pickle
import time
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import RubikCube

TABLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'table'))
os.makedirs(TABLE_DIR, exist_ok=True)

FACTORIALS = [1, 1, 2, 6, 24, 120, 720, 5040]

# 10 bước xoay hợp lệ của Phase 2: U1, U2, U3, R2, F2, D1, D2, D3, L2, B2
PHASE2_MOVES = [0, 1, 2, 4, 7, 9, 10, 11, 13, 16]


def build_phase2_move_tables():
    print("1. Đang khởi tạo Phase 2 Move Tables (40320 x 18)...")
    start_time = time.time()
    
    corner_perm_move = [[0] * 18 for _ in range(40320)]
    edge8_perm_move = [[0] * 18 for _ in range(40320)]
    
    for i in range(40320):
        # Bảng Góc
        c_cube = RubikCube.RubikCube()
        c_cube.set_corner_permutation_coord(i)
        
        # Bảng Cạnh U/D
        e_cube = RubikCube.RubikCube()
        e_cube.set_edge8_permutation_coord(i)
        
        for move in PHASE2_MOVES:
            # Xoay và lưu góc
            c_temp = RubikCube.RubikCube()
            c_temp.corners = [dict(c) for c in c_cube.corners]
            c_temp.move_cubie(move)
            corner_perm_move[i][move] = c_temp.get_corner_permutation_coord()
            
            # Xoay và lưu cạnh
            e_temp = RubikCube.RubikCube()
            e_temp.edges = [dict(e) for e in e_cube.edges]
            e_temp.move_cubie(move)
            edge8_perm_move[i][move] = e_temp.get_edge8_permutation_coord()

    print(f"-> Hoàn thành Move Tables trong {time.time() - start_time:.2f} giây.")
    
    with open(os.path.join(TABLE_DIR, "corner_perm_move_table.pkl"), "wb") as f:
        pickle.dump(corner_perm_move, f)
    with open(os.path.join(TABLE_DIR, "edge8_perm_move_table.pkl"), "wb") as f:
        pickle.dump(edge8_perm_move, f)
        
    return corner_perm_move, edge8_perm_move

if __name__ == "__main__":
    build_phase2_move_tables()