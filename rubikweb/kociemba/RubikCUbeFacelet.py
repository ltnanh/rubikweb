import RubikCube
from typing import List, Optional


CORNER_FACELETS: List[List[int]] = [
    [8, 9, 20],   # URF 
    [6, 18, 38],  # UFL 
    [0, 36, 47],  # ULB 
    [2, 45, 11],  # UBR 
    [29, 26, 15], # DFR 
    [27, 44, 24], # DLF 
    [33, 53, 42], # DBL 
    [35, 17, 51]  # DRB 
]

EDGE_FACELETS: List[List[int]] = [
    [5, 10],  # UR 
    [7, 19],  # UF 
    [3, 37],  # UL 
    [1, 46],  # UB 
    [32, 16], # DR 
    [28, 25], # DF 
    [30, 43], # DL 
    [34, 52], # DB 
    [23, 12], # FR 
    [21, 41], # FL 
    [50, 39], # BL 
    [48, 14]  # BR 
]

# Bộ màu chuẩn và nhãn định danh của Góc/Cạnh gốc
CORNER_COLOR_SETS: List[set] = [{'U', 'R', 'F'}, {'U', 'F', 'L'}, {'U', 'L', 'B'}, {'U', 'B', 'R'},
                                {'D', 'F', 'R'}, {'D', 'L', 'F'}, {'D', 'B', 'L'}, {'D', 'R', 'B'}]

EDGE_COLOR_SETS: List[set] = [{'U', 'R'}, {'U', 'F'}, {'U', 'L'}, {'U', 'B'},
                              {'D', 'R'}, {'D', 'F'}, {'D', 'L'}, {'D', 'B'},
                              {'F', 'R'}, {'F', 'L'}, {'B', 'L'}, {'B', 'R'}]

CORNER_COLORS: List[str] = ["URF", "UFL", "ULB", "UBR", "DFR", "DLF", "DBL", "DRB"]
EDGE_COLORS: List[str] = ["UR", "UF", "UL", "UB", "DR", "DF", "DL", "DB", "FR", "FL", "BL", "BR"]


# bảng ánh xạ ký tự xoay sang Move Index (0..17)
FACES: List[str] = ['U', 'R', 'F', 'D', 'L', 'B']
MOVE_MAP: dict = {}
for f_idx, face in enumerate(FACES):
    MOVE_MAP[face] = f_idx * 3 + 0        # Xoay 90 độ xuôi (R)
    MOVE_MAP[face + '2'] = f_idx * 3 + 1  # Xoay 180 độ (R2)
    MOVE_MAP[face + "'"] = f_idx * 3 + 2  # Xoay 90 độ ngược (R')



class FaceletCube:
    #Khởi tạo mảng ô màu. Mặc định là khối đã giải
    def __init__(self, facelet_string: Optional[str] = None):
        if facelet_string is None:
            self.f: List[str] = list("UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB")
        else:
            self.f: List[str] = list(facelet_string.upper().replace(" ", "").replace("\n", ""))
            if len(self.f) != 54:
                raise ValueError("Len of facelet string must be 54")


    #2D representation of rubik
    def print_cube(self):
        template = (
            "    {0}{1}{2}\n"
            "    {3}{4}{5}\n"
            "    {6}{7}{8}\n"
            "{36}{37}{38} {18}{19}{20} {9}{10}{11} {45}{46}{47}\n"
            "{39}{40}{41} {21}{22}{23} {12}{13}{14} {48}{49}{50}\n"
            "{42}{43}{44} {24}{25}{26} {15}{16}{17} {51}{52}{53}\n"
            "    {27}{28}{29}\n"
            "    {30}{31}{32}\n"
            "    {33}{34}{35}"
        )
        print(template.format(*self.f))


    #"""Convert faclet representation to cubie representation (RubikCube)
    def to_rubik_cube(self):
        cubie_cube = RubikCube.RubikCube()
        
        # 1. DỊCH 8 VIÊN GÓC
        for cp in range(8):
            facelet_indices = CORNER_FACELETS[cp]
            colors_at_slot = [self.f[idx] for idx in facelet_indices]
            set_at_slot = set(colors_at_slot)
            
            actual_cubie_id = -1
            for i in range(8):
                if set_at_slot == CORNER_COLOR_SETS[i]:
                    actual_cubie_id = i
                    break
            cubie_cube.corners[cp]['c'] = actual_cubie_id
            
            orientation = -1
            for ori in range(3):
                if colors_at_slot[ori] in ('U', 'D'):
                    orientation = ori
                    break
            cubie_cube.corners[cp]['o'] = orientation

        # 2. DỊCH 12 VIÊN CẠNH
        for ep in range(12):
            facelet_indices = EDGE_FACELETS[ep]
            c0 = self.f[facelet_indices[0]] # Lấy màu ở ô ưu tiên
            c1 = self.f[facelet_indices[1]] # Lấy màu ở ô phụ
            set_at_slot = {c0, c1}
            
            actual_cubie_id = -1
            for i in range(12):
                if set_at_slot == EDGE_COLOR_SETS[i]:
                    actual_cubie_id = i
                    break
            cubie_cube.edges[ep]['e'] = actual_cubie_id
            
            if c0 == EDGE_COLORS[actual_cubie_id][0]:
                cubie_cube.edges[ep]['o'] = 0
            else:
                cubie_cube.edges[ep]['o'] = 1
        cubie_cube.verify()
        return cubie_cube
    
    #Convert from cubie level to facelet level 
    def update_from_rubik_cube(self, rubik_cube: RubikCube.RubikCube):
        # Cập nhật màu cho 8 ô đỗ góc
        for cp in range(8):
            cubie_id = rubik_cube.corners[cp]['c']
            o = rubik_cube.corners[cp]['o']
            for slot_idx, idx in enumerate(CORNER_FACELETS[cp]):
                self.f[idx] = CORNER_COLORS[cubie_id][(slot_idx - o) % 3]

        # Cập nhật màu cho 12 ô đỗ cạnh
        for ep in range(12):
            cubie_id = rubik_cube.edges[ep]['e']
            o = rubik_cube.edges[ep]['o'] 
            for slot_idx, idx in enumerate(EDGE_FACELETS[ep]):
                self.f[idx] = EDGE_COLORS[cubie_id][slot_idx ^ o]

    #Scramble the cube 
    def scramble(self, scramblestr: str):
        cubie_cube = self.to_rubik_cube()
        moves = scramblestr.strip().split()
        for m in moves:
            if m in MOVE_MAP:
                cubie_cube.move_cubie(MOVE_MAP[m])
            else:
                raise ValueError(f"Invalid move in scramble: {m}")

        self.update_from_rubik_cube(cubie_cube)



if __name__ == "__main__":
    fc = FaceletCube()
    fc.print_cube() 
    print(fc.f) 
