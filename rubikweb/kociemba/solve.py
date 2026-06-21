import time
import sys
import os
import copy


sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from RubikCube import RubikCube
from RubikCUbeFacelet import FaceletCube
import phase1_solver
import phase2_solver
from phase1_solver import MOVE_NAMES, MOVE_MAP



# Helper function to convert move string to (axis, power)
def _get_move_info(move_str: str):
    move_idx = MOVE_MAP[move_str]
    axis = move_idx // 3
    power = (move_idx % 3) + 1 # 1 for x1, 2 for x2, 3 for x3 (x')
    return axis, power

def _get_move_str(axis: int, power: int):
    if power == 0: return None # No-op
    return MOVE_NAMES[axis * 3 + (power - 1)]

def simplify_solution_sequence(solution_moves: list) -> list:
    if not solution_moves:
        return []

    simplified_internal_repr = [] # Store as (axis, power) tuples
    for move_str in solution_moves:
        axis, power = _get_move_info(move_str)

        if not simplified_internal_repr or axis != simplified_internal_repr[-1][0]:
            simplified_internal_repr.append((axis, power))
        else:
            last_axis, last_power = simplified_internal_repr[-1]
            new_power = (last_power + power) % 4
            if new_power == 0: simplified_internal_repr.pop() # 4 quarter turns = no-op
            else: simplified_internal_repr[-1] = (last_axis, new_power)
    
    return [_get_move_str(axis, power) for axis, power in simplified_internal_repr if power != 0]




def solve_cube(cube: RubikCube, timeout: float = 30.0):
    overall_start_time = time.time()

    p1_solution, p1_solved_cube = phase1_solver.solve_phase1(cube)
    p2_solution = phase2_solver.solve_phase2(p1_solved_cube) 

    best_p1 = p1_solution
    best_p2 = p2_solution
    best_solution = simplify_solution_sequence(p1_solution + p2_solution)
    best_len = len(best_solution)

    print(f"\n[INITIAL] Found solution: {best_len} moves ({len(best_p1)} P1 + {len(best_p2)} P2)")
    yield best_solution, len(best_p1), len(best_p2)

    # Dừng sớm nếu thuật toán ban đầu đã tìm được chuỗi quá tốt
    if best_len <= 21:
        print(f"[OPT] Solution is already <= 21 moves. Stopping search.")
        return

    # Bắt đầu tìm kiếm Suboptimal với P1 dài hơn
    current_p1_bound = len(best_p1) + 1
    max_p1_bound = 14

    while current_p1_bound < best_len and current_p1_bound <= max_p1_bound:
        if time.time() - overall_start_time > timeout:
            print(f"\n[TIMEOUT] Search exceeded {timeout}s. Returning best solution found so far.")
            break

        print(f"\n[SUBOPTIMAL] Searching Phase 1 with exact {current_p1_bound} moves")
        
        # p1_solution_generator cung cấp lời giải phase 1 theo stream 
        p1_solution_generator = phase1_solver.solve_phase1_suboptimal(cube, current_p1_bound)
        found_any_p1_sol = False
        
        # Vòng lặp này lấy từng phase1 solve trong stream để xử lí 
        for p1_sol in p1_solution_generator:
            if not found_any_p1_sol:
                found_any_p1_sol = True

            if p1_sol:
                # Khống chế Phase 2 phải giải quyết ngắn hơn (best_len - current_p1_bound - 1)
                p2_max_length = best_len - current_p1_bound - 1
                if p2_max_length < 0:
                    continue
                    
                temp_cube = copy.deepcopy(cube)
                for move_str in p1_sol:
                    temp_cube.move_cubie(phase1_solver.MOVE_MAP[move_str])
                
                # Chuyền max_length vào, cắt tỉa triệt để!
                p2_sol = phase2_solver.solve_phase2(temp_cube, max_length=p2_max_length)
                
                if p2_sol is not None:
                    combined_sol = simplify_solution_sequence(p1_sol + p2_sol)
                    total_len = len(combined_sol)
                    
                    if total_len < best_len:
                        best_len = total_len
                        best_solution = combined_sol
                        best_p1 = p1_sol
                        best_p2 = p2_sol
                        print(f"NEW BEST: {best_len} moves! ({len(best_p1)} P1 + {len(best_p2)} P2)")
                        yield best_solution, len(best_p1), len(best_p2)
                        
                        if best_len <= 21:
                            print(f"[OPT] Found a solution <= 21 moves. Stopping search.")
                            break
        
        if not found_any_p1_sol:
            print(" No solutions found at this depth.")
            
        if best_len <= 21:
            break
            
        current_p1_bound += 1

    print(f"\n[FINAL] Best algorithm found: {best_len} moves.")








if __name__ == "__main__":
    scramble_string = "L2 F U2 B2 U2 R2 B2 R2 F U2 F2 L' F' R D L' D L' D L"
    print(f"Scramble: {scramble_string}\n")

    fc = FaceletCube()
    fc.scramble(scramble_string)

    initial_cube = fc.to_rubik_cube()

    start_time = time.time()
    
    solution_found = False
   
    for total_sol, p1_len, p2_len in solve_cube(initial_cube, timeout=60.0):
        solution_found = True

    end_time = time.time()

    if solution_found:
        print(f"\nTotal solving time: {end_time - start_time:.3f} seconds")
        print(f"Length: {len(total_sol)} moves (Phase 1: {p1_len}, Phase 2: {p2_len})") 
        print(f"Complete algorithm: {' '.join(total_sol)}")
    else:
        print("No solution found.")