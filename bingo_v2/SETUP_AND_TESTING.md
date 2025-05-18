# Bingo V2 Setup and Testing Guide

## Prerequisites
- Python 3.9+
- Node.js 16+
- Git

## Setup Instructions

### Backend Setup
1. Navigate to backend directory:
   ```bash
   cd bingo_v2/backend
   ```

2. Activate conda environment:
   ```bash
   conda activate bingo-app
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest  # For testing
   ```

### Frontend Setup
1. Navigate to frontend directory:
   ```bash
   cd bingo_v2/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Running the Application

### Quick Start (Both Backend and Frontend)
```bash
cd bingo_v2
./scripts/start_app.sh
```
This will start both the backend (port 5001) and frontend (port 3001) servers.

### Individual Server Start

### Start Backend Server
Option 1 - Using the provided script:
```bash
cd bingo_v2
./scripts/run_backend.sh
```

Option 2 - Manual setup:
```bash
cd bingo_v2/backend
conda activate bingo-app
export FLASK_APP=app.py
flask run --port=5001
```

### Start Frontend Server
```bash
cd bingo_v2/frontend
PORT=3001 npm start
```

The application will be available at:
- Frontend: http://localhost:3001
- Backend API: http://localhost:5001

## Testing

### Backend Tests
Option 1 - Using the provided script:
```bash
cd bingo_v2
./scripts/test_backend.sh
```

Option 2 - Manual setup:
```bash
cd bingo_v2/backend
conda activate bingo-app
python -m pytest tests/ -v
```

### Frontend Tests
```bash
cd bingo_v2/frontend
npm test -- --watchAll=false --coverage
```

## API Endpoints

### Settings
- GET `/api/settings` - Get current settings
- POST `/api/settings/save` - Save settings
- POST `/api/settings/reset` - Reset to defaults

### Images
- GET `/api/images/<type>?name=<name>` - Get image by type (background, h_bingo, celebration)
- POST `/api/images/process` - Upload and process new image
- POST `/api/images/optimize` - Optimize existing image
- GET `/api/images/list` - List all available images

### Bingo Card
- GET `/api/bingo-card?tile_size=<size>&free_center=<bool>` - Generate new bingo card
- GET `/api/bingo-tiles` - Get all available bingo tiles

## Features Implemented

### Core Game Mechanics
- ✅ Dynamic grid sizes (3x3, 5x5, 7x7)
- ✅ Free center tile option
- ✅ Background image reveal on tile click
- ✅ Win detection (single, double, H-pattern, complete)
- ✅ Celebration animations

### UI/UX
- ✅ Alien/space theme with neon effects
- ✅ Star field background
- ✅ Responsive design
- ✅ Custom fonts and animations
- ✅ Status messages

### Settings Management
- ✅ Grid size selection
- ✅ Background color picker
- ✅ Image upload and selection
- ✅ Automatic image optimization
- ✅ Settings persistence

### Image Processing
- ✅ Automatic resizing (50KB for celebrations, 250KB for backgrounds)
- ✅ Base64 encoding for frontend
- ✅ Multi-type image support

## Troubleshooting

### Port Already in Use
If you get port conflicts:
- Backend: Use a different port with `--port=<port>`
- Frontend: Use `PORT=<port> npm start`

### CORS Issues
The backend is configured with Flask-CORS. If you still have CORS issues:
1. Check that the frontend is using the correct backend URL
2. Ensure both servers are running on the expected ports

### Image Upload Issues
- Images are automatically optimized
- Supported formats: PNG, JPG, JPEG, GIF
- Max recommended sizes: 250KB for backgrounds, 50KB for celebrations

## Development Notes

### Adding New Features
1. Backend: Add new routes in `app.py`
2. Frontend: Update components and pages as needed
3. Tests: Add corresponding tests for new functionality

### Code Style
- Python: Follow PEP 8
- JavaScript: Use ES6+ features
- React: Functional components with hooks