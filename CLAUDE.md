# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python application that generates interactive HTML bingo cards, available in two modes:

1. **CLI Tool**: Standalone command-line application for generating static HTML bingo cards
2. **Web Application**: Flask server that provides a web interface for generating and playing bingo cards

Both modes generate self-contained HTML with embedded assets (CSS, JS, images) for compatibility with platforms like Google Sites. The web application is deployable on AWS free tier using Docker and EC2.

## Tech Stack

- **Python 3.11+**: Core language with modern type hints (list[str], dict, TypedDict)
- **Package Manager**: uv for fast dependency management
- **CLI Framework**: Click for command-line interface
- **Web Framework**: Flask for web server and HTTP API
- **UI Libraries**: Rich (progress bars, tables) and Questionary (interactive prompts)
- **Logging**: Loguru (ERROR level only to avoid CLI conflicts)
- **Template Engine**: Jinja2 for HTML generation and web templates
- **Image Processing**: Pillow for optimization and base64 encoding
- **Deployment**: Docker containers deployable to AWS EC2 (t2.micro free tier)
- **Output**: Self-contained HTML with embedded CSS/JavaScript

## Code Architecture

### Module Structure

```
bingo-app/
├── create_bingo_card.py    # Main CLI - handles user input, orchestration
├── app.py                  # Flask web server - provides web interface
├── image_processor.py      # Image utilities - loading, scaling, encoding
├── themes.py               # Theme configs - colors, fonts, emojis (TypedDict)
├── bingo.jinja            # HTML template with embedded CSS/JS
├── Dockerfile             # Docker container configuration
├── deploy.sh              # AWS EC2 deployment script
├── .env.example           # Environment variables template
├── pyproject.toml         # Dependencies + tool configs (ruff, mypy, black, pytest)
└── images/                # Asset directory
```

### Key Design Patterns

1. **Modular Separation**: Main CLI delegates to specialized modules (image processing, themes)
2. **Type Safety**: Uses TypedDict for theme configs and `BingoConfig`, modern type hints throughout
3. **Clean CLI Output**: Loguru configured for ERROR only; Rich Progress handles all user feedback
4. **Path Handling**: Use `resolve_path()` utility for consistent path resolution with `.expanduser().resolve()`
5. **Minimal Dependencies**: Pydantic removed from runtime; dict-based config is simpler

### Data Flow

```
CSV file → load_bingo_data() → unique list[str]
                                     ↓
                            get_random_bingo_items() → 2D grid
                                     ↓
Images → process_all_images() → dict of base64 encodings
                                     ↓
                            generate_bingo_html_card() → self-contained HTML
```

## Development Commands

### CLI Tool (Original)
```bash
# Install dependencies (includes dev tools: pytest, ruff, mypy, black)
uv sync --extra dev

# Run the CLI
uv run create-bingo-card

# Run with arguments (non-interactive)
uv run create-bingo-card --no-interactive --tile-size 5 --output test.html

# Generate both 5x5 and 7x7 cards (default behavior when --tile-size omitted)
uv run create-bingo-card --csv-file data.csv --output my_bingo

# Test with different themes
uv run create-bingo-card --theme thanksgiving --free-center

# Custom celebration images
uv run create-bingo-card --bingo-image-path img.png --double-bingo-image-path img2.png --super-bingo-image-path img3.png
```

### Web Application (New)
```bash
# Run Flask development server
uv run python app.py

# Or using Flask CLI
uv run flask --app app run --host 0.0.0.0 --port 8080 --debug

# Test web endpoints
curl http://localhost:8080/health
curl http://localhost:8080/api/themes
curl http://localhost:8080/bingo/alien/5x5

# Production mode
FLASK_ENV=production FLASK_DEBUG=False uv run python app.py
```

### Docker & Deployment
```bash
# Build Docker image
docker build -t bingo-app .

# Run container locally
docker run -p 8080:8080 bingo-app

# Deploy to AWS EC2 (requires setup)
./deploy.sh --ecr-repo YOUR_ECR_REPO --instance-id i-1234567890abcdef0

# Deploy via SSH instead of SSM
./deploy.sh --ecr-repo YOUR_ECR_REPO --ssh-host ec2-user@YOUR_IP --ssh-key ~/.ssh/key.pem
```

### Code Quality & Testing
```bash
# Linting (configured in pyproject.toml)
uv run ruff check *.py          
uv run ruff check --fix *.py    # Auto-fix issues

# Format code
uv run black *.py               

# Type checking
uv run mypy *.py                

# Run tests (test directory configured but no tests exist yet)
uv run pytest

# Add/remove dependencies
uv add package-name
uv remove package-name
uv lock --upgrade
```

## Important Implementation Details

### Image Processing (image_processor.py)

**Critical**: All images are converted to square aspect ratio by padding with transparency. This ensures proper reveal mechanics in the bingo grid.

**Size Limits**:
- Background images: 250KB max (configurable via `target_size_kb`)
- Celebration images (h_bingo, bingo, double_bingo, super_bingo): 50KB max (hardcoded)
- Images exceeding limits are automatically scaled using binary search algorithm

**Process**: `load → make_square → scale_if_needed → encode_base64`

### Progress Bar Integration

**Do NOT** add `logger.info()` or `logger.warning()` calls during progress bar execution. This corrupts the Rich progress display.

✅ **Correct**: Update progress descriptions
```python
progress.update(task_id, description="Processing images (3/5)")
```

❌ **Wrong**: Log during progress
```python
logger.info("Processing image 3/5")  # Breaks progress bar
```

The `process_all_images()` function accepts optional `progress_task` and `progress_tracker` parameters for live updates.

### Theme System (themes.py)

Themes are defined as TypedDict structures with strict typing:
- `ThemeColors`, `ThemeMessages`, `ThemeEmojis`, `ThemeFonts`
- Available themes: `alien`, `ghost`, `thanksgiving`, `christmas`, `new_year`
- Each theme defines colors, fonts (Google Fonts), emojis, and win messages

When adding new themes: copy existing theme structure in `THEMES` dict and update all required fields.

### CSV Format

**Requirements**:
- One bingo term per line
- UTF-8 encoding
- Empty lines ignored
- Duplicates automatically removed
- Need at least N² unique items for N×N grid

### CLI Architecture

Two execution modes:
1. **Interactive**: `prompt_for_input()` uses questionary for guided setup
2. **Non-interactive**: `--no-interactive` flag uses CLI args + defaults

Default behavior: Generate **both** 5x5 and 7x7 cards unless `--tile-size` specified.

## Code Quality Standards

The project is configured with modern Python tooling in `pyproject.toml`:

- **Ruff**: Linting with pycodestyle, pyflakes, isort, flake8-bugbear, pyupgrade
- **Black**: Code formatting (100 char line length)
- **Mypy**: Type checking (lenient mode, can be strict later)
- **Pytest**: Testing framework (testpaths = ["tests"])

All code must pass `uv run ruff check *.py` before committing.

## Static HTML Output

The generated HTML is **completely self-contained**:
- All CSS/JS embedded inline
- Images encoded as base64 data URIs
- Google Fonts loaded from CDN (only external dependency)
- Uses localStorage for game state
- Pure vanilla JavaScript (no frameworks)

**Constraint**: Must work inside Google Sites iframes (no server-side code, no external assets except fonts).

## Flask Web Application (app.py)

### Architecture

The Flask app provides a web interface while reusing all CLI logic:

1. **Landing Page** (`/`): Theme and size selection interface
2. **Bingo Generation** (`/bingo/<theme>/<size>`): Real-time bingo card generation
3. **API Endpoints** (`/api/themes`, `/health`): JSON APIs for themes and health checks
4. **Error Handling**: Custom 404/400 pages with helpful navigation

### Key Features

- **Theme Selection**: Interactive preview of all 5 themes
- **Size Options**: 3x3, 5x5, 7x7 grid support with keyboard shortcuts
- **Responsive Design**: Mobile-friendly CSS with gradient backgrounds
- **Real-time Generation**: Each request generates a fresh randomized bingo card
- **Error Handling**: Validates theme names and grid sizes with helpful messages
- **Health Checks**: `/health` endpoint for deployment monitoring

### Path Resolution

**Critical**: Template and asset paths are resolved relative to `app.py` using `Path(__file__).parent.resolve()`:

```python
# Get the directory where app.py is located
APP_DIR = Path(__file__).parent.resolve()

# Build paths relative to app directory
template_path = APP_DIR / "bingo.jinja"
csv_path = APP_DIR / "Bingo Tiles.csv"
```

This ensures the Flask app works whether run from the project root or installed as a package.

### Request Flow

```
GET / → Landing page with theme/size selection
    ↓
User clicks size → JavaScript opens `/bingo/<theme>/<size>` in new tab
    ↓
Flask validates params → loads data → generates bingo grid → renders template
    ↓
Returns complete HTML bingo card (same as CLI output)
```

### Development vs Production

- **Development**: `FLASK_DEBUG=True`, auto-reload on file changes
- **Production**: `FLASK_DEBUG=False`, optimized for performance
- **Docker**: Runs as non-root user on port 8080 with health checks

## AWS Deployment

### Docker Container

- **Base**: `python:3.11-slim` for minimal footprint
- **Build**: Multi-stage build with `uv` for fast package installation
- **Security**: Non-root user, minimal runtime dependencies
- **Size**: Optimized for AWS free tier constraints
- **Health**: Built-in health check endpoint on `/health`

### Deployment Options

1. **EC2 t2.micro**: Free tier eligible, Docker-based deployment
2. **App Runner**: Simplified container deployment (alternative)
3. **Lambda**: Not suitable due to file dependencies and startup time

### Security Considerations

- **No hardcoded credentials**: Uses environment variables and IAM roles
- **Secret key**: Flask sessions require `SECRET_KEY` environment variable
- **Port exposure**: Only port 8080 exposed in container
- **User isolation**: Runs as non-root `app` user in container

### Monitoring

The deployment includes:
- **Health checks**: Docker HEALTHCHECK and `/health` endpoint
- **Logging**: Container logs accessible via `docker logs`
- **Restart policy**: `--restart unless-stopped` for automatic recovery

## Key Constraints & Decisions

1. **No NumPy**: Removed to reduce 20MB installation size (use `//` for integer division)
2. **No Pydantic**: Removed from dependencies (was unused); reduces install size
3. **Loguru ERROR-only**: INFO/WARNING suppressed to prevent progress bar conflicts
4. **PIL/Pillow only**: Use `Resampling.LANCZOS` (ANTIALIAS deprecated)
5. **Pure pathlib**: All path operations use `resolve_path()` utility

## Testing Generated HTML

After generating cards, test in:
1. Local browser (Chrome, Firefox, Safari)
2. Google Sites embed element
3. Mobile browsers (responsive design)

Check:
- Tiles click and reveal background correctly
- Win detection works (row, column, diagonal, H-pattern, super)
- Celebration images appear for different win types
- Randomize/Reset buttons function
- localStorage persists state across refreshes
