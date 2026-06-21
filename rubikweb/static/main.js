import { state, COLORS, updateStatus, clearSolution } from './globals.js';
import { isValidScramble, isValidPieces } from './validators.js';
import { initCube3D, resetCube, applyMoves, cubes, rotateLayer } from './cube3d.js';
import { solveRubikApi } from './api.js';

// Init 3D Cube
initCube3D('cube-canvas');

const GRID_LAYOUT = { 'U': [2,1], 'L': [1,2], 'F': [2,2], 'R': [3,2], 'B': [4,2], 'D': [2,3] };

function initFaceletMap() {
    const mapContainer = document.getElementById('facelet-map');
    if (!mapContainer) return;
    mapContainer.innerHTML = '';
    
    const faces = ['U', 'R', 'F', 'D', 'L', 'B'];
    const unpaintedColor = '#444444';
    
    faces.forEach((face, fIdx) => {
        const faceDiv = document.createElement('div');
        faceDiv.className = 'map-face';
        faceDiv.style.gridColumn = GRID_LAYOUT[face][0];
        faceDiv.style.gridRow = GRID_LAYOUT[face][1];
        
        for (let i = 0; i < 9; i++) {
            const cellIdx = fIdx * 9 + i;
            const cell = document.createElement('div');
            cell.className = 'map-cell';
            cell.dataset.idx = cellIdx;

            if (i === 4) {
                state.faceletColors[cellIdx] = face;
                cell.style.backgroundColor = '#' + COLORS[face].toString(16).padStart(6, '0');
                cell.style.cursor = 'not-allowed';
            } else {
                state.faceletColors[cellIdx] = '';
                cell.style.backgroundColor = unpaintedColor;
                
                cell.addEventListener('mousedown', function(e) {
                    if (e.buttons === 1 || e.type === 'mousedown') {
                        state.faceletColors[cellIdx] = state.currentPaintColor;
                        this.style.backgroundColor = '#' + COLORS[state.currentPaintColor].toString(16).padStart(6, '0');
                    }
                });
                cell.addEventListener('mouseenter', function(e) {
                    if (e.buttons === 1) {
                        state.faceletColors[cellIdx] = state.currentPaintColor;
                        this.style.backgroundColor = '#' + COLORS[state.currentPaintColor].toString(16).padStart(6, '0');
                    }
                });
            }
            
            faceDiv.appendChild(cell);
        }
        mapContainer.appendChild(faceDiv);
    });
}

document.querySelectorAll('.color-swatch').forEach(swatch => {
    swatch.addEventListener('click', (e) => {
        document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('active'));
        e.target.classList.add('active');
        state.currentPaintColor = e.target.dataset.color;
    });
});

initFaceletMap();

document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        const targetTab = e.target.dataset.tab;
        document.getElementById(targetTab).classList.add('active');
        
        state.currentSolveMode = (targetTab === 'color-tab') ? 'facelet' : 'scramble';
    });
});

document.getElementById('perform-scramble-btn').addEventListener('click', async () => {
    let scrambleInput = document.getElementById('scramble-input').value.trim();
    if (!scrambleInput) return;

    if (!isValidScramble(scrambleInput)) {
        alert("Scramble must only contain characters U, U', U2, D, D', D2, R, R', R2, L, L', L2, F, F', F2, B, B', B2 separated by spaces.");
        return;
    }
    scrambleInput = scrambleInput.toUpperCase();
    document.getElementById('scramble-input').value = scrambleInput;

    clearSolution();

    const performBtn = document.getElementById('perform-scramble-btn');
    const solveBtn = document.getElementById('solve-btn');
    const randomBtn = document.getElementById('random-btn');

    performBtn.disabled = true;
    solveBtn.disabled = true;
    randomBtn.disabled = true;
    performBtn.textContent = '🔄 Scrambling...';

    resetCube();
    await new Promise(r => setTimeout(r, 100));

    const moves = scrambleInput.split(/\s+/); 
    await applyMoves(moves);

    state.isCubeScrambled = true;
    updateStatus('Scrambled (Waiting for solve)', 'status-scrambling');

    performBtn.disabled = false;
    solveBtn.disabled = false;
    randomBtn.disabled = false;
    performBtn.textContent = '🔄 Perform Scramble';
});

document.getElementById('apply-color-btn').addEventListener('click', () => {
    if (state.faceletColors.includes('')) {
        alert("⚠️ Please paint all 54 cells on the Rubik's cube!");
        return;
    }

    const colorCount = {};
    state.faceletColors.forEach(c => colorCount[c] = (colorCount[c] || 0) + 1);
    for (const face of ['U', 'R', 'F', 'D', 'L', 'B']) {
        if (colorCount[face] !== 9) {
            alert(`⚠️ Color input error: The Rubik's cube must have exactly 9 cells for each color!\nCurrently, color [${face}] has ${colorCount[face] || 0} cells.`);
            return;
        }
    }

    if (!isValidPieces(state.faceletColors)) {
        alert("⚠️ There are invalid corner/edge colors or incorrectly twisted/flipped pieces (incorrect clockwise order)!");
        return;
    }

    clearSolution();

    state.currentFaceletString = state.faceletColors.join('');
    resetCube();
    
    cubes.forEach(cube => {
        cube.mesh.material.forEach((mat) => {
            if (mat.name && mat.name.startsWith('facelet_')) {
                const idx = parseInt(mat.name.split('_')[1]);
                const colorKey = state.currentFaceletString[idx];
                mat.color.setHex(COLORS[colorKey]);
            }
        });
    });

    state.isCubeScrambled = true;
    updateStatus('Custom color applied', 'status-scrambling');
});

document.getElementById('reset-map-btn').addEventListener('click', initFaceletMap);

document.getElementById('solve-btn').addEventListener('click', () => {
    if (state.currentSolveMode === 'scramble') {
        let scrambleInput = document.getElementById('scramble-input').value.trim();
        if (!scrambleInput) return;
        if (!isValidScramble(scrambleInput)) {
            alert("Scramble must only contain characters U, U', U2, D, D', D2, R, R', R2, L, L', L2, F, F', F2, B, B', B2 separated by spaces.");
            return;
        }
        scrambleInput = scrambleInput.toUpperCase();
        document.getElementById('scramble-input').value = scrambleInput;
    }
    
    const solveBtn = document.getElementById('solve-btn');
    const resultPanel = document.getElementById('result-panel');
    const solutionDiv = document.getElementById('solution-moves');
    const moveCountSpan = document.getElementById('move-count');
    const phase1Span = document.getElementById('phase1-count');
    const phase2Span = document.getElementById('phase2-count');
    const timeSpan = document.getElementById('solve-time');
    
    solveRubikApi(solveBtn, resultPanel, solutionDiv, moveCountSpan, phase1Span, phase2Span, timeSpan);
});

function randomScramble() {
    const moves = ['U', "U'", 'U2', 'R', "R'", 'R2', 'F', "F'", 'F2', 'D', "D'", 'D2', 'L', "L'", 'L2', 'B', "B'", 'B2'];
    const length = 20 + Math.floor(Math.random() * 10);
    const scramble = [];
    let lastFace = '';
    
    for (let i = 0; i < length; i++) {
        let move;
        do {
            move = moves[Math.floor(Math.random() * moves.length)];
        } while (move[0] === lastFace);
        scramble.push(move);
        lastFace = move[0];
    }
    
    document.getElementById('scramble-input').value = scramble.join(' ');
    clearSolution();
}

document.getElementById('random-btn').addEventListener('click', randomScramble);

document.getElementById('play-animation')?.addEventListener('click', async () => {
    if (!state.currentSolution) return;
    
    const resetBtn = document.getElementById('reset-cube');
    const playBtn = document.getElementById('play-animation');
    const performBtn = document.getElementById('perform-scramble-btn');
    const solveBtn = document.getElementById('solve-btn');
    const randomBtn = document.getElementById('random-btn');
    
    playBtn.disabled = true;
    resetBtn.disabled = true;
    performBtn.disabled = true;
    solveBtn.disabled = true;
    randomBtn.disabled = true;
    
    if (!state.isCubeScrambled) {
        const scrambleInput = document.getElementById('scramble-input').value.trim();
        if (scrambleInput) {
            updateStatus('🔄 Scrambling automatically...', 'status-scrambling');
            resetCube(); 
            await new Promise(r => setTimeout(r, 100));
            
            const moves = scrambleInput.split(/\s+/);
            await applyMoves(moves);
            
            state.isCubeScrambled = true;
            await new Promise(r => setTimeout(r, 500));
        }
    }
    
    updateStatus('⚡ Solving...', 'status-solving');
    
    const moveSpans = document.querySelectorAll('#solution-moves span');
    
    for (let i = 0; i < state.currentSolution.length; i++) {
        moveSpans.forEach(span => span.classList.remove('current-move'));
        if (moveSpans[i]) moveSpans[i].classList.add('current-move');
        
        const move = state.currentSolution[i];
        
        let layer, axis, angle;
        const base = move[0];
        const suffix = move[1];
        
        switch(base) {
            case 'U': layer = 1; axis = 'y'; angle = suffix === "'" ? 1 : (suffix === '2' ? -2 : -1); break;
            case 'D': layer = -1; axis = 'y'; angle = suffix === "'" ? -1 : (suffix === '2' ? 2 : 1); break;
            case 'R': layer = 1; axis = 'x'; angle = suffix === "'" ? 1 : (suffix === '2' ? -2 : -1); break;
            case 'L': layer = -1; axis = 'x'; angle = suffix === "'" ? -1 : (suffix === '2' ? 2 : 1); break;
            case 'F': layer = 1; axis = 'z'; angle = suffix === "'" ? 1 : (suffix === '2' ? -2 : -1); break;
            case 'B': layer = -1; axis = 'z'; angle = suffix === "'" ? -1 : (suffix === '2' ? 2 : 1); break;
            default: continue;
        }
        
        const times = Math.abs(angle);
        const dir = Math.sign(angle);
        for (let t = 0; t < times; t++) {
            await rotateLayer(layer, axis, dir);
            await new Promise(r => setTimeout(r, 50));
        }
    }
    
    moveSpans.forEach(span => span.classList.remove('current-move'));
    
    state.isCubeScrambled = false;
    updateStatus('🎉 Solved', 'status-solved');
    
    playBtn.disabled = false;
    resetBtn.disabled = false;
    performBtn.disabled = false;
    solveBtn.disabled = false;
    randomBtn.disabled = false;
});

document.getElementById('reset-cube')?.addEventListener('click', resetCube);

document.getElementById('copy-btn')?.addEventListener('click', () => {
    if (state.currentSolution) {
        navigator.clipboard.writeText(state.currentSolution.join(' '));
        alert('Solution copied!');
    }
});

console.log('🎉 3D Cube ready!');
