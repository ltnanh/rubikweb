import pickle
import time
import os

def build_phase1_pruning_table():
    print("Starting to build Phase 1 Pruning Table...")
    
    TABLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'table'))
    twist_move_path = os.path.join(TABLE_DIR, "twist_move_table.pkl")
    flip_move_path = os.path.join(TABLE_DIR, "flip_move_table.pkl")

    with open(twist_move_path, "rb") as f:
        twist_move = pickle.load(f)
    with open(flip_move_path, "rb") as f:
        flip_move = pickle.load(f)
    


    # Initialize a flat Pruning Table array of size: 2187 * 2048 = 4,478,976  .Set the default value to -1 
    TOTAL_STATES = 2187 * 2048
    pruning_table = bytearray([255] * TOTAL_STATES) 
    
    # Fill the goal state (solved state: twist = 0, flip = 0)
    pruning_table[0] = 0
    current_depth = 0
    filled_count = 1
    
    start_time = time.time()
    

    # Breadth-First Search (BFS) loop
    while filled_count < TOTAL_STATES:
        layer_start = time.time()
        new_filled = 0
        
        # Iterate through all states in the table
        for index in range(TOTAL_STATES):
            # If a state at the current depth is found
            if pruning_table[index] == current_depth:
                twist = index // 2048
                flip = index % 2048
                
                # Try applying all 18 basic moves
                for move in range(18):
                    # Use the Move Table for a lookup of the new coordinate
                    next_twist = twist_move[twist][move]
                    next_flip = flip_move[flip][move]
                    
                    # Calculate the new index in the pruning table
                    next_index = next_twist * 2048 + next_flip
                    
                    # If this state has not been visited yet
                    if pruning_table[next_index] == 255:
                        pruning_table[next_index] = current_depth + 1
                        new_filled += 1
                        
        filled_count += new_filled
        print(f"Depth {current_depth} -> {current_depth + 1}: Filled {new_filled} new states. "
              f"Total: {filled_count}/{TOTAL_STATES} ({filled_count/TOTAL_STATES*100:.2f}%) "
              f"| Layer time: {time.time() - layer_start:.2f}s")
        

        # Safety break if no new states can be filled   
        if new_filled == 0:
            break
            
        current_depth += 1

    print(f"\n=== Finished building table in {time.time() - start_time:.2f} seconds ===")
    print(f"Max depth of Phase 1 : {current_depth} moves.")
    
    # 5. Save the pruning table to a binary file
    with open(os.path.join(TABLE_DIR, "phase1_pruning_table.pkl"), "wb") as f:
        pickle.dump(list(pruning_table), f)
    print("Successfully saved 'phase1_pruning_table.pkl'!")

if __name__ == "__main__":
    build_phase1_pruning_table()