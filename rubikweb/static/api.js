import { state, API_URL, clearSolution } from './globals.js';

export async function solveRubikApi(solveBtn, resultPanel, solutionDiv, moveCountSpan, phase1Span, phase2Span, timeSpan) {
    clearSolution();
    solveBtn.textContent = '⏳ Solving...';
    solveBtn.disabled = true;
    
    const isFaceletMode = (state.currentSolveMode === 'facelet');
    const apiEndpoint = isFaceletMode ? '/api/solve-by-facelet' : API_URL;
    
    const reqBody = isFaceletMode 
        ? { facelet_string: state.currentFaceletString } 
        : { scramble: document.getElementById('scramble-input').value.trim() };

    try {
        const response = await fetch(apiEndpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(reqBody)
        });
        
        const data = await response.json();
        
        if (data.success) {
            solutionDiv.innerHTML = data.solution.map((move, idx) => `<span data-idx="${idx}">${move}</span>`).join(' ');
            moveCountSpan.textContent = data.moves_count;
            phase1Span.textContent = data.phase1_moves;
            phase2Span.textContent = data.phase2_moves;
            timeSpan.textContent = data.solving_time_ms;
            
            resultPanel.classList.remove('hidden');
            state.currentSolution = data.solution;
        } else {
            alert('Solve failed: ' + (data.detail || 'Unknown error'));
        }
    } catch (error) {
        alert('Connection error: ' + error.message);
    } finally {
        solveBtn.textContent = '⚡ SOLVE NOW';
        solveBtn.disabled = false;
    }
}
