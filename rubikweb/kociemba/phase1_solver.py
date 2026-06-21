import pickle
import os
import time
import copy
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from RubikCube import RubikCube
from RubikCUbeFacelet import FaceletCube


TABLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'table'))
with open(os.path.join(TABLE_DIR, "twist_move_table.pkl"), "rb") as f:
    twist_move = pickle.load(f)
with open(os.path.join(TABLE_DIR, "flip_move_table.pkl"), "rb") as f:
    flip_move = pickle.load(f)
with open(os.path.join(TABLE_DIR, "udslice_move_table.pkl"), "rb") as f:
    udslice_move = pickle.load(f)
with open(os.path.join(TABLE_DIR, "phase1_pruning_table.pkl"), "rb") as f:
    phase1_pruning = pickle.load(f)

MOVE_NAMES = ["U", "U2", "U'", "R", "R2", "R'", "F", "F2", "F'", "D", "D2", "D'", "L", "L2", "L'", "B", "B2", "B'"]
MOVE_MAP = {name: i for i, name in enumerate(MOVE_NAMES)}


def is_move_redundant(move: int, path: list) -> bool:
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




def search(twist: int, flip: int, ud_slice: int, g: int, bound: int, path: list) -> int:
    index = twist * 2048 + flip
    h = phase1_pruning[index]
    f = g + h
    
    if f > bound: 
        return f
        
    if h == 0:
        # Nếu h=0 (twist=0, flip=0) và ud_slice=0, thì khối đã đạt trạng thái G1.
        if ud_slice == 0: 
            return -1 # Đã tìm thấy lời giải cho Phase 1
            
    min_over_bound = float('inf')
    
    for move in range(18):
        if is_move_redundant(move, path):
            continue
            
        next_twist = twist_move[twist][move]
        next_flip = flip_move[flip][move]
        next_ud_slice = udslice_move[ud_slice][move]
        
        path.append(move)
        result = search(next_twist, next_flip, next_ud_slice, g + 1, bound, path)
        
        if result == -1: 
            return -1
        if result < min_over_bound:
            min_over_bound = result
            
        path.pop()
        
    return min_over_bound




def solve_phase1(initial_cube: RubikCube):
    twist = initial_cube.get_corner_orientation_coord()
    flip = initial_cube.get_edge_orientation_coord()
    ud_slice = initial_cube.get_ud_slice_coord()
    
    bound = phase1_pruning[twist * 2048 + flip]
    path = []
    
    start_time = time.time()
    
    while True:
        if bound > 12: return None, None # Vượt quá giới hạn Phase 1 
            
        result = search(twist, flip, ud_slice, 0, bound, path)
        
        if result == -1:
            solution = [MOVE_NAMES[m] for m in path]
            print(f"Done phase 1 in {time.time() - start_time:.3f} s")
            
            solved_phase1_cube = copy.deepcopy(initial_cube)
            for move_str in solution:
                solved_phase1_cube.move_cubie(MOVE_MAP[move_str])
                
            return solution, solved_phase1_cube

        #if not solved yet, increase bound and continue search  
        bound = result



def search_suboptimal(twist: int, flip: int, ud_slice: int, g: int, bound: int, path: list):
    index = twist * 2048 + flip
    h = phase1_pruning[index]
    f = g + h
    
    if f > bound:
        return
 
    # Chỉ yield đường đi khi đạt chính xác giới hạn bound
    if h == 0 and ud_slice == 0:
        if g == bound:
            yield path[:]
        return
        
    for move in range(18):
        if is_move_redundant(move, path):
            continue
            
        next_twist = twist_move[twist][move]
        next_flip = flip_move[flip][move]
        next_ud_slice = udslice_move[ud_slice][move]
        
        path.append(move)
        yield from search_suboptimal(next_twist, next_flip, next_ud_slice, g + 1, bound, path)
        path.pop()



def solve_phase1_suboptimal(initial_cube: RubikCube, bound: int):
    """Tìm và 'nhả' (yield) từng lời giải Phase 1 có chiều dài đúng bằng bound."""
    twist = initial_cube.get_corner_orientation_coord()
    flip = initial_cube.get_edge_orientation_coord()
    ud_slice = initial_cube.get_ud_slice_coord()
    
    for path in search_suboptimal(twist, flip, ud_slice, 0, bound, []):
        yield [MOVE_NAMES[m] for m in path]
