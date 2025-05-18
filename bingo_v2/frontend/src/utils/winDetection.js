// Win detection algorithms for bingo game

export const detectWins = (revealedTiles, gridSize) => {
  const revealed = new Set(revealedTiles);
  const winningLines = [];
  const winningTiles = new Set();
  
  // Check rows
  for (let row = 0; row < gridSize; row++) {
    const rowTiles = [];
    let isWin = true;
    
    for (let col = 0; col < gridSize; col++) {
      const tileId = `${row}-${col}`;
      rowTiles.push(tileId);
      if (!revealed.has(tileId)) {
        isWin = false;
        break;
      }
    }
    
    if (isWin) {
      winningLines.push({ type: 'row', index: row, tiles: rowTiles });
      rowTiles.forEach(tile => winningTiles.add(tile));
    }
  }
  
  // Check columns
  for (let col = 0; col < gridSize; col++) {
    const colTiles = [];
    let isWin = true;
    
    for (let row = 0; row < gridSize; row++) {
      const tileId = `${row}-${col}`;
      colTiles.push(tileId);
      if (!revealed.has(tileId)) {
        isWin = false;
        break;
      }
    }
    
    if (isWin) {
      winningLines.push({ type: 'column', index: col, tiles: colTiles });
      colTiles.forEach(tile => winningTiles.add(tile));
    }
  }
  
  // Check diagonal (top-left to bottom-right)
  const diag1Tiles = [];
  let isDiag1Win = true;
  for (let i = 0; i < gridSize; i++) {
    const tileId = `${i}-${i}`;
    diag1Tiles.push(tileId);
    if (!revealed.has(tileId)) {
      isDiag1Win = false;
      break;
    }
  }
  
  if (isDiag1Win) {
    winningLines.push({ type: 'diagonal', index: 1, tiles: diag1Tiles });
    diag1Tiles.forEach(tile => winningTiles.add(tile));
  }
  
  // Check diagonal (top-right to bottom-left)
  const diag2Tiles = [];
  let isDiag2Win = true;
  for (let i = 0; i < gridSize; i++) {
    const tileId = `${i}-${gridSize - 1 - i}`;
    diag2Tiles.push(tileId);
    if (!revealed.has(tileId)) {
      isDiag2Win = false;
      break;
    }
  }
  
  if (isDiag2Win) {
    winningLines.push({ type: 'diagonal', index: 2, tiles: diag2Tiles });
    diag2Tiles.forEach(tile => winningTiles.add(tile));
  }
  
  // Check for H-pattern (for 5x5 and 7x7 grids)
  const isHPattern = checkHPattern(revealed, gridSize);
  
  // Check for complete board
  const isComplete = revealed.size === gridSize * gridSize;
  
  // Determine win type
  let winType = null;
  if (isComplete) {
    winType = 'complete';
  } else if (isHPattern) {
    winType = 'h-pattern';
  } else if (winningLines.length >= 2) {
    winType = 'double';
  } else if (winningLines.length === 1) {
    winType = 'single';
  }
  
  return {
    winType,
    winningLines,
    winningTiles: Array.from(winningTiles),
    lineCount: winningLines.length,
    isHPattern,
    isComplete
  };
};

export const checkHPattern = (revealedTiles, gridSize) => {
  if (gridSize < 5 || gridSize % 2 === 0) {
    return false; // H-pattern only works on odd grids 5x5 or larger
  }
  
  const revealed = new Set(revealedTiles);
  const middleRow = Math.floor(gridSize / 2);
  
  // Check left column
  for (let row = 0; row < gridSize; row++) {
    if (!revealed.has(`${row}-0`)) {
      return false;
    }
  }
  
  // Check right column
  for (let row = 0; row < gridSize; row++) {
    if (!revealed.has(`${row}-${gridSize - 1}`)) {
      return false;
    }
  }
  
  // Check middle row
  for (let col = 1; col < gridSize - 1; col++) {
    if (!revealed.has(`${middleRow}-${col}`)) {
      return false;
    }
  }
  
  return true;
};

export const getHPatternTiles = (gridSize) => {
  const tiles = [];
  const middleRow = Math.floor(gridSize / 2);
  
  // Left column
  for (let row = 0; row < gridSize; row++) {
    tiles.push(`${row}-0`);
  }
  
  // Right column
  for (let row = 0; row < gridSize; row++) {
    tiles.push(`${row}-${gridSize - 1}`);
  }
  
  // Middle row (excluding corners already added)
  for (let col = 1; col < gridSize - 1; col++) {
    tiles.push(`${middleRow}-${col}`);
  }
  
  return tiles;
};