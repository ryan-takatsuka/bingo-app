# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a standalone Python CLI application that generates static, self-contained HTML bingo cards. The application is designed to be embedded into Google Sites pages, which limits it to features that work within static HTML constraints.

## Tech Stack

- **Python 3.11**: Core language (managed via Conda environment)
- **CLI Framework**: Click for command-line interface
- **UI Libraries**: Rich and Questionary for enhanced interactive terminal experience
- **Template Engine**: Jinja2 for HTML generation
- **Image Processing**: Pillow (PIL) for image optimization and base64 encoding
- **Data Processing**: NumPy for array operations
- **Output**: Self-contained HTML with embedded CSS/JavaScript (no external dependencies)

## Code Structure

```
bingo_v1/
├── create_bingo_card.py    # Main CLI application
├── bingo.jinja            # HTML template with embedded CSS/JS
├── requirements.txt       # Python dependencies
├── Bingo Tiles.csv       # Sample CSV data file
├── images/               # Image assets directory
│   ├── default_background.png
│   ├── god_gamer.png
│   ├── hexy_bald.png
│   ├── rat_king.png
│   └── real_hexy_bald.png
├── bingo_5x5.html        # Sample generated output
└── bingo_7x7.html        # Sample generated output
```

## Application Generation Process

1. **Data Loading**: Reads bingo tile values from CSV file (one value per line)
2. **Image Processing**: 
   - Loads and optimizes images (background, H-bingo, celebration)
   - Automatically scales down images >250KB for performance
   - Converts images to base64 for embedding in HTML
3. **Grid Generation**:
   - Creates randomized bingo grids (5x5, 7x7, or custom size)
   - Optionally sets center tile as "FREE" for odd-sized grids
4. **HTML Generation**:
   - Uses Jinja2 template to generate static HTML
   - Embeds all assets (CSS, JS, images) directly in the HTML
   - No external dependencies or API calls

## Key Features

- **Interactive CLI**: Two modes - interactive prompts or direct command-line arguments
- **Multiple Grid Sizes**: Supports 5x5, 7x7, or custom sizes
- **Background Reveal**: Clicking tiles reveals portions of a background image
- **Win Detection**: 
  - Standard bingo (row, column, diagonal)
  - H-pattern bingo
  - Double bingo
  - Super bingo (all tiles)
- **Celebration Effects**: Custom images and animations for different win types
- **Sound Effects**: Embedded audio for interactions (alien-themed)
- **Fully Self-Contained**: All assets embedded as base64 in the HTML

## Static HTML Architecture

The generated HTML file is completely self-contained:
- **No External Resources**: All CSS, JavaScript, images, and fonts are embedded
- **No Server Required**: Runs entirely in the browser
- **Google Sites Compatible**: Designed to work within iframe restrictions
- **State Management**: Uses localStorage for game state persistence
- **Event Handling**: Pure JavaScript for all interactions

## Best Practices

1. **Image Optimization**: Always use the built-in image scaling to keep file sizes manageable
2. **CSV Format**: Ensure CSV files have one bingo term per line, no headers
3. **Testing**: Test generated HTML files in various browsers and within Google Sites
4. **Grid Size**: Consider usability when choosing grid sizes (5x5 and 7x7 are optimal)
5. **Free Center**: Only enable for odd-sized grids where it makes sense

## Development Commands

```bash
# Set up environment
conda create -n bingo-app python=3.11
conda activate bingo-app
pip install -r requirements.txt

# Run interactive mode
python create_bingo_card.py

# Run with command-line arguments
python create_bingo_card.py --csv-file data.csv --tile-size 5 --free-center

# Generate both 5x5 and 7x7 cards
python create_bingo_card.py --csv-file data.csv --output my_bingo
```

## CLI Options

- `--csv-file`: Path to CSV file with bingo tile values
- `--image-path`: Background image to reveal
- `--h-bingo-image-path`: Image for H-pattern celebration
- `--celebration-image-path`: Image for double/super bingo
- `--tile-size`: Grid dimension (generates both 5x5 and 7x7 if not specified)
- `--free-center`: Set center tile as FREE
- `--output`: Output HTML file path
- `--no-down-scaling`: Disable automatic image optimization
- `--background-color`: Hex color for theme
- `--no-interactive`: Skip interactive prompts

## Important Notes

- The application generates static HTML that works offline
- All game logic runs client-side in JavaScript
- No analytics or tracking included
- Designed for embedding in restricted environments like Google Sites
- Images are automatically optimized to maintain reasonable file sizes