from pathlib import Path
from jinja2 import Template
import io
from typing import List, Optional
import click
import numpy as np
import random
import base64
from PIL import Image
from io import BytesIO


def load_bingo_data(csv_file_path: Path) -> List[str]:
    """Load bingo tile values from a CSV file."""
    if not csv_file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")

    with csv_file_path.open() as f:
        # Read lines, strip whitespace, and filter out empty lines
        lines = [line.strip() for line in f.readlines()]
        return list(set([line for line in lines if line]))


def escape_quotes(items: List[str]) -> List[str]:
    """Add escape character to quotes in strings so they are added properly to the HTML."""
    return [item.replace('"', '\\"') for item in items]


def create_image_encoding_from_path(image_path: Path, resolution_scale: float = 1, tile_size: int = 5) -> str:
    """
    Convert an image to a base64 encoded string for embedding in HTML.
    Adjusts the image to match the aspect ratio of the bingo grid (square)
    so the entire image fits within the grid of tiles.
    """
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

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

    # Now apply the resolution scaling to the square image
    scaled_size = int(max_dimension * resolution_scale)
    square_img = square_img.resize(
        (scaled_size, scaled_size), Image.LANCZOS if hasattr(Image, "LANCZOS") else Image.ANTIALIAS
    )

    # Save new resized image to local buffer
    buffer = BytesIO()
    square_img.save(buffer, format="PNG")
    buffer.seek(0)
    img_bytes = buffer.read()

    # Encode image with base64 and return string
    base64_encoded_result_bytes = base64.b64encode(img_bytes)
    return base64_encoded_result_bytes.decode("ascii")


def load_jinja_template(template_path: Optional[Path] = None) -> Template:
    """Load the bingo Jinja template file."""
    if template_path is None:
        template_path = Path("bingo.jinja").resolve()

    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    # Load the jinja template
    with io.open(template_path, "r", encoding="utf-8") as f:
        return Template(f.read())


def get_random_bingo_items(items: List[str], free_center: bool = False, tile_size: int = 5) -> List[List[str]]:
    """Generate a randomized 2D grid of bingo items."""
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
    """Validate that a string is a proper hex color code."""
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
        celebration_image_encoding: str,
        output_file: Path,
        background_color: str = "#f5f9ff",
) -> Path:
    """Generate the HTML bingo card file using the Jinja template."""
    # Load jinja template and populate with bingo data
    template = load_jinja_template()
    html_str = template.render(
        {
            "initial_items": initial_items,
            "all_bingo_items": escape_quotes(all_bingo_items),
            "image": image_encoding,
            "h_bingo_image": h_bingo_image_encoding,
            "celebration_image": celebration_image_encoding,
            "N_options": len(all_bingo_items),
            "background_color": background_color,
        }
    )

    # Write output html file
    with output_file.open(mode="w", encoding="utf-8") as f:
        f.write(html_str)
    return output_file


@click.command()
@click.option(
    "--csv-file",
    type=click.Path(exists=True),
    help="Path to the CSV file with bingo tile values",
    default="Bingo Tiles.csv",
)
@click.option(
    "--image-path",
    type=click.Path(exists=True),
    help="Path to the background image to reveal on the board",
    default="images/default_background.png",
)
@click.option(
    "--h-bingo-image-path",
    type=click.Path(exists=True),
    help="Path to the image used for H-bingo celebration",
    default="images/hexy_bald.png",
)
@click.option(
    "--celebration-image-path",
    type=click.Path(exists=True),
    help="Path to the image used for double and super bingo celebrations",
    default="images/rat_king.png",
)
@click.option("--tile-size", type=int, help="Number of rows and columns in the bingo grid", default=5)
@click.option(
    "--free-center",
    is_flag=True,
    help="Set center tile as FREE (only works with odd tile size)",
    default=False,
)
@click.option(
    "--output",
    type=str,
    help="Output HTML file path",
    default="bingo.html",
)
@click.option(
    "--image-resolution",
    type=float,
    help="Scale factor for the background image (< 1 to downsize)",
    default=1.0,
)
@click.option(
    "--background-color",
    type=str,
    help="Hex color for the background and tiles (e.g. #0a0a30)",
    default="#0a0a30",
)
def main(
        csv_file: str,
        image_path: str,
        h_bingo_image_path: str,
        celebration_image_path: str,
        tile_size: int,
        free_center: bool,
        output: str,
        image_resolution: float,
        background_color: str,
):
    """Generate a bingo card HTML file from a CSV of tile values and a background image."""
    try:
        # Validate the background color
        if not validate_hex_color(background_color):
            raise ValueError(f"Invalid hex color format: {background_color}. Please use format like #0a0a30")

        # Convert paths
        csv_file_path = Path(csv_file).resolve()
        image_file_path = Path(image_path).resolve()
        h_bingo_image_file_path = Path(h_bingo_image_path).resolve()
        celebration_image_file_path = Path(celebration_image_path).resolve()
        output_file_path = Path(output).resolve()

        # Load data and generate bingo card
        print(f"Loading bingo values from {csv_file_path}")
        all_bingo_items = load_bingo_data(csv_file_path)
        print(f"Loaded {len(all_bingo_items)} unique bingo values")

        print(f"Generating random {tile_size}x{tile_size} bingo grid")
        initial_items = get_random_bingo_items(all_bingo_items, free_center=free_center, tile_size=tile_size)

        print(f"Loading and encoding image from {image_file_path} (fitting to {tile_size}x{tile_size} grid)")
        image_encoding = create_image_encoding_from_path(
            image_file_path, resolution_scale=image_resolution, tile_size=tile_size
        )

        print(f"Loading and encoding H-bingo celebration image from {h_bingo_image_file_path}")
        h_bingo_image_encoding = create_image_encoding_from_path(
            h_bingo_image_file_path, resolution_scale=1.0
        )

        print(f"Loading and encoding celebration image from {celebration_image_file_path}")
        celebration_image_encoding = create_image_encoding_from_path(
            celebration_image_file_path, resolution_scale=1.0
        )

        print(f"Generating HTML bingo card with dark theme and background color: {background_color}")
        bingo_file = generate_bingo_html_card(
            initial_items=initial_items,
            all_bingo_items=all_bingo_items,
            image_encoding=image_encoding,
            h_bingo_image_encoding=h_bingo_image_encoding,
            celebration_image_encoding=celebration_image_encoding,
            output_file=output_file_path,
            background_color=background_color,
        )

        print(f"✅ Successfully generated a {tile_size}x{tile_size} bingo card: {bingo_file}")
        print(f"Open the file in a web browser to play!")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()