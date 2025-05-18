# Bingo V2 Refactoring Plan

## Overview
This document outlines the comprehensive plan to refactor Bingo V2 to achieve feature parity with V1 while leveraging the benefits of a modern web application architecture.

## Current State Analysis

### V1 Features (Complete)
- Static HTML bingo card generation
- Customizable grid sizes (5x5, 7x7)
- Background image reveal on tile click
- Multiple win detection types:
  - Single bingo (row/column/diagonal)
  - Double bingo
  - H-bingo pattern
  - Super bingo (complete board)
- Celebration animations for each win type
- Alien/space theme with neon effects
- Image optimization (50KB for celebrations, 250KB for backgrounds)
- Free center tile option
- CSV-based tile content
- Command-line interface with interactive mode

### V2 Current State
- Basic React frontend with routing
- Flask backend with CORS support
- Partial bingo card generation
- Mock data fallback
- Basic tile click functionality
- Incomplete win detection
- Missing celebration effects
- No image reveal functionality
- Limited customization options

## Missing Features in V2

1. **Core Game Mechanics**
   - Background image reveal on tile click
   - Complete win detection algorithms
   - H-pattern detection
   - Celebration triggers

2. **Image Handling**
   - Image upload/selection
   - Image optimization
   - Base64 encoding for frontend
   - Multiple image types (background, h-bingo, celebration)

3. **UI/UX Features**
   - Alien/space theme
   - Neon glow effects
   - Star background animation
   - UFO hover animations
   - Celebration animations

4. **Customization**
   - Dynamic grid sizes
   - Background color picker
   - Image selection
   - Theme options

5. **State Management**
   - Persistent game state
   - Settings storage
   - Progress tracking

## Implementation Phases

### Phase 1: Backend Enhancements

#### 1.1 Image Processing API
```python
# New endpoints needed:
/api/images/process
/api/images/optimize
/api/images/list
```

**Tasks:**
- Implement image size optimization (scale_image_to_target_size)
- Add base64 encoding for all image types
- Support different size limits per image type
- Create image management endpoints

#### 1.2 Enhanced Card Generation
```python
# Update existing endpoint:
/api/bingo-card
```

**Tasks:**
- Fix free center tile logic for odd-sized grids
- Support dynamic grid sizes (3x3, 5x5, 7x7, custom)
- Add validation for tile count vs grid size
- Implement proper randomization

#### 1.3 Settings Management
```python
# New endpoints:
/api/settings
/api/settings/save
/api/settings/load
```

**Tasks:**
- Create settings model
- Implement CRUD operations
- Add default settings fallback

### Phase 2: Frontend Core Functionality

#### 2.1 BingoCardPage Complete Refactor

**File:** `frontend/src/pages/BingoCardPage.js`

**Tasks:**
- Add background image state and reveal logic
- Implement complete win detection:
  ```javascript
  // Win detection functions needed:
  checkRowWin()
  checkColumnWin()
  checkDiagonalWin()
  checkHPattern()
  checkCompleteBingo()
  ```
- Add celebration state management
- Support dynamic grid rendering
- Implement tile flip animations

#### 2.2 Win Detection Implementation

**New file:** `frontend/src/utils/winDetection.js`

```javascript
export const detectWins = (revealedTiles, gridSize) => {
  // Return object with:
  // - winType: 'single', 'double', 'h-pattern', 'complete'
  // - winningTiles: array of winning tile IDs
  // - lineCount: number of winning lines
};
```

#### 2.3 Celebration System

**New file:** `frontend/src/components/Celebrations.js`

**Components needed:**
- `SingleBingoCelebration`
- `DoubleBingoCelebration`
- `HBingoCelebration`
- `SuperBingoCelebration`

**Effects to implement:**
- Alien confetti
- UFO animations
- Neon pulse effects
- Image overlays
- Sound effects (optional)

### Phase 3: UI/Theme Implementation

#### 3.1 Alien/Space Theme

**Files to update:**
- `frontend/src/styles/App.css`
- `frontend/src/styles/BingoCard.css`

**Tasks:**
- Port CSS variables from V1
- Add keyframe animations:
  - `neonPulse`
  - `alienScan`
  - `ufoHover`
  - `starTwinkle`
- Implement gradient backgrounds
- Add glow effects

#### 3.2 Enhanced Settings Page

**File:** `frontend/src/pages/SettingsPage.js`

**New features:**
- Image upload component
- Color picker for background
- Grid size selector with preview
- Theme selector
- Save/load functionality

#### 3.3 Responsive Design Updates

**Tasks:**
- Dynamic font sizing based on grid
- Mobile-optimized touch interactions
- Viewport-based scaling
- Orientation handling

### Phase 4: State Management

#### 4.1 React Context Setup

**New file:** `frontend/src/context/GameContext.js`

```javascript
const GameContext = createContext({
  gameState: {},
  settings: {},
  updateGame: () => {},
  updateSettings: () => {},
});
```

#### 4.2 Local Storage Integration

**New file:** `frontend/src/utils/storage.js`

**Functions:**
- `saveGameState()`
- `loadGameState()`
- `saveSettings()`
- `loadSettings()`
- `clearAllData()`

#### 4.3 Backend Persistence

**Tasks:**
- Add database models for game state
- Create save/load endpoints
- Implement auto-save functionality

### Phase 5: Additional Features

#### 5.1 Image Management

**New component:** `frontend/src/components/ImageManager.js`

**Features:**
- Upload interface
- Image preview
- Selection UI
- Optimization status

#### 5.2 Game Statistics

**New component:** `frontend/src/components/GameStats.js`

**Track:**
- Games played
- Win types achieved
- Average time to win
- Favorite tiles

#### 5.3 Accessibility

**Tasks:**
- Add ARIA labels
- Keyboard navigation
- Screen reader support
- High contrast mode

### Phase 6: Testing & Quality

#### 6.1 Backend Tests

**Files to create:**
- `backend/tests/test_image_processing.py`
- `backend/tests/test_card_generation.py`
- `backend/tests/test_settings.py`

#### 6.2 Frontend Tests

**Files to create:**
- `frontend/src/__tests__/winDetection.test.js`
- `frontend/src/__tests__/BingoCard.test.js`
- `frontend/src/__tests__/Celebrations.test.js`

#### 6.3 Performance Optimization

**Tasks:**
- Implement lazy loading
- Optimize animation performance
- Minimize bundle size
- Add loading states
- Implement error boundaries

## Implementation Priority

### High Priority (Core Functionality)
1. Win detection algorithms
2. Background image reveal
3. Basic celebration effects
4. Grid size support
5. Free center tile

### Medium Priority (Enhanced Features)
1. Full theme implementation
2. All celebration animations
3. Image upload/management
4. Settings persistence
5. Responsive design

### Low Priority (Nice to Have)
1. Game statistics
2. Sound effects
3. Multiplayer support
4. Advanced animations
5. PWA features

## Technical Recommendations

### Frontend
- Use React hooks for all components
- Implement custom hooks for game logic
- Use CSS modules for styling
- Add TypeScript (optional)
- Use React.memo for performance

### Backend
- Add request validation
- Implement proper error handling
- Use environment variables
- Add logging
- Consider adding Redis for caching

### DevOps
- Set up CI/CD pipeline
- Add pre-commit hooks
- Configure ESLint/Prettier
- Add Docker support
- Create deployment scripts

## Migration Strategy

1. **Incremental Updates**
   - Keep V1 functional during development
   - Test features in isolation
   - Gradual rollout

2. **Data Migration**
   - Port existing CSV files
   - Convert static assets
   - Maintain backwards compatibility

3. **Testing Strategy**
   - Unit tests for each component
   - Integration tests for API
   - End-to-end tests for workflows
   - Performance benchmarks

## Timeline Estimate

- **Phase 1**: 2-3 days (Backend)
- **Phase 2**: 3-4 days (Core Frontend)
- **Phase 3**: 2-3 days (UI/Theme)
- **Phase 4**: 1-2 days (State Management)
- **Phase 5**: 2-3 days (Additional Features)
- **Phase 6**: 2-3 days (Testing)

**Total estimate**: 12-18 days for complete implementation

## Success Metrics

1. **Feature Parity**: All V1 features working in V2
2. **Performance**: Page load < 3s, smooth animations
3. **Accessibility**: WCAG 2.1 AA compliance
4. **Code Quality**: >80% test coverage
5. **User Experience**: Intuitive interface, responsive design

## Conclusion

This refactoring plan provides a roadmap to transform Bingo V2 into a fully-featured web application that maintains all the functionality of V1 while adding the benefits of a modern web architecture. The phased approach allows for incremental development and testing, ensuring a stable migration path.