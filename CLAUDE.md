# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A standalone Python CLI application that generates static, self-contained HTML bingo cards. Designed for embedding into Google Sites pages, which requires all assets (CSS, JS, images) to be embedded directly in the HTML with no external dependencies.

## Tech Stack

- **Python 3.11+**: Core language with modern type hints (list[str], dict, TypedDict)
- **Package Manager**: uv for fast dependency management
- **CLI Framework**: Click for command-line interface
- **UI Libraries**: Rich (progress bars, tables) and Questionary (interactive prompts)
- **Logging**: Loguru (ERROR level only to avoid CLI conflicts)
- **Template Engine**: Jinja2 for HTML generation
- **Image Processing**: Pillow for optimization and base64 encoding
- **Output**: Self-contained HTML with embedded CSS/JavaScript

## Code Architecture

### Module Structure

```
bingo-app/
├── create_bingo_card.py    # Main CLI - handles user input, orchestration
├── image_processor.py       # Image utilities - loading, scaling, encoding
├── themes.py               # Theme configs - colors, fonts, emojis (TypedDict)
├── bingo.jinja            # HTML template with embedded CSS/JS
├── pyproject.toml         # Dependencies + tool configs (ruff, mypy, black, pytest)
└── images/                # Asset directory
```

### Key Design Patterns

1. **Modular Separation**: Main CLI delegates to specialized modules (image processing, themes)
2. **Type Safety**: Uses TypedDict for theme configs, modern type hints throughout
3. **Clean CLI Output**: Loguru configured for ERROR only; Rich Progress handles all user feedback
4. **Path Handling**: Pure pathlib with `.expanduser().resolve()` for all paths
5. **No Pydantic in Runtime**: Config passed as dicts for simplicity (Pydantic models exist but unused)

### Data Flow

```
CSV file → load_bingo_data() → unique list[str]
                                     ↓
                            get_random_bingo_items() → 2D grid
                                     ↓
Images → process_all_images() → base64 encodings
                                     ↓
                            generate_bingo_html_card() → self-contained HTML
```

## Development Commands

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

# Code quality checks
uv run ruff check *.py          # Linting (configured in pyproject.toml)
uv run ruff check --fix *.py    # Auto-fix issues
uv run black *.py               # Format code
uv run mypy *.py                # Type checking

# Add/remove dependencies
uv add package-name
uv remove package-name
uv lock --upgrade
```

## Important Implementation Details

### Image Processing (image_processor.py)

**Critical**: All images are converted to square aspect ratio by padding with transparency. This ensures proper reveal mechanics in the bingo grid.

**Size Limits**:
- Background images: 250KB max (configurable)
- Celebration images: 50KB max (hardcoded)
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
- Available themes: `alien`, `ghost`, `thanksgiving`, `christmas`
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

## Key Constraints & Decisions

1. **No NumPy**: Removed to reduce 20MB installation size (use `//` for integer division)
2. **Loguru ERROR-only**: INFO/WARNING suppressed to prevent progress bar conflicts
3. **No Pydantic at runtime**: Models exist but unused; dict-based config is simpler
4. **PIL/Pillow only**: Use `Image.LANCZOS` (ANTIALIAS deprecated)
5. **Pure pathlib**: All path operations use `Path.expanduser().resolve()`

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
