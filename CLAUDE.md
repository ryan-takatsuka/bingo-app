# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

This repository contains two versions of a bingo app:

- **bingo_v1**: A standalone Python CLI application that generates static HTML bingo cards
- **bingo_v2**: A full-featured web application with Flask backend and React frontend

## Deployment Considerations

- This bingo application is a static html file that is embedded into a Google Sites page. So it is limited to the features that are supported by this use case.

## Build and Development Commands

### Bingo V1 (CLI Version)

```bash
# Set up Python environment (Python 3.11)
conda create -n bingo-app python=3.11
conda activate bingo-app
pip install -r bingo_v1/requirements.txt

# Run the bingo card generator
python bingo_v1/create_bingo_card.py  # Interactive mode with Rich CLI
python bingo_v1/create_bingo_card.py --no-interactive [options]  # Direct CLI mode

# Common usage examples
python bingo_v1/create_bingo_card.py --csv-file data/my_terms.csv --free-center --output my_bingo_card
python bingo_v1/create_bingo_card.py --csv-file data/terms.csv --tile-size 7 --image-path images/background.jpg
```

#### V1 CLI Options
- `--csv-file`: CSV file with bingo tile values (one per line)
- `--image-path`: Background image revealed on tile selection
- `--h-bingo-image-path`: Image for H-pattern bingo celebration
- `--celebration-image-path`: Image for double/super bingo celebrations
- `--tile-size`: Grid size (generates both 5x5 and 7x7 if not specified)
- `--free-center`: Set center tile as FREE (odd sizes only)
- `--output`: Output HTML file path
- `--no-down-scaling`: Disable automatic image optimization
- `--background-color`: Hex color for background/tiles
- `--no-interactive`: Skip interactive prompts

### Bingo V2 (Web Application)

```bash
# Backend setup and development  
cd bingo_v2/backend
conda activate bingo-app
pip install -r requirements.txt
flask run --port=5001

# Frontend setup and development
cd bingo_v2/frontend
npm install
npm start         # Development server
npm run build     # Production build
npm test          # Run tests
```

## High-Level Architecture

### V1 Architecture
- **Core Script**: `create_bingo_card.py` - CLI tool using Click for command-line interface
  - Interactive mode with Rich/Questionary for enhanced terminal UI
  - Modular functions for CSV loading, image processing, and HTML generation
  - Automatic image optimization (250KB for backgrounds, 50KB for celebrations)
- **Template Engine**: Jinja2 for generating HTML from `bingo.jinja` template
  - Self-contained HTML with embedded CSS/JS (no external dependencies)
  - Alien-themed UI with animations and sound effects
  - Multiple win detection algorithms (standard, H-pattern, double, super)
- **Image Processing**: Pillow for image optimization and base64 encoding
  - Automatic resizing to maintain performance
  - Square aspect ratio enforcement for grid alignment
- **Dependencies**: numpy, click, rich, questionary, jinja2, pillow

### V2 Architecture

#### Backend (Flask)
- **Entry Point**: `backend/app.py` - Flask application with CORS enabled
- **API Routes**: RESTful endpoints for bingo card operations
- **File Handling**: Image upload/processing with automatic resizing for performance
- **Data Storage**: CSV file support for bingo tiles

#### Frontend (React)
- **Entry Point**: `frontend/src/App.js` - Main React component with routing
- **Routing**: React Router for navigation between pages
- **Pages**:
  - `HomePage`: Landing page
  - `BingoCardPage`: Main game interface
  - `SettingsPage`: Configuration options
- **Components**: Modular UI components in `components/`
- **Styling**: CSS modules in `styles/`
- **API Communication**: Axios for backend communication (proxy configured to port 5000)

## Key Features Across Versions

- Dynamic bingo card generation from CSV data
- Customizable grid sizes (5x5, 7x7, or custom)
- Background image reveal on tile selection
- Win detection (single bingo, double bingo, H-bingo)
- Celebration effects with custom images
- Image optimization to maintain performance
- Free center tile option (odd-sized grids)

## Development Workflow

1. For V1 changes: Work directly with the Python scripts and test using the CLI
2. For V2 changes: Run both backend and frontend servers concurrently for full-stack development
3. Frontend proxies to backend on port 5000 (configured in package.json)
4. All images are processed to maintain sub-250KB size for optimal performance

## Image Management

- **V1**: Images should be placed in `/bingo_v1/images/`
- **V2**: Images should ONLY be placed in `/bingo_v2/images/` (backend directory)
  - Frontend accesses images via Flask API endpoints (`/api/images/<filename>`)
  - Do NOT place images in `/bingo_v2/frontend/public/images/` - this creates unnecessary duplication
- **Image optimization**: Background images are automatically scaled to <250KB, celebration images to <50KB

## Testing Approach

- **V1**: Manual testing through CLI with various parameter combinations
  - Test interactive mode flow with different input scenarios
  - Test CLI mode with all parameter combinations
  - Verify HTML output opens correctly and all features work (tile selection, win detection, celebrations)
  - Test image optimization with various file sizes
- **V2 Frontend**: Use `npm test` for React component tests
- **V2 Backend**: Manual API testing during development (no test suite currently configured)