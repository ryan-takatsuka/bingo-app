# Bingo Card Generator

A customizable bingo card generator that creates interactive HTML bingo cards from CSV data with background images and celebration effects.

## Installation

### Prerequisites

This application requires Python 3.11 or higher and uses [uv](https://github.com/astral-sh/uv) for fast, reliable package management.

#### Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Option 1: Install from Source (Recommended)

Install the bingo card generator from the project directory:

```bash
# Clone or navigate to the project directory
cd bingo-app

# Install the package and all dependencies
uv sync

# The CLI commands are now available
uv run create-bingo-card
uv run create-spooky-bingo
```

### Option 2: Development Mode

For active development where you want changes to be immediately reflected:

```bash
# Install in development mode
uv pip install -e .

# Run commands directly (no 'uv run' prefix needed)
create-bingo-card
create-spooky-bingo
```

## Running the Bingo Card Generator

### Using uv run (Recommended)

```bash
# Use the CLI command with uv run
uv run create-bingo-card

# Or use the alias
uv run create-spooky-bingo
```

### If you installed in development mode:

```bash
# Run commands directly
create-bingo-card
create-spooky-bingo
```

### Running from source:

```bash
# Run the Python script directly with uv
uv run python create_bingo_card.py
```

### Usage Options

You can run the generator in two ways:

1. **Interactive Mode**: Run the command with no arguments, and the CLI will walk you through all configuration options.

    ```bash
    # Using uv run
    uv run create-bingo-card

    # If installed in dev mode
    create-bingo-card

    # Running from source
    uv run python create_bingo_card.py
    ```

2. **Command-line Arguments**: Provide specific options directly as arguments.

    ```bash
    # Using uv run
    uv run create-bingo-card --csv-file my_tiles.csv --image-path background.jpg

    # If installed in dev mode
    create-bingo-card --csv-file my_tiles.csv --image-path background.jpg

    # Running from source
    uv run python create_bingo_card.py --csv-file my_tiles.csv --image-path background.jpg
    ```

### Command-line Options

Generate a bingo card HTML file from a CSV of tile values and a background image.

| Option | Type | Description |
|--------|------|-------------|
| `--csv-file` | PATH | Path to the CSV file with bingo tile values |
| `--image-path` | PATH | Path to the background image to reveal on the board |
| `--h-bingo-image-path` | PATH | Path to the image used for H-bingo celebration |
| `--celebration-image-path` | PATH | Path to the image used for double and super bingo celebrations |
| `--tile-size` | INTEGER | Number of rows and columns in the bingo grid (if not specified, 5x5 and 7x7 will be generated) |
| `--free-center` | FLAG | Set center tile as FREE (only works with odd tile size) |
| `--output` | TEXT | Output HTML file path (will be appended with _5x5 or _7x7 if tile-size is not specified) |
| `--no-down-scaling` | FLAG | Disable automatic image scaling (images > 250KB will be scaled down by default) |
| `--background-color` | TEXT | Hex color for the background and tiles (e.g. #0a0a30) |
| `--theme` | TEXT | Theme to use (alien or ghost) - default: alien |
| `--no-interactive` | FLAG | Skip interactive prompts and use specified arguments + defaults |
| `--help` | FLAG | Show this message and exit |

## Examples

Generate a standard 5×5 bingo card with a free center:

```bash
# Using uv run
uv run create-bingo-card --csv-file data/my_terms.csv --free-center --output my_bingo_card

# If installed in dev mode
create-bingo-card --csv-file data/my_terms.csv --free-center --output my_bingo_card

# Running from source
uv run python create_bingo_card.py --csv-file data/my_terms.csv --free-center --output my_bingo_card
```

Generate a custom 7×7 bingo card with a background image:

```bash
# Using uv run
uv run create-bingo-card --csv-file data/lots_of_terms.csv --tile-size 7 --image-path images/background.jpg

# If installed in dev mode
create-bingo-card --csv-file data/lots_of_terms.csv --tile-size 7 --image-path images/background.jpg

# Running from source
uv run python create_bingo_card.py --csv-file data/lots_of_terms.csv --tile-size 7 --image-path images/background.jpg
```

Generate a ghost hunt themed bingo card:

```bash
# Using uv run
uv run create-spooky-bingo --theme ghost --csv-file ghost_hunt_tiles.csv --output ghost_hunt

# If installed in dev mode
create-spooky-bingo --theme ghost --csv-file ghost_hunt_tiles.csv --output ghost_hunt

# Running from source
uv run python create_bingo_card.py --theme ghost --csv-file ghost_hunt_tiles.csv --output ghost_hunt
```

## Themes

The bingo card generator supports multiple themes:

### Alien Theme (Default)
- Space/alien themed with purple and cyan colors
- UFO and alien emojis
- Neon glow effects
- Messages: "BINGO!", "DOUBLE BINGO!", "H BINGO!", "You are a God Gamer"

### Ghost Theme
- Spooky ghost hunt theme with dark purple and orange colors
- Ghost, bat, and pumpkin emojis
- Eerie font styles (Creepster, Nosifer, Eater)
- Messages: "GHOST CAPTURED!", "DOUBLE CAPTURE!", "HAUNTED PATTERN!", "Master Ghost Hunter!"

To use a theme, add the `--theme` option:

```bash
uv run create-bingo-card --theme ghost
```

## Updating Google Sites

After generating your bingo cards, follow these steps to update the Google Sites page:

1. **Generate the bingo HTML files**
   ```bash
   # Using uv run
   uv run create-bingo-card

   # If installed in dev mode
   create-bingo-card

   # Running from source
   uv run python create_bingo_card.py
   ```
   This will create your bingo HTML files (e.g., `bingo_5x5.html` and `bingo_7x7.html`)

2. **Go to Google Sites**
   - Navigate to https://sites.google.com
   - Click on "Spooky Saturday Bingo"

3. **Update the 5×5 bingo card**
   - Open the `bingo_5x5.html` file in a text editor
   - Select all content (Ctrl+A or Cmd+A) and copy it
   - On the Google Sites page, click on the 5×5 bingo card element to select it
   - Click the edit button (pencil icon)
   - Delete all existing content in the embed element
   - Paste the copied HTML content
   - Click "Insert" or "Update" to save

4. **Update the 7×7 bingo card**
   - Repeat step 3 for the `bingo_7x7.html` file and the bigger bingo tab/element

## Notes

- If you don't specify a tile size, the script will automatically generate both 5×5 and 7×7 cards
- The FREE center option only works with odd-numbered tile sizes (5×5, 7×7, etc.)
- Large background images (>250KB) will be automatically scaled down unless you use the `--no-down-scaling` option
- Themes automatically set appropriate colors, fonts, and messages - you can still override the background color with `--background-color`