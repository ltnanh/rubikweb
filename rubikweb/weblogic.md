# Logic backend của web 
## 1. Kiến trúc Backend (Layered Architecture)

Backend được thiết kế theo mô hình MVC (Layered Architecture) giúp mã nguồn sạch, dễ bảo trì và chịu tải tốt. Các thành phần được chia thành các thư mục riêng biệt theo Separation of Concerns:

```text
rubikweb/
├── api/                    
│   ├── __init__.py
│   └── routes.py           # Chứa các endpoint (@router.post("/api/solve"))
├── core/                   
│   ├── __init__.py
│   └── config.py           # Chứa các cấu hình (TIMEOUT, MAX_CONCURRENT_SOLVES)
├── schemas/                
│   ├── __init__.py
│   └── models.py           # Định nghĩa cấu trúc dữ liệu Pydantic (Request, Response)
├── services/               
│   ├── __init__.py
│   └── solver_service.py   # Xử lý Logic kinh doanh, gọi thuật toán, timeout
├── kociemba/               # Thuật toán Kociemba nguyên bản
├── static/                 # Frontend
└── main.py                 # File entry-point kết nối FastAPI và Router
```

### Điểm nhấn Kiến trúc:
1. **Concurrency Control (Semaphore):** Ứng dụng tích hợp cơ chế xếp hàng `asyncio.Semaphore` (hiện đặt giới hạn xử lý đồng thời là 2). Nếu nhiều người cùng nhấn nút giải, các luồng mới sẽ được xếp hàng để bảo vệ CPU/RAM của server (phù hợp với các VPS free tier cấu hình thấp).
2. **Non-blocking Event Loop:** Quá trình giải Rubik (mất vài giây) được đưa vào thread phụ qua `asyncio.to_thread()`, nhờ đó FastAPI không bị "đóng băng" (treo event loop), vẫn có thể phục vụ các request tĩnh (như tải html, css, js) một cách mượt mà.
3. **Tiến trình độc lập (Multiprocessing):** Hàm giải Rubik bản thân nó chạy trên một tiến trình con (worker) được cấp phát thông qua `context("fork")`, cách ly lỗi bộ nhớ và có hard timeout (10 giây) để ngắt khi thuật toán bế tắc.

## 2. Chi tiết các thành phần API

### 2.1 Lớp API Router (`api/routes.py`)
Tiếp nhận HTTP Request từ frontend, xác thực dữ liệu qua Pydantic và chuyển tiếp cho service.

- `@router.post("/api/solve")`: Endpoint dùng khi người dùng nhập scramble. Trả về `SolveResponse`.
- `@router.post("/api/solve-by-facelet")`: Endpoint dùng khi người dùng tự tô màu trên web. Trả về `SolveResponse`.
- `@router.get("/api/health")`: Kiểm tra trạng thái server.

**Luồng xử lý tại Router:**
1. Khóa Semaphore: `async with solve_semaphore`
2. Gọi hàm giải trên thread phụ: `await asyncio.to_thread(solve_cube_from_scramble, request.scramble)`
3. Đóng gói kết quả tính toán thành JSON (`SolveResponse`) trả về cho frontend.
4. Bắt và xử lý `TimeoutError` (HTTP 408) hoặc `Exception` (HTTP 400).

### 2.2 Lớp Data Models (`schemas/models.py`)
Quản lý cấu trúc dữ liệu đầu vào và đầu ra, dùng Pydantic.
- `SolveRequest`: `{ "scramble": "R U R' U'" }`
- `SolveByFaceletRequest`: `{ "facelet_string": "U R F D L B..." }`
- `SolveResponse`: Trả về `solution` (danh sách move), `moves_count`, `phase1_moves`, `phase2_moves`, `solving_time_ms`, `success`.

### 2.3 Lớp Logic & Worker (`services/solver_service.py`)
- **`_solve_worker`**: Hàm chạy trên process con. Nó nhận `mode` (scramble/facelet) và `payload`, khởi tạo `FaceletCube`, chuyển thành `RubikCube` và gọi `solve_cube()` (thuật toán Kociemba). Kết quả được bắn qua `Pipe` về process cha.
- **`_solve_with_hard_timeout`**: Hàm điều phối chính. Nó theo dõi timeout, liên tục `poll()` pipe. Nếu quá timeout thì sẽ kill worker, hoặc nếu hoàn thành sớm thì trả về kết quả.

### 2.4 Entry Point (`main.py`)
- Khởi tạo FastAPI `app = FastAPI()`.
- Áp dụng cấu hình CORS (cho phép frontend giao tiếp mượt mà).
- Mount các routes của hệ thống bằng `app.include_router(router)`.
- Mount thư mục `static` và cấu hình Endpoint `/` để redirect về `index.html`.
- Khi deploy, thay vì chạy trực tiếp qua `python web_api.py`, hệ thống chạy thông qua `uvicorn main:app`.

### 2.5 Luồng hoạt động tổng thể của Backend
```text
Start Server (uvicorn main:app)
-> Load FastAPI app và mount tĩnh
-> Mount API Routes

User gửi Request (Solve)
-> Request được validate bởi Pydantic Schema
-> Qua trạm kiểm soát Semaphore (Xếp hàng nếu quá tải)
-> Bắt đầu await asyncio.to_thread() (Đẩy sang background thread)
-> Background thread gọi `_solve_with_hard_timeout`
-> Đẻ ra Process con (Worker)
-> Worker tính toán và bắn kết quả qua Pipe
-> Background thread nhận kết quả, trả về cho Router
-> FastAPI trả JSON về Frontend.

## 3. Kiến trúc Frontend (Thư mục `static`)

Với kiến trúc ES6 Modules, toàn bộ mã nguồn JavaScript phía trình duyệt được tách rời thành các file có chức năng riêng biệt giúp dễ dàng quản lý và tái sử dụng.

### 3.1 Sơ đồ kiến trúc Frontend

```text
index.html (Giao diện web)
  │
  ├─── style.css (Định dạng giao diện và bố cục)
  │
  └─── main.js (Entry point - "Tổng chỉ huy")
         │
         ├─── globals.js (Trạng thái và biến dùng chung)
         │
         ├─── validators.js (Xác thực dữ liệu input)
         │
         ├─── cube3d.js (Động cơ 3D Three.js)
         │
         └─── api.js (Xử lý giao tiếp với Backend)
```

### 3.2 Chức năng từng file

**1. `globals.js`**
- Đóng vai trò là bộ não lưu trữ trạng thái toàn cục của cả ứng dụng (`state`).
- Lưu trữ cấu hình màu sắc tiêu chuẩn (`COLORS`) và địa chỉ gọi API (`API_URL`).
- Chứa các hàm cập nhật giao diện dùng chung như `updateStatus` (đổi text trạng thái) hay `clearSolution` (xóa lời giải cũ).

**2. `validators.js`**
- Chuyên chứa các hàm tính toán, kiểm tra logic độc lập không dính tới giao diện (Pure functions).
- `isValidScramble()`: Kiểm tra xem chuỗi scramble nhập vào có đúng định dạng chuẩn (U, R', F2...) không.
- `isValidPieces()`: Kiểm tra thuật toán sơ bộ xem màu sắc người dùng tô có tạo ra một khối Rubik hợp lệ không (vd: không thể có cạnh Xanh-Xanh, góc phải đúng thứ tự chiều kim đồng hồ).

**3. `cube3d.js`**
- Đảm nhiệm toàn bộ logic về thư viện `Three.js` (Render 3D).
- Khởi tạo Scene, Camera, Lighting và OrbitControls để người dùng có thể xoay khối Rubik bằng chuột.
- Chứa hàm `rotateLayer()` dùng lượng giác và ma trận xoay để tạo animation xoay tầng Rubik mượt mà.
- Expose (xuất) ra các biến và hàm điều khiển như `cubes`, `applyMoves`, `resetCube` để `main.js` có thể gọi.

**4. `api.js`**
- Chuyên môn hóa nhiệm vụ gọi xuống Backend (FastAPI).
- Đóng gói hàm `solveRubikApi()`: Tự động gom dữ liệu (từ ô input scramble hoặc từ mảng facelet được tô màu), gửi POST request lên server.
- Xử lý các luồng try-catch, bắt các lỗi mạng hoặc `ValueError` Toán học từ Backend để bắn alert lên giao diện cho người dùng biết.

**5. `main.js`**
- File `import` tất cả các chức năng từ 4 file trên.
- Quản lý logic tương tác của trình duyệt (DOM Manipulation).
- Lắng nghe và xử lý sự kiện (Event Listener) của người dùng: Click chuyển Tab, vẽ màu lên Grid 2D, bấm nút xáo ngẫu nhiên, bấm xem lời giải,...
- Đảm bảo tính tuần tự khi hoạt động, ví dụ: bắt lỗi bằng `validators.js`, sau đó áp dụng vào 3D bằng `cube3d.js`, cuối cùng gọi giải bằng `api.js`.

**6. `style.css`**
- Chứa toàn bộ các quy tắc định dạng giao diện (CSS) cho trang web.
- Quản lý bố cục (Flexbox, CSS Grid) cho giao diện người dùng, như bố trí các nút bấm, lưới ô màu 2D (`facelet-map`), và khu vực hiển thị khối Rubik 3D.
- Tạo ra các hiệu ứng UI/UX như hover, trạng thái active của tab, màu sắc các nút bấm và animation nhỏ.

### 3.3 Luồng hoạt động Frontend (Ví dụ: Tính năng tô màu)

```text
Người dùng chọn màu và click vào Grid 2D 
-> main.js cập nhật state.faceletColors (qua globals.js)
-> User bấm "Áp dụng lên 3D" 
-> main.js lấy mảng màu đưa cho validators.js kiểm tra
-> Hợp lệ -> Gọi resetCube() và đổi màu Material trong cube3d.js
-> User bấm "Giải Ngay"
-> main.js gọi api.js
-> api.js gọi fetch() xuống Backend
-> Nhận kết quả -> Cập nhật DOM hiển thị số moves và solution
-> User bấm "Xem Giải"
-> main.js vòng lặp gọi rotateLayer() trong cube3d.js để diễn hoạt 3D
```

