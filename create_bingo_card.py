from pathlib import Path
from jinja2 import Template
import io
from typing import List, Optional, Dict, Any
import click
import numpy as np
import random
import base64
from PIL import Image
from io import BytesIO
import os
import questionary
import subprocess
import sys
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.text import Text
from themes import get_theme, list_themes

# Initialize rich console
console = Console()


def load_bingo_data(csv_file_path: Path) -> List[str]:
    """Load bingo tile values from a CSV file.

    Args:
        csv_file_path: Path to the CSV file containing bingo tile values.

    Returns:
        List of unique strings representing bingo tile values.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
    """
    if not csv_file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")

    with csv_file_path.open() as f:
        # Read lines, strip whitespace, and filter out empty lines
        lines = [line.strip() for line in f.readlines()]
        return list(set([line for line in lines if line]))


def escape_quotes(items: List[str]) -> List[str]:
    """Add escape character to quotes in strings so they are added properly to the HTML.

    Args:
        items: List of strings that may contain quotes.

    Returns:
        List of strings with escaped quotes.
    """
    return [item.replace('"', '\\"') for item in items]


def get_image_size_kb(img: Image.Image, format: str = "PNG") -> float:
    """Get the size of an image in kilobytes.

    Args:
        img: PIL Image object to measure.
        format: Image format to use when calculating size (default: PNG).

    Returns:
        Size of the image in kilobytes.
    """
    buffer = BytesIO()
    img.save(buffer, format=format)
    size_bytes = len(buffer.getvalue())
    return size_bytes / 1024


def scale_image_to_target_size(img: Image.Image, target_size_kb: float = 250.0, format: str = "PNG") -> Image.Image:
    """Scale an image down to meet a target file size in KB.

    Uses binary search to find the optimal scale factor that results in an image
    size close to but not exceeding the target size.

    Args:
        img: PIL Image object to scale.
        target_size_kb: Target maximum size in kilobytes (default: 250.0).
        format: Image format to use when calculating size (default: PNG).

    Returns:
        Scaled PIL Image object.
    """
    # Start with the original image
    current_img = img.copy()
    current_size_kb = get_image_size_kb(current_img, format)

    # If image is already smaller than target, return it unchanged
    if current_size_kb <= target_size_kb:
        return current_img

    # Binary search to find the right scale factor
    min_scale = 0.1
    max_scale = 1.0
    best_img = None
    best_size_kb = current_size_kb
    best_scale = max_scale

    # Try up to 10 iterations to get close to target size
    for _ in range(10):
        scale = (min_scale + max_scale) / 2
        width, height = img.size
        new_width = int(width * scale)
        new_height = int(height * scale)

        resized_img = img.resize((new_width, new_height),
                                 Image.LANCZOS if hasattr(Image, "LANCZOS") else Image.ANTIALIAS)
        size_kb = get_image_size_kb(resized_img, format)

        # Update best result if this one is closer to target
        if size_kb <= target_size_kb and size_kb > best_size_kb:
            best_img = resized_img
            best_size_kb = size_kb
            best_scale = scale

        # Adjust search range
        if size_kb > target_size_kb:
            max_scale = scale
        else:
            min_scale = scale

    # If we couldn't find a suitable size, use the smallest one
    if best_img is None:
        width, height = img.size
        new_width = int(width * min_scale)
        new_height = int(height * min_scale)
        best_img = img.resize((new_width, new_height),
                              Image.LANCZOS if hasattr(Image, "LANCZOS") else Image.ANTIALIAS)

    return best_img


def create_image_encoding_from_path(
        image_path: Path,
        target_size_kb: float = 250.0,
        no_downscaling: bool = False,
        tile_size: int = 5,
        image_type: str = "background"
) -> str:
    """
    Convert an image to a base64 encoded string for embedding in HTML.
    Adjusts the image to match the aspect ratio of the bingo grid (square)
    so the entire image fits within the grid of tiles.
    Automatically scales the image to stay under target_size_kb unless no_downscaling is True.

    Parameters:
    - image_path: Path to the image file
    - target_size_kb: Target maximum size in KB
    - no_downscaling: If True, disable automatic scaling
    - tile_size: Size of the bingo grid (for background image sizing)
    - image_type: Type of image - "background", "h_bingo", or "celebration"
                 (determines which size limit to apply)
    """
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    # Set appropriate target size based on image type
    if image_type == "h_bingo" or image_type == "celebration":
        # Use 50KB limit for celebration images
        actual_target_size_kb = 50.0
    else:
        # Use default (250KB) for background image
        actual_target_size_kb = target_size_kb

    # Read image from path
    img = Image.open(image_path)

    # Bingo grid is always square, so we want a square image
    # Create a square canvas with padding to preserve aspect ratio
    original_width, original_height = img.size

    # Determine the size of the square we need
    max_dimension = max(original_width, original_height)

    # Create a new square image with transparent background
    square_img = Image.new("RGBA", (max_dimension, max_dimension), (0, 0, 0, 0))

    # Calculate position to paste the original image so it's centered
    paste_x = (max_dimension - original_width) // 2
    paste_y = (max_dimension - original_height) // 2

    # Paste the original image on the transparent canvas
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    square_img.paste(img, (paste_x, paste_y), img if img.mode == "RGBA" else None)

    # Apply automatic scaling if needed and not disabled
    if not no_downscaling:
        current_size_kb = get_image_size_kb(square_img)
        if current_size_kb > actual_target_size_kb:
            square_img = scale_image_to_target_size(square_img, actual_target_size_kb)
            if image_type == "h_bingo" or image_type == "celebration":
                console.print(f"[yellow]{image_type.capitalize()} image automatically scaled down to stay under "
                              f"{actual_target_size_kb} KB[/]")
            else:
                console.print(f"[yellow]Image automatically scaled down to stay under {actual_target_size_kb} KB[/]")

    # Save new image to local buffer
    buffer = BytesIO()
    square_img.save(buffer, format="PNG")
    buffer.seek(0)
    img_bytes = buffer.read()

    # Encode image with base64 and return string
    base64_encoded_result_bytes = base64.b64encode(img_bytes)
    return base64_encoded_result_bytes.decode("ascii")


def load_jinja_template(template_path: Optional[Path] = None) -> Template:
    """Load the bingo Jinja template file.

    Args:
        template_path: Path to the Jinja template file. If None, defaults to 'bingo.jinja'
            in the current directory.

    Returns:
        Jinja Template object loaded from the template file.

    Raises:
        FileNotFoundError: If the template file does not exist.
    """
    if template_path is None:
        template_path = Path("bingo.jinja").resolve()

    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    # Load the jinja template
    with io.open(template_path, "r", encoding="utf-8") as f:
        return Template(f.read())


def get_random_bingo_items(items: List[str], free_center: bool = False, tile_size: int = 5) -> List[List[str]]:
    """Generate a randomized 2D grid of bingo items.

    Args:
        items: List of possible bingo tile values to choose from.
        free_center: If True, sets the center tile to 'FREE' (only works with odd tile sizes).
        tile_size: Number of rows and columns in the bingo grid (default: 5).

    Returns:
        2D list (list of lists) containing the randomized bingo grid.

    Raises:
        ValueError: If there aren't enough unique items for the requested tile size,
            or if trying to set a free center with an even-sized grid.
    """
    # Check that there are enough items to support the bingo tile size
    if len(items) < tile_size ** 2:
        raise ValueError(
            f"Not enough unique items in the CSV file "
            f"for the bingo size {tile_size}x{tile_size}. "
            f"Need at least {tile_size ** 2}, but only have {len(items)}."
        )

    # Get randomized list of items. Convert to set to ensure they are unique
    randomized_items = random.sample(items, tile_size ** 2)

    # Create the bingo data to fill the jinja html table
    bingo_data = []
    item_number = 0
    for row in range(tile_size):
        row_data = []
        for col in range(tile_size):
            row_data.append(randomized_items[item_number])
            item_number += 1
        bingo_data.append(row_data)

    # Set the center square as FREE
    if free_center:
        if tile_size % 2 == 0:
            raise ValueError("Cannot set center tile with even-sized bingo grid.")
        center_index = int(np.floor(tile_size / 2))
        bingo_data[center_index][center_index] = "FREE"

    return bingo_data


def validate_hex_color(color: str) -> bool:
    """Validate that a string is a proper hex color code.

    Args:
        color: String to validate as a hex color code (e.g., '#0a0a30').

    Returns:
        True if the string is a valid hex color code, False otherwise.
    """
    if not color.startswith("#"):
        return False

    # Remove the # prefix
    color = color[1:]

    # Check if it's a valid hex length (3, 4, 6, or 8 characters)
    if len(color) not in [3, 4, 6, 8]:
        return False

    # Check if all characters are valid hex digits
    try:
        int(color, 16)
        return True
    except ValueError:
        return False


def generate_bingo_html_card(
        initial_items: List[List[str]],
        all_bingo_items: List[str],
        image_encoding: str,
        h_bingo_image_encoding: str,
        bingo_image_encoding: str,
        double_bingo_image_encoding: str,
        super_bingo_image_encoding: str,
        output_file: Path,
        background_color: str = "#f5f9ff",
        theme_config: Optional[Dict[str, Any]] = None,
) -> Path:
    """Generate the HTML bingo card file using the Jinja template.

    Args:
        initial_items: 2D list containing the initial bingo grid layout.
        all_bingo_items: List of all possible bingo items for randomization.
        image_encoding: Base64-encoded background image string.
        h_bingo_image_encoding: Base64-encoded horizontal bingo celebration image string.
        bingo_image_encoding: Base64-encoded standard bingo celebration image string.
        double_bingo_image_encoding: Base64-encoded double bingo celebration image string.
        super_bingo_image_encoding: Base64-encoded super bingo celebration image string.
        output_file: Path where the HTML file should be saved.
        background_color: Hex color code for the background (default: '#f5f9ff').
        theme_config: Optional theme configuration dictionary.

    Returns:
        Path to the generated HTML file.
    """
    # Load jinja template and populate with bingo data
    template = load_jinja_template()
    
    # If theme config is provided, use theme colors, otherwise use defaults
    if theme_config:
        template_data = {
            "initial_items": initial_items,
            "all_bingo_items": escape_quotes(all_bingo_items),
            "image": image_encoding,
            "h_bingo_image": h_bingo_image_encoding,
            "bingo_image": bingo_image_encoding,
            "double_bingo_image": double_bingo_image_encoding,
            "super_bingo_image": super_bingo_image_encoding,
            "N_options": len(all_bingo_items),
            "background_color": theme_config["colors"]["background"],
            "theme": theme_config,
        }
    else:
        template_data = {
            "initial_items": initial_items,
            "all_bingo_items": escape_quotes(all_bingo_items),
            "image": image_encoding,
            "h_bingo_image": h_bingo_image_encoding,
            "bingo_image": bingo_image_encoding,
            "double_bingo_image": double_bingo_image_encoding,
            "super_bingo_image": super_bingo_image_encoding,
            "N_options": len(all_bingo_items),
            "background_color": background_color,
        }
    
    html_str = template.render(template_data)

    # Write output html file
    with output_file.open(mode="w", encoding="utf-8") as f:
        f.write(html_str)
    return output_file


def prompt_for_input(
        defaults: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Prompt the user for input values using questionary.

    Args:
        defaults: Dictionary containing default values for each input field.

    Returns:
        Dictionary containing the user's input values or default values if not provided.
    """
    results = {}

    # Create a rich panel with instructions
    instructions = Panel(
        "[bold cyan]Welcome to the Bingo Card Generator![/]\n\n"
        "Please provide the following information or press Enter to use the default value.",
        title="📋 Interactive Bingo Setup",
        border_style="cyan"
    )
    console.print(instructions)

    # CSV file
    csv_default = str(defaults["csv_file"])
    csv_file = questionary.text(
        "CSV file with bingo tile values:",
        default=csv_default
    ).ask()
    results["csv_file"] = csv_file or csv_default

    # Image paths
    image_default = str(defaults["image_path"])
    image_path = questionary.text(
        "Background image path:",
        default=image_default
    ).ask()
    results["image_path"] = image_path or image_default

    h_bingo_image_default = str(defaults["h_bingo_image_path"])
    h_bingo_image_path = questionary.text(
        "H-bingo celebration image path (max 50KB):",
        default=h_bingo_image_default
    ).ask()
    results["h_bingo_image_path"] = h_bingo_image_path or h_bingo_image_default

    bingo_image_default = str(defaults["bingo_image_path"])
    bingo_image_path = questionary.text(
        "Standard bingo celebration image path (max 50KB):",
        default=bingo_image_default
    ).ask()
    results["bingo_image_path"] = bingo_image_path or bingo_image_default

    double_bingo_image_default = str(defaults["double_bingo_image_path"])
    double_bingo_image_path = questionary.text(
        "Double bingo celebration image path (max 50KB):",
        default=double_bingo_image_default
    ).ask()
    results["double_bingo_image_path"] = double_bingo_image_path or double_bingo_image_default

    super_bingo_image_default = str(defaults["super_bingo_image_path"])
    super_bingo_image_path = questionary.text(
        "Super bingo celebration image path (max 50KB):",
        default=super_bingo_image_default
    ).ask()
    results["super_bingo_image_path"] = super_bingo_image_path or super_bingo_image_default

    # Ask if tile size should be specified
    specify_tile_size = questionary.confirm(
        "Do you want to specify a single tile size? (No = generate both 5x5 and 7x7)",
        default=False
    ).ask()

    if specify_tile_size:
        tile_size_default = str(defaults["tile_size"])
        tile_size = questionary.text(
            "Tile size (number of rows/columns):",
            default=tile_size_default
        ).ask()
        results["tile_size"] = int(tile_size or tile_size_default)
    else:
        results["tile_size"] = None  # Signal to generate both 5x5 and 7x7

    # Free center
    free_center = questionary.confirm(
        "Set center tile as FREE? (only works with odd tile sizes)",
        default=defaults["free_center"]
    ).ask()
    results["free_center"] = free_center

    # Output filename
    output_default = str(defaults["output"])
    output = questionary.text(
        "Output HTML file path:",
        default=output_default
    ).ask()
    results["output"] = output or output_default

    # No downscaling option
    no_downscaling = questionary.confirm(
        "Disable automatic image scaling? (celebration images > 50KB and background > 250KB will be scaled down by default)",
        default=False
    ).ask()
    results["no_downscaling"] = no_downscaling

    # Background color
    bg_color_default = defaults["background_color"]
    bg_color = questionary.text(
        "Background color (hex format, e.g. #0a0a30):",
        default=bg_color_default
    ).ask()
    results["background_color"] = bg_color or bg_color_default

    console.print("\n[green]✓[/] All inputs collected!\n")

    return results


def generate_bingo_card(
        cfg: Dict[str, Any],
        tile_size: int,
        theme_config: Optional[Dict[str, Any]] = None
) -> Path:
    """
    Generate a single bingo card with the specified tile size.

    Args:
        cfg: Dictionary containing configuration parameters for the bingo card.
        tile_size: Number of rows and columns in the bingo grid.

    Returns:
        Path to the generated HTML file.
    """
    # Prepare output filename with tile size suffix
    base_output = Path(cfg["output"])
    stem = base_output.stem
    suffix = base_output.suffix
    output_with_size = base_output.parent / f"{stem}_{tile_size}x{tile_size}{suffix}"

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
    ) as progress:
        # Set up progress tracking
        main_task = progress.add_task(f"Generating {tile_size}x{tile_size} bingo card", total=5)

        # Load data
        progress.update(main_task, description=f"Loading bingo values from {cfg['csv_file']}")
        csv_file_path = Path(cfg["csv_file"]).resolve()
        all_bingo_items = load_bingo_data(csv_file_path)
        progress.advance(main_task)

        # Generate random grid
        progress.update(main_task, description=f"Creating {tile_size}x{tile_size} bingo grid")
        initial_items = get_random_bingo_items(all_bingo_items, free_center=cfg["free_center"], tile_size=tile_size)
        progress.advance(main_task)

        # Process images
        progress.update(main_task, description="Processing background image")
        image_file_path = Path(cfg["image_path"]).resolve()
        image_encoding = create_image_encoding_from_path(
            image_file_path,
            no_downscaling=cfg["no_downscaling"],
            tile_size=tile_size,
            image_type="background"
        )

        progress.update(main_task, description="Processing celebration images (max 50KB)")
        h_bingo_image_file_path = Path(cfg["h_bingo_image_path"]).resolve()
        h_bingo_image_encoding = create_image_encoding_from_path(
            h_bingo_image_file_path,
            no_downscaling=cfg["no_downscaling"],
            image_type="h_bingo"
        )

        bingo_image_file_path = Path(cfg["bingo_image_path"]).resolve()
        bingo_image_encoding = create_image_encoding_from_path(
            bingo_image_file_path,
            no_downscaling=cfg["no_downscaling"],
            image_type="celebration"
        )

        double_bingo_image_file_path = Path(cfg["double_bingo_image_path"]).resolve()
        double_bingo_image_encoding = create_image_encoding_from_path(
            double_bingo_image_file_path,
            no_downscaling=cfg["no_downscaling"],
            image_type="celebration"
        )

        super_bingo_image_file_path = Path(cfg["super_bingo_image_path"]).resolve()
        super_bingo_image_encoding = create_image_encoding_from_path(
            super_bingo_image_file_path,
            no_downscaling=cfg["no_downscaling"],
            image_type="celebration"
        )
        progress.advance(main_task)

        # Generate HTML
        progress.update(main_task, description="Generating HTML bingo card")
        bingo_file = generate_bingo_html_card(
            initial_items=initial_items,
            all_bingo_items=all_bingo_items,
            image_encoding=image_encoding,
            h_bingo_image_encoding=h_bingo_image_encoding,
            bingo_image_encoding=bingo_image_encoding,
            double_bingo_image_encoding=double_bingo_image_encoding,
            super_bingo_image_encoding=super_bingo_image_encoding,
            output_file=output_with_size,
            background_color=cfg["background_color"],
            theme_config=theme_config,
        )
        progress.advance(main_task)

        # Complete
        progress.update(main_task, description="Bingo card generation complete!")
        progress.advance(main_task)

    return bingo_file


def show_summary(generated_files: List[Path], all_bingo_items: List[str]) -> None:
    """Display a summary of the generated bingo cards.

    Args:
        generated_files: List of paths to the generated HTML files.
        all_bingo_items: List of all bingo items used in the cards.
    """
    # Create a nice table showing the results
    table = Table(title="Generated Bingo Cards")
    table.add_column("File", style="cyan")
    table.add_column("Size", style="magenta")
    table.add_column("Items", style="green")

    for file_path in generated_files:
        file_size = os.path.getsize(file_path) / 1024  # Size in KB
        table.add_row(
            str(file_path),
            f"{file_size:.1f} KB",
            str(len(all_bingo_items))
        )

    console.print(table)
    console.print("\n[bold green]✅ Successfully generated bingo card(s)![/]")
    console.print("[italic]Open the file(s) in a web browser to play![/]")


@click.command()
@click.option(
    "--csv-file",
    type=click.Path(),
    help="Path to the CSV file with bingo tile values",
    default=None,
)
@click.option(
    "--image-path",
    type=click.Path(),
    help="Path to the background image to reveal on the board (max 250KB)",
    default=None,
)
@click.option(
    "--h-bingo-image-path",
    type=click.Path(),
    help="Path to the image used for H-bingo celebration (max 50KB)",
    default=None,
)
@click.option(
    "--bingo-image-path",
    type=click.Path(),
    help="Path to the image used for standard bingo celebration (max 50KB)",
    default=None,
)
@click.option(
    "--double-bingo-image-path",
    type=click.Path(),
    help="Path to the image used for double bingo celebration (max 50KB)",
    default=None,
)
@click.option(
    "--super-bingo-image-path",
    type=click.Path(),
    help="Path to the image used for super bingo celebration (max 50KB)",
    default=None,
)
@click.option(
    "--tile-size",
    type=int,
    help="Number of rows and columns in the bingo grid (if not specified, 5x5 and 7x7 will be generated)",
    default=None,
)
@click.option(
    "--free-center",
    is_flag=True,
    help="Set center tile as FREE (only works with odd tile size)",
    default=None,
)
@click.option(
    "--output",
    type=str,
    help="Output HTML file path (will be appended with _5x5 or _7x7 if tile-size is not specified)",
    default=None,
)
@click.option(
    "--no-down-scaling",
    is_flag=True,
    help="Disable automatic image scaling (celebration images > 50KB and background > 250KB will be scaled down by default)",
    default=False,
)
@click.option(
    "--background-color",
    type=str,
    help="Hex color for the background and tiles (e.g. #0a0a30)",
    default=None,
)
@click.option(
    "--no-interactive",
    is_flag=True,
    help="Skip interactive prompts and use specified arguments + defaults",
    default=False,
)
@click.option(
    "--theme",
    type=click.Choice(list_themes()),
    help="Theme to use for the bingo card (alien or ghost)",
    default="alien",
)
@click.option(
    "--update",
    is_flag=True,
    help="Update the bingo-card-generator package by pulling latest changes from git repository",
    default=False,
)
def main(
        csv_file: Optional[str],
        image_path: Optional[str],
        h_bingo_image_path: Optional[str],
        bingo_image_path: Optional[str],
        double_bingo_image_path: Optional[str],
        super_bingo_image_path: Optional[str],
        tile_size: Optional[int],
        free_center: Optional[bool],
        output: Optional[str],
        no_down_scaling: bool,
        background_color: Optional[str],
        no_interactive: bool,
        theme: str,
        update: bool,
):
    """Generate a bingo card HTML file from a CSV of tile values and a background image.

    Args:
        csv_file: Path to the CSV file with bingo tile values.
        image_path: Path to the background image to reveal on the board.
        h_bingo_image_path: Path to the image used for H-bingo celebration.
        bingo_image_path: Path to the image used for standard bingo celebration.
        double_bingo_image_path: Path to the image used for double bingo celebration.
        super_bingo_image_path: Path to the image used for super bingo celebration.
        tile_size: Number of rows and columns in the bingo grid.
        free_center: Whether to set the center tile as FREE.
        output: Output HTML file path.
        no_down_scaling: Whether to disable automatic image scaling.
        background_color: Hex color for the background and tiles.
        no_interactive: Whether to skip interactive prompts and use defaults.
        theme: Theme to use for the bingo card (alien or ghost).
        update: Whether to update the package by pulling latest changes from git repository.
    """
    # Handle update option first
    if update:
        console.print(Panel.fit(
            Text("🔄 UPDATING BINGO CARD GENERATOR", justify="center"),
            border_style="bright_blue"
        ))
        
        try:
            # Find the installation directory of the package
            import bingo_card_generator
            package_path = Path(bingo_card_generator.__file__).parent
        except ImportError:
            # Fallback: try to find the git repository in current directory or parents
            current_path = Path.cwd()
            package_path = None
            
            # Check current directory and parents for .git directory
            for path in [current_path] + list(current_path.parents):
                if (path / '.git').exists():
                    # Check if this looks like the bingo-app repository
                    if (path / 'create_bingo_card.py').exists() or (path / 'setup.py').exists():
                        package_path = path
                        break
            
            if package_path is None:
                console.print("[red]❌ Could not locate bingo-app git repository.[/]")
                console.print("[yellow]💡 Make sure you're running this from within the bingo-app directory or that the package is properly installed.[/]")
                return
        
        console.print(f"📁 Found repository at: {package_path}")
        
        # Check if it's a git repository
        git_dir = package_path / '.git'
        if not git_dir.exists():
            console.print("[red]❌ Directory is not a git repository.[/]")
            return
        
        # Run git pull
        try:
            console.print("🔄 Pulling latest changes...")
            result = subprocess.run(
                ['git', 'pull'],
                cwd=package_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            console.print("[green]✅ Successfully updated the repository![/]")
            if result.stdout.strip():
                console.print(f"Git output: {result.stdout.strip()}")
            
            # Reinstall the package to pick up any changes
            console.print("📦 Reinstalling package...")
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-e', '.'],
                cwd=package_path,
                check=True
            )
            console.print("[green]✅ Package reinstalled successfully![/]")
            
        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ Error updating repository: {e}[/]")
            if e.stdout:
                console.print(f"Output: {e.stdout}")
            if e.stderr:
                console.print(f"Error: {e.stderr}")
        except Exception as e:
            console.print(f"[red]❌ Unexpected error: {e}[/]")
        
        return
    
    # Get theme configuration
    theme_config = get_theme(theme)
    
    # Default values
    defaults = {
        "csv_file": "Bingo Tiles.csv",
        "image_path": "images/default_background.png",
        "h_bingo_image_path": "images/hexy_bald.png",
        "bingo_image_path": "images/rat_king.png",
        "double_bingo_image_path": "images/rat_king.png",
        "super_bingo_image_path": "images/god_gamer.png",
        "tile_size": 5,
        "free_center": False,
        "output": "bingo.html",
        "no_downscaling": no_down_scaling,
        # Use theme background color as default, but CLI argument will override this
        "background_color": background_color if background_color else theme_config["colors"]["background"],
    }
    
    # Print welcome banner with theme name
    console.print(Panel.fit(
        Text(f"🎮 BINGO CARD GENERATOR 🎲\n{theme_config['name']} Theme", justify="center"),
        border_style="bright_blue"
    ))

    # Collect inputs: either from command line or interactive prompts
    inputs = {}

    if no_interactive:
        # Use command line arguments + defaults for any missing values
        inputs = {
            "csv_file": csv_file or defaults["csv_file"],
            "image_path": image_path or defaults["image_path"],
            "h_bingo_image_path": h_bingo_image_path or defaults["h_bingo_image_path"],
            "bingo_image_path": bingo_image_path or defaults["bingo_image_path"],
            "double_bingo_image_path": double_bingo_image_path or defaults["double_bingo_image_path"],
            "super_bingo_image_path": super_bingo_image_path or defaults["super_bingo_image_path"],
            "tile_size": tile_size if tile_size is not None else defaults["tile_size"],
            "free_center": free_center if free_center is not None else defaults["free_center"],
            "output": output or defaults["output"],
            "no_downscaling": no_down_scaling,
            "background_color": background_color or defaults["background_color"],
        }
    else:
        # Fill in any provided command line arguments as defaults
        if csv_file:
            defaults["csv_file"] = csv_file
        if image_path:
            defaults["image_path"] = image_path
        if h_bingo_image_path:
            defaults["h_bingo_image_path"] = h_bingo_image_path
        if bingo_image_path:
            defaults["bingo_image_path"] = bingo_image_path
        if double_bingo_image_path:
            defaults["double_bingo_image_path"] = double_bingo_image_path
        if super_bingo_image_path:
            defaults["super_bingo_image_path"] = super_bingo_image_path
        if tile_size is not None:
            defaults["tile_size"] = tile_size
        if free_center is not None:
            defaults["free_center"] = free_center
        if output:
            defaults["output"] = output
        if background_color:
            defaults["background_color"] = background_color

        # Now prompt for any missing values
        inputs = prompt_for_input(defaults)

    try:
        # Validate the background color
        if not validate_hex_color(inputs["background_color"]):
            raise ValueError(f"Invalid hex color format: {inputs['background_color']}. Please use format like #0a0a30")

        # Convert paths
        csv_file_path = Path(inputs["csv_file"]).resolve()

        # Load bingo items (needed to check if we have enough for the requested tile sizes)
        console.print(f"[bold]Loading bingo values from[/] [cyan]{csv_file_path}[/]")
        all_bingo_items = load_bingo_data(csv_file_path)
        console.print(f"[bold]Loaded[/] [green]{len(all_bingo_items)}[/] [bold]unique bingo values[/]")

        # Determine which tile sizes to generate
        tile_sizes_to_generate = []
        if inputs["tile_size"] is None:
            # Generate both 5x5 and 7x7 cards
            tile_sizes_to_generate = [5, 7]
        else:
            # Generate just the specified size
            tile_sizes_to_generate = [inputs["tile_size"]]

        # Check if we have enough items for the largest requested size
        max_tile_size = max(tile_sizes_to_generate)
        if len(all_bingo_items) < max_tile_size ** 2:
            console.print(
                f"[bold red]Error:[/] Not enough unique items in the CSV file "
                f"for a {max_tile_size}x{max_tile_size} bingo grid. "
                f"Need at least {max_tile_size ** 2}, but only have {len(all_bingo_items)}."
            )
            return

        # Generate bingo cards
        generated_files = []
        for size in tile_sizes_to_generate:
            console.print(f"\n[bold]Generating {size}x{size} bingo card...[/]")
            bingo_file = generate_bingo_card(inputs, size, theme_config)
            generated_files.append(bingo_file)

        # Show summary
        show_summary(generated_files, all_bingo_items)

    except Exception as e:
        console.print(f"[bold red]❌ Error:[/] {e}")
        raise


if __name__ == "__main__":
    main()