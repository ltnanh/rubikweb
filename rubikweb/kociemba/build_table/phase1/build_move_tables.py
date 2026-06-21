import pickle
import time
import os
import sys 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))) 
import RubikCube  

def generate_twist_move_table():
    """Sinh bảng dịch chuyển cho hướng góc: Kích thước 2187 dòng x 18 cột"""
    print("Initializing Twist Move Table (2187 x 18)...")
    start_time = time.time()
    
    # Tạo mảng trống 2187 x 18
    twist_move_table = [[0] * 18 for _ in range(2187)]
    
    for i in range(2187):
        for move in range(18):
            # 1. Create a new cube and set its corner orientation coordinate to i
            cube = RubikCube.RubikCube()
            cube.set_corner_orientation_coord(i)
            
            # 2. Perform the corresponding move
            cube.move_cubie(move)
            
            # 3. Get the new coordinate and save it to the table
            twist_move_table[i][move] = cube.get_corner_orientation_coord()
            
    print(f"Finished Twist Move Table in {time.time() - start_time:.2f} seconds.")
    return twist_move_table




def generate_flip_move_table():
    """Sinh bảng dịch chuyển cho hướng cạnh: Kích thước 2048 dòng x 18 cột"""
    print("Initializing Flip Move Table (2048 x 18)...")
    start_time = time.time()
    
    # Tạo mảng trống 2048 x 18
    flip_move_table = [[0] * 18 for _ in range(2048)]
    
    for i in range(2048):
        for move in range(18):
            # 1. Create a new cube and set its edge orientation coordinate to i
            cube = RubikCube.RubikCube()
            cube.set_edge_orientation_coord(i)
            
            # 2. Perform the corresponding move
            cube.move_cubie(move)
            
            # 3. Get the new coordinate and save it to the table
            flip_move_table[i][move] = cube.get_edge_orientation_coord()
            
    print(f"Finished Flip Move Table in {time.time() - start_time:.2f} seconds.")
    return flip_move_table


def generate_udslice_move_table():
    print("Initializing UDSlice Move Table (495 x 18)...")
    start_time = time.time()
    udslice_move_table = [[0] * 18 for _ in range(495)]
    for i in range(495):
        for move in range(18):
            cube = RubikCube.RubikCube()
            cube.set_ud_slice_coord(i)
            cube.move_cubie(move)
            udslice_move_table[i][move] = cube.get_ud_slice_coord()
    print(f"Finished UDSlice Move Table in {time.time() - start_time:.2f} seconds.")
    return udslice_move_table





if __name__ == "__main__":
    twist_table = generate_twist_move_table()
    flip_table = generate_flip_move_table()
    udslice_table = generate_udslice_move_table()
    print("\nExporting data to disk...")
    
    TABLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'table'))
    os.makedirs(TABLE_DIR, exist_ok=True)

    with open(os.path.join(TABLE_DIR, "twist_move_table.pkl"), "wb") as f:
        pickle.dump(twist_table, f)
        
    with open(os.path.join(TABLE_DIR, "flip_move_table.pkl"), "wb") as f:
        pickle.dump(flip_table, f)
        
    with open(os.path.join(TABLE_DIR, "udslice_move_table.pkl"), "wb") as f:
        pickle.dump(udslice_table, f)

    print("Successfully saved 3 files: 'twist_move_table.pkl', 'flip_move_table.pkl', and 'udslice_move_table.pkl'!")