export function isValidScramble(scrambleStr) {
    if (!scrambleStr) return true;
    const validMoves = ["U", "U'", "U2", "D", "D'", "D2", "R", "R'", "R2", "L", "L'", "L2", "F", "F'", "F2", "B", "B'", "B2"];
    const moves = scrambleStr.toUpperCase().trim().split(/\s+/);
    return moves.every(move => validMoves.includes(move));
}





export function isValidPieces(faceletArray) {
    const edgeIndices = [
        [5, 10], [7, 19], [3, 37], [1, 46],
        [32, 16], [28, 25], [30, 43], [34, 52],
        [23, 12], [21, 41], [48, 14], [50, 39]
    ];
    const validEdges = new Set([
        "UR", "RU", "UF", "FU", "UL", "LU", "UB", "BU",
        "DR", "RD", "DF", "FD", "DL", "LD", "DB", "BD",
        "FR", "RF", "FL", "LF", "BR", "RB", "BL", "LB"
    ]);

    for (let [i1, i2] of edgeIndices) {
        let edgeStr = faceletArray[i1] + faceletArray[i2];
        if (!validEdges.has(edgeStr)) return false;
    }

    const cornerIndices = [
        [8, 9, 20],   // URF
        [6, 18, 38],  // UFL
        [0, 36, 47],  // ULB
        [2, 45, 11],  // UBR
        [29, 26, 15], // DFR
        [27, 44, 24], // DLF
        [33, 53, 42], // DBL
        [35, 17, 51]  // DRB
    ];
    const baseCorners = ["URF", "UFL", "ULB", "UBR", "DFR", "DLF", "DBL", "DRB"];
    const validCorners = new Set();
    baseCorners.forEach(c => {
        validCorners.add(c);
        validCorners.add(c[1] + c[2] + c[0]);
        validCorners.add(c[2] + c[0] + c[1]);
    });

    for (let [i1, i2, i3] of cornerIndices) {
        let cornerStr = faceletArray[i1] + faceletArray[i2] + faceletArray[i3];
        if (!validCorners.has(cornerStr)) return false;
    }

    return true;
}
