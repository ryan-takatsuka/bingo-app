import { detectWins, checkHPattern, getHPatternTiles } from '../utils/winDetection';

describe('Win Detection', () => {
  describe('detectWins', () => {
    it('should detect a single row win', () => {
      const revealed = ['0-0', '0-1', '0-2', '0-3', '0-4'];
      const result = detectWins(revealed, 5);
      
      expect(result.winType).toBe('single');
      expect(result.lineCount).toBe(1);
      expect(result.winningLines[0].type).toBe('row');
      expect(result.winningLines[0].index).toBe(0);
    });
    
    it('should detect a single column win', () => {
      const revealed = ['0-0', '1-0', '2-0', '3-0', '4-0'];
      const result = detectWins(revealed, 5);
      
      expect(result.winType).toBe('single');
      expect(result.lineCount).toBe(1);
      expect(result.winningLines[0].type).toBe('column');
      expect(result.winningLines[0].index).toBe(0);
    });
    
    it('should detect a diagonal win', () => {
      const revealed = ['0-0', '1-1', '2-2', '3-3', '4-4'];
      const result = detectWins(revealed, 5);
      
      expect(result.winType).toBe('single');
      expect(result.lineCount).toBe(1);
      expect(result.winningLines[0].type).toBe('diagonal');
      expect(result.winningLines[0].index).toBe(1);
    });
    
    it('should detect a double bingo', () => {
      const revealed = [
        '0-0', '0-1', '0-2', '0-3', '0-4', // Row 0
        '0-0', '1-0', '2-0', '3-0', '4-0'  // Column 0
      ];
      const result = detectWins(revealed, 5);
      
      expect(result.winType).toBe('double');
      expect(result.lineCount).toBe(2);
    });
    
    it('should detect a complete board', () => {
      const revealed = [];
      for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 3; j++) {
          revealed.push(`${i}-${j}`);
        }
      }
      const result = detectWins(revealed, 3);
      
      expect(result.winType).toBe('complete');
      expect(result.isComplete).toBe(true);
    });
    
    it('should detect no win', () => {
      const revealed = ['0-0', '1-1', '2-2'];
      const result = detectWins(revealed, 5);
      
      expect(result.winType).toBe(null);
      expect(result.lineCount).toBe(0);
    });
  });
  
  describe('checkHPattern', () => {
    it('should detect H-pattern on 5x5 grid', () => {
      const revealed = [
        // Left column
        '0-0', '1-0', '2-0', '3-0', '4-0',
        // Right column  
        '0-4', '1-4', '2-4', '3-4', '4-4',
        // Middle row
        '2-1', '2-2', '2-3'
      ];
      
      expect(checkHPattern(revealed, 5)).toBe(true);
    });
    
    it('should detect H-pattern on 7x7 grid', () => {
      const revealed = [
        // Left column
        '0-0', '1-0', '2-0', '3-0', '4-0', '5-0', '6-0',
        // Right column  
        '0-6', '1-6', '2-6', '3-6', '4-6', '5-6', '6-6',
        // Middle row
        '3-1', '3-2', '3-3', '3-4', '3-5'
      ];
      
      expect(checkHPattern(revealed, 7)).toBe(true);
    });
    
    it('should not detect H-pattern on even grids', () => {
      const revealed = ['0-0', '1-0', '0-3', '1-3', '0-1', '0-2'];
      expect(checkHPattern(revealed, 4)).toBe(false);
    });
    
    it('should not detect incomplete H-pattern', () => {
      const revealed = [
        // Left column
        '0-0', '1-0', '2-0', '3-0', '4-0',
        // Right column (missing one)
        '0-4', '1-4', '2-4', '3-4',
        // Middle row
        '2-1', '2-2', '2-3'
      ];
      
      expect(checkHPattern(revealed, 5)).toBe(false);
    });
  });
  
  describe('getHPatternTiles', () => {
    it('should return correct tiles for 5x5 grid', () => {
      const tiles = getHPatternTiles(5);
      expect(tiles).toContain('0-0'); // Left column
      expect(tiles).toContain('4-0'); // Left column
      expect(tiles).toContain('0-4'); // Right column
      expect(tiles).toContain('4-4'); // Right column
      expect(tiles).toContain('2-1'); // Middle row
      expect(tiles).toContain('2-3'); // Middle row
      expect(tiles).toHaveLength(13); // 5 + 5 + 3
    });
    
    it('should return correct tiles for 7x7 grid', () => {
      const tiles = getHPatternTiles(7);
      expect(tiles).toHaveLength(19); // 7 + 7 + 5
    });
  });
});