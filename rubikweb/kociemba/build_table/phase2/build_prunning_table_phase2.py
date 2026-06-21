import pickle
import time
import os
import sys 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import RubikCube

TABLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'table'))
os.makedirs(TABLE_DIR, exist_ok=True)


#10 bước xoay hợp lệ của Phase : U1, U2, U3, R2, F2, D1, D2, D3, L2, B2
PHASE2_MOVES = [0, 1, 2, 4, 7, 9, 10, 11, 13, 16]


# compute parity of a lemar coord 
def get_parity(coord):
    inversions = 0
    FACTORIALS = [1, 1, 2, 6, 24, 120, 720, 5040]
    for i in range(7, 0, -1):
        fact = FACTORIALS[i]
        inversions += coord // fact
        coord %= fact
    return inversions % 2



def load_phase2_move_tables():
    print("1. Loading Phase 2 Move Tables...")
    
    corner_move_path = os.path.join(TABLE_DIR, "corner_perm_move_table.pkl")
    edge8_move_path = os.path.join(TABLE_DIR, "edge8_perm_move_table.pkl")
        
    with open(corner_move_path, "rb") as f:
        corner_perm_move = pickle.load(f)
    with open(edge8_move_path, "rb") as f:
        edge8_perm_move = pickle.load(f)
        
    print(f"-> Finished loading Move Tables")
    return corner_perm_move, edge8_perm_move



#Build prunning table 
def build_phase2_pruning_table(c_move_table, e_move_table):
    print("\n2. Calculating Parity array for 40,320 states")
    parity = [get_parity(i) for i in range(40320)]
    
    TOTAL_STATES = 40320 * 20160  # Exactly 812,851,200 cells
    print(f"3. Initializing RAM for {TOTAL_STATES / (1024**2):.1f} MB...")
    pruning_table = bytearray([255] * TOTAL_STATES)

    # solved state : Góc 0, Cạnh 0 -> Index 0
    pruning_table[0] = 0
    
    current_depth = 0
    filled_count = 1
    start_time = time.time()
    
    print("\nSTARTING PHASE 2 BFS LOOP (THIS WILL TAKE SEVERAL MINUTES)")
    
    while filled_count < TOTAL_STATES:
        layer_start = time.time()
        new_filled = 0
        
        # Linear loop scanning directly into the compressed array (Maximum speed for Python)
        for idx in range(TOTAL_STATES):
            if pruning_table[idx] == current_depth:
                
                # Inverse Mapping technique to retrieve the two raw coordinates from the flat index
                c_perm = idx // 20160
                half_e = idx % 20160
                e_perm_base = half_e * 2
                
                # Combine Parity to restore the correct Edge8Perm
                if parity[c_perm] == parity[e_perm_base]:
                    e_perm = e_perm_base
                else:
                    e_perm = e_perm_base + 1
                    
                # Look up Move Tables for the 10 valid moves
                for move in PHASE2_MOVES:
                    next_c = c_move_table[c_perm][move]
                    next_e = e_move_table[e_perm][move]
                    
                    # Compress into a new flat index
                    next_idx = next_c * 20160 + (next_e // 2)
                    
                    if pruning_table[next_idx] == 255:
                        pruning_table[next_idx] = current_depth + 1
                        new_filled += 1
                        
        filled_count += new_filled
        print(f"Depth {current_depth} -> {current_depth+1}: Filled {new_filled:,} states. "
              f"Progress: {filled_count/TOTAL_STATES*100:.2f}% "
              f"| Time for layer: {time.time() - layer_start:.1f}s")
              
        if new_filled == 0: break
        current_depth += 1

    print(f"\n=== Finished building table in {time.time() - start_time:.2f} seconds ===")
    print(f"Max depth of Phase 2 : {current_depth} moves.")
    
    with open(os.path.join(TABLE_DIR, "phase2_pruning_table.pkl"), "wb") as f:
        pruning_table_bytes = bytes(pruning_table)
        f.write(pruning_table_bytes)
    print("Successfully saved 'phase2_pruning_table.pkl'!")



if __name__ == "__main__":
    c_move, e_move = load_phase2_move_tables()
    build_phase2_pruning_table(c_move, e_move)