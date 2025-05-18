import React, { useState, useEffect, useCallback, useRef } from 'react';
import { detectWins } from '../utils/winDetection';
import Celebrations from '../components/Celebrations';
import '../styles/BingoCard.css';

function BingoCardPage() {
  // Load saved state from sessionStorage
  const savedState = sessionStorage.getItem('bingoState');
  const savedImages = sessionStorage.getItem('bingoImages');
  const initialState = savedState ? JSON.parse(savedState) : {
    bingoCard: null,
    revealedTiles: []
  };
  const initialImages = savedImages ? JSON.parse(savedImages) : null;
  
  const [bingoCard, setBingoCard] = useState(initialState.bingoCard);
  const [revealedTiles, setRevealedTiles] = useState(initialState.revealedTiles);
  const [loading, setLoading] = useState(!initialState.bingoCard);
  const [error, setError] = useState(null);
  const [statusMessage, setStatusMessage] = useState('');
  const [showStatus, setShowStatus] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [celebration, setCelebration] = useState(null);
  const [images, setImages] = useState(initialImages?.images || {});
  const [settings, setSettings] = useState({});
  const [backgroundImage, setBackgroundImage] = useState(initialImages?.backgroundImage || null);
  const [previousWinState, setPreviousWinState] = useState(null);
  const [imagesLoaded, setImagesLoaded] = useState(!!initialImages);
  
  const cardRef = useRef(null);
  const statusTimeoutRef = useRef(null);

  // Load settings from API
  const loadSettings = useCallback(async () => {
    try {
      const response = await fetch('/api/settings');
      const data = await response.json();
      setSettings(data);
      return data;
    } catch (err) {
      console.error('Error loading settings:', err);
      return {
        grid_size: '5x5',
        free_center: true,
        background_color: '#0a0a30'
      };
    }
  }, []);

  // Load images from API
  const loadImages = useCallback(async (settingsData) => {
    try {
      const imageTypes = ['background', 'h_bingo', 'celebration'];
      const imagePromises = imageTypes.map(async (type) => {
        const imageName = settingsData[`${type}_image`] || 'default';
        const response = await fetch(`/api/images/${type}?name=${imageName}`);
        if (!response.ok) throw new Error(`Failed to fetch ${type} image`);
        const data = await response.json();
        return { type, image: data.image };
      });
      
      const imageResults = await Promise.all(imagePromises);
      const imageMap = {};
      imageResults.forEach(({ type, image }) => {
        imageMap[type] = image;
      });
      
      setImages(imageMap);
      setBackgroundImage(imageMap.background);
      setImagesLoaded(true);
      
      // Persist images to sessionStorage
      sessionStorage.setItem('bingoImages', JSON.stringify({
        images: imageMap,
        backgroundImage: imageMap.background
      }));
      
      console.log('Background image loaded:', !!imageMap.background);
      console.log('Background image length:', imageMap.background?.length);
    } catch (err) {
      console.error('Error loading images:', err);
      // Set defaults on error
      setImages({
        background: null,
        h_bingo: null,
        celebration: null
      });
      setBackgroundImage(null);
      setImagesLoaded(true);
    }
  }, []);

  // Status message handler
  const showStatusMessage = useCallback((message, duration = 3000) => {
    if (statusTimeoutRef.current) {
      clearTimeout(statusTimeoutRef.current);
    }
    setStatusMessage(message);
    setShowStatus(true);
    statusTimeoutRef.current = setTimeout(() => {
      setShowStatus(false);
      statusTimeoutRef.current = null;
    }, duration);
  }, []);

  // Check for wins and trigger celebrations
  const checkForWins = useCallback((revealed) => {
    if (!bingoCard) return;
    
    const gridSize = parseInt(settings.grid_size?.split('x')[0] || '5');
    const winResult = detectWins(revealed, gridSize);
    
    // Only celebrate new wins
    if (previousWinState?.winType !== winResult.winType) {
      if (winResult.winType) {
        setCelebration(winResult.winType);
        
        // Show status message
        let message = '';
        switch (winResult.winType) {
          case 'single':
            message = 'BINGO!';
            break;
          case 'double':
            message = 'DOUBLE BINGO!';
            break;
          case 'h-pattern':
            message = 'H-BINGO!';
            break;
          case 'complete':
            message = 'SUPER BINGO!';
            break;
          default:
            break;
        }
        if (message) {
          showStatusMessage(message, 3000);
        }
      }
    }
    
    setPreviousWinState(winResult);
    
    // Highlight winning tiles
    const tiles = cardRef.current?.querySelectorAll('.bingo-tile');
    tiles?.forEach(tile => {
      const tileId = tile.dataset.id;
      if (winResult.winningTiles.includes(tileId)) {
        tile.classList.add('winning-tile');
      } else {
        tile.classList.remove('winning-tile');
      }
    });
  }, [bingoCard, settings, previousWinState, showStatusMessage]);

  // Fetch bingo card from API
  const fetchBingoCard = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const settingsData = await loadSettings();
      const gridSize = parseInt(settingsData.grid_size?.split('x')[0] || '5');
      const freeCenter = settingsData.free_center !== false;
      
      // Load images
      await loadImages(settingsData);
      
      // Fetch bingo card
      const response = await fetch(`/api/bingo-card?tile_size=${gridSize}&free_center=${freeCenter}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (!data.card || data.card.length !== gridSize) {
        throw new Error('Invalid card data received');
      }
      
      // Convert to tile format
      const tiles = [];
      for (let i = 0; i < gridSize; i++) {
        for (let j = 0; j < gridSize; j++) {
          const text = data.card[i][j];
          const isFree = text === 'FREE';
          tiles.push({
            id: `${i}-${j}`,
            text: isFree ? 'FREE' : text,
            isFree: isFree,
            row: i,
            col: j
          });
        }
      }
      
      setBingoCard({ 
        tiles, 
        gridSize,
        allTiles: data.all_tiles || []
      });
      
      // Don't pre-reveal free tiles - let user click them
      // const freeTiles = tiles.filter(t => t.isFree).map(t => t.id);
      // setRevealedTiles(freeTiles);
      setRevealedTiles([]);
      
    } catch (err) {
      console.error('Error fetching bingo card:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [loadSettings, loadImages]);

  // Tile click handler
  const handleTileClick = useCallback((tileId) => {
    if (isAnimating || !bingoCard) return;
    
    const tile = bingoCard.tiles.find(t => t.id === tileId);
    if (!tile) return;
    
    // Allow free tiles to be toggled too
    const newRevealedTiles = revealedTiles.includes(tileId)
      ? revealedTiles.filter(id => id !== tileId)
      : [...revealedTiles, tileId];
    
    setRevealedTiles(newRevealedTiles);
    checkForWins(newRevealedTiles);
  }, [isAnimating, bingoCard, revealedTiles, checkForWins]);

  // Randomize card
  const handleRandomize = useCallback(() => {
    if (isAnimating || !bingoCard) return;
    
    showStatusMessage('Randomizing...', 1000);
    setIsAnimating(true);
    
    // Get new random arrangement first
    const availableTiles = [...bingoCard.allTiles];
    const shuffled = availableTiles.sort(() => Math.random() - 0.5);
    const gridSize = bingoCard.gridSize;
    const newTiles = [];
    let tileIndex = 0;
    
    for (let i = 0; i < gridSize; i++) {
      for (let j = 0; j < gridSize; j++) {
        const isFree = settings.free_center && i === Math.floor(gridSize / 2) && j === Math.floor(gridSize / 2);
        newTiles.push({
          id: `${i}-${j}`,
          text: isFree ? 'FREE' : shuffled[tileIndex++],
          isFree: isFree,
          row: i,
          col: j
        });
      }
    }
    
    // Animate tiles
    const tiles = cardRef.current?.querySelectorAll('.bingo-tile');
    tiles?.forEach((tile, index) => {
      setTimeout(() => {
        tile.classList.add('randomizing');
      }, index * 20);
    });
    
    // Update state after animation starts
    setTimeout(() => {
      setBingoCard({ ...bingoCard, tiles: newTiles });
      
      // Reset all revealed tiles (don't pre-reveal free tiles)
      // const freeTiles = newTiles.filter(t => t.isFree).map(t => t.id);
      // setRevealedTiles(freeTiles);
      setRevealedTiles([]);
      setPreviousWinState(null);
      
      // Remove animation classes after animation completes
      setTimeout(() => {
        tiles?.forEach(tile => {
          tile.classList.remove('randomizing', 'winning-tile');
        });
        setIsAnimating(false);
      }, 600); // Wait for animation to complete
    }, 100); // Small delay to let animations start
  }, [isAnimating, bingoCard, settings, showStatusMessage]);

  // Reset tiles
  const handleReset = useCallback(() => {
    if (isAnimating) return;
    
    showStatusMessage('Resetting tiles...', 1500);
    setIsAnimating(true);
    
    // Immediately reset the revealed tiles state and previous win state
    setRevealedTiles([]);
    setPreviousWinState(null);
    
    const tiles = cardRef.current?.querySelectorAll('.bingo-tile');
    tiles?.forEach((tile, index) => {
      const tileId = parseInt(tile.dataset.id);
      const wasRevealed = revealedTiles.includes(tileId);
      
      // Immediately remove revealed and winning-tile classes
      tile.classList.remove('revealed', 'winning-tile');
      
      setTimeout(() => {
        if (wasRevealed) {
          // For previously revealed tiles, add resetting animation (flips to show front)
          tile.classList.add('resetting');
        } else {
          // For non-revealed tiles, add shake-only animation
          tile.classList.add('shake-only');
        }
      }, index * 20);
    });
    
    setTimeout(() => {
      tiles?.forEach(tile => {
        tile.classList.remove('resetting');
        tile.classList.remove('shake-only');
      });
      
      setIsAnimating(false);
    }, 1500);
  }, [isAnimating, bingoCard, showStatusMessage, revealedTiles]);
  
  // Save current state
  const handleSave = useCallback(() => {
    if (!bingoCard) return;
    
    const saveData = {
      bingoCard,
      revealedTiles,
      savedAt: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(saveData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bingo-save-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showStatusMessage('Game saved!', 2000);
  }, [bingoCard, revealedTiles, showStatusMessage]);
  
  // Load saved state
  const handleLoad = useCallback((event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const saveData = JSON.parse(e.target.result);
        if (saveData.bingoCard && saveData.revealedTiles) {
          setBingoCard(saveData.bingoCard);
          setRevealedTiles(saveData.revealedTiles);
          
          // Ensure images are loaded after loading a save
          if (!backgroundImage) {
            const settingsData = await loadSettings();
            await loadImages(settingsData);
          }
          
          showStatusMessage('Game loaded successfully!', 2000);
          
          // Clear the file input so the same file can be loaded again
          event.target.value = '';
        } else {
          showStatusMessage('Invalid save file', 2000);
        }
      } catch (err) {
        showStatusMessage('Error loading save file', 2000);
        console.error('Load error:', err);
      }
    };
    reader.readAsText(file);
  }, [showStatusMessage, backgroundImage, loadSettings, loadImages]);

  // Load images separately when component mounts
  useEffect(() => {
    const loadInitialImages = async () => {
      const settingsData = await loadSettings();
      await loadImages(settingsData);
    };
    loadInitialImages();
  }, [loadSettings, loadImages]);

  // Initial load and reload on settings change
  useEffect(() => {
    // Check if we need to reload the card based on settings change
    const checkSettings = async () => {
      const currentSettings = await loadSettings();
      const currentGridSize = parseInt(currentSettings.grid_size?.split('x')[0] || '5');
      
      // If grid size changed or no card exists, fetch new card
      if (!bingoCard || bingoCard.gridSize !== currentGridSize) {
        sessionStorage.removeItem('bingoState'); // Clear old state
        fetchBingoCard();
      }
    };
    
    checkSettings();
  }, []); // Run on mount
  
  // Save state to sessionStorage whenever it changes
  useEffect(() => {
    if (bingoCard) {
      sessionStorage.setItem('bingoState', JSON.stringify({
        bingoCard,
        revealedTiles
      }));
    }
  }, [bingoCard, revealedTiles]);

  // Ensure images are loaded when component becomes visible (tab switching)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && !imagesLoaded) {
        const reloadImages = async () => {
          const settingsData = await loadSettings();
          await loadImages(settingsData);
        };
        reloadImages();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    // Also check on focus
    const handleFocus = () => {
      if (!backgroundImage) {
        const reloadImages = async () => {
          const settingsData = await loadSettings();
          await loadImages(settingsData);
        };
        reloadImages();
      }
    };
    
    window.addEventListener('focus', handleFocus);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleFocus);
    };
  }, [backgroundImage, imagesLoaded, loadSettings, loadImages]);

  // Render loading state
  if (loading) {
    return (
      <div className="bingo-page">
        <h1>Loading Bingo...</h1>
        <div className="loading-spinner">🛸</div>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className="bingo-page">
        <h1>Error</h1>
        <p>{error}</p>
        <button onClick={fetchBingoCard}>Try Again</button>
      </div>
    );
  }

  const gridSize = bingoCard?.gridSize || 5;
  const gridStyle = {
    gridTemplateColumns: `repeat(${gridSize}, 1fr)`,
    gridTemplateRows: `repeat(${gridSize}, 1fr)`
  };

  // Ensure background image is applied
  const cardStyle = {
    ...gridStyle,
    backgroundImage: backgroundImage ? `url(data:image/png;base64,${backgroundImage})` : 'none',
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundRepeat: 'no-repeat',
    // Add important to ensure it's not overridden
    background: backgroundImage ? `url(data:image/png;base64,${backgroundImage}) center/cover no-repeat` : 'transparent'
  };

  return (
    <div className="bingo-page">
      <h1>BINGO</h1>
      
      {showStatus && (
        <div className="status-message">
          {statusMessage}
        </div>
      )}
      
      <div className="controls">
        <button onClick={handleRandomize} disabled={isAnimating}>
          🎲 Randomize 🎲
        </button>
        <button onClick={handleReset} disabled={isAnimating}>
          ↩️ Reset Tiles
        </button>
        <button onClick={handleSave} disabled={!bingoCard}>
          💾 Save
        </button>
        <label className="file-button">
          📂 Load
          <input
            type="file"
            accept=".json"
            onChange={handleLoad}
            style={{ display: 'none' }}
          />
        </label>
      </div>
      
      <div className="bingo-container">
        <div 
          className="bingo-card" 
          ref={cardRef}
          style={cardStyle}
        >
          {bingoCard?.tiles.map((tile, index) => {
            const isFirstTile = index === 0;
            const isTopRight = index === gridSize - 1;
            const isBottomLeft = index === gridSize * (gridSize - 1);
            const isLastTile = index === gridSize * gridSize - 1;
            
            const tileClasses = [
              'bingo-tile',
              tile.isFree ? 'free-tile' : '',
              revealedTiles.includes(tile.id) ? 'revealed' : '',
              isFirstTile ? 'top-left' : '',
              isTopRight ? 'top-right' : '',
              isBottomLeft ? 'bottom-left' : '',
              isLastTile ? 'bottom-right' : ''
            ].filter(Boolean).join(' ');
            
            return (
            <div
              key={tile.id}
              data-id={tile.id}
              className={tileClasses}
              onClick={() => handleTileClick(tile.id)}
            >
              <div className="tile-front">
                <span className="tile-text">{tile.text}</span>
              </div>
              <div className="tile-back">
                <span className="tile-text">{tile.text}</span>
              </div>
            </div>
            );
          })}
        </div>
      </div>
      
      {celebration && (
        <Celebrations
          celebrationType={celebration}
          images={{
            hBingo: images.h_bingo,
            celebration: images.celebration
          }}
          onComplete={() => setCelebration(null)}
        />
      )}
    </div>
  );
}

export default BingoCardPage;