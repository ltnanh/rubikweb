// Mảng màu của khối Rubik
export const COLORS = {
    'U': 0xffffff,
    'R': 0xff3333,
    'F': 0x00cc00,
    'D': 0xffcc00,
    'L': 0xff6600,
    'B': 0x0066ff
};

export const API_URL = '/api/solve';

// Trạng thái toàn cục (được chia sẻ giữa các module)
export const state = {
    isCubeScrambled: false,
    currentSolveMode: 'facelet',
    currentPaintColor: 'U',
    faceletColors: new Array(54).fill(''),
    currentSolution: null,
    currentFaceletString: ''
};

// Hàm cập nhật trạng thái UI dùng chung
export function updateStatus(text, stateClass = '') {
    const statusEl = document.getElementById('cube-status');
    if (statusEl) {
        statusEl.textContent = text;
        statusEl.className = 'cube-status';
        if (stateClass) statusEl.classList.add(stateClass);
    }
}

export function clearSolution() {
    document.getElementById('solution-moves').innerHTML = '';
    document.getElementById('move-count').textContent = '0';
    document.getElementById('phase1-count').textContent = '0';
    document.getElementById('phase2-count').textContent = '0';
    document.getElementById('solve-time').textContent = '0';
    state.currentSolution = null;
}
