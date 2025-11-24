"""Image processing utilities for bingo card generation."""

import base64
from io import BytesIO
from pathlib import Path
from typing import Literal

from loguru import logger
from PIL import Image
from rich.console import Console

console = Console()

ImageType = Literal["background", "h_bingo", "celebration"]


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


def scale_image_to_target_size(
    img: Image.Image, target_size_kb: float = 250.0, format: str = "PNG"
) -> Image.Image:
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

    # Try up to 10 iterations to get close to target size
    for _ in range(10):
        scale = (min_scale + max_scale) / 2
        width, height = img.size
        new_width = int(width * scale)
        new_height = int(height * scale)

        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        size_kb = get_image_size_kb(resized_img, format)

        # Update best result if this one is closer to target
        if size_kb <= target_size_kb and size_kb > best_size_kb:
            best_img = resized_img
            best_size_kb = size_kb

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
        best_img = img.resize((new_width, new_height), Image.LANCZOS)

    return best_img


def create_square_image(img: Image.Image) -> Image.Image:
    """Create a square image by padding with transparency.

    Args:
        img: PIL Image object to make square.

    Returns:
        Square PIL Image object with transparent padding.
    """
    original_width, original_height = img.size
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

    return square_img


def process_image(
    image_path: Path,
    image_type: ImageType = "background",
    target_size_kb: float = 250.0,
    no_downscaling: bool = False,
) -> str:
    """Process an image and return its base64 encoding.

    This function:
    1. Loads the image
    2. Converts it to a square aspect ratio
    3. Optionally scales it down to meet size requirements
    4. Encodes it as base64 for embedding in HTML

    Args:
        image_path: Path to the image file.
        image_type: Type of image - determines size limits.
        target_size_kb: Target maximum size in KB (for background images).
        no_downscaling: If True, disable automatic scaling.

    Returns:
        Base64-encoded image string ready for embedding in HTML.

    Raises:
        FileNotFoundError: If the image file does not exist.
    """
    if not image_path.exists():
        logger.error(f"Image file not found: {image_path}")
        raise FileNotFoundError(f"Image file not found: {image_path}")

    # Set appropriate target size based on image type
    if image_type in ("h_bingo", "celebration"):
        actual_target_size_kb = 50.0
    else:
        actual_target_size_kb = target_size_kb

    # Load and make square
    img = Image.open(image_path)
    square_img = create_square_image(img)

    # Apply automatic scaling if needed and not disabled
    if not no_downscaling:
        current_size_kb = get_image_size_kb(square_img)
        if current_size_kb > actual_target_size_kb:
            square_img = scale_image_to_target_size(square_img, actual_target_size_kb)

    # Encode to base64
    buffer = BytesIO()
    square_img.save(buffer, format="PNG")
    buffer.seek(0)
    img_bytes = buffer.read()

    base64_encoded = base64.b64encode(img_bytes).decode("ascii")

    return base64_encoded


def process_all_images(config: dict, progress_task=None, progress_tracker=None) -> dict[str, str]:
    """Process all images for a bingo card.

    Args:
        config: Configuration dictionary with image paths.
        progress_task: Optional progress task ID for updating descriptions.
        progress_tracker: Optional Rich Progress instance.

    Returns:
        Dictionary mapping image types to their base64 encodings.
    """
    image_configs = [
        ("background", config["image_path"], "background"),
        ("h_bingo", config["h_bingo_image_path"], "h_bingo"),
        ("bingo", config["bingo_image_path"], "celebration"),
        ("double_bingo", config["double_bingo_image_path"], "celebration"),
        ("super_bingo", config["super_bingo_image_path"], "celebration"),
    ]

    images = {}
    for idx, (key, path, img_type) in enumerate(image_configs, 1):
        # Update progress description if available
        if progress_tracker and progress_task is not None:
            progress_tracker.update(
                progress_task,
                description=f"Processing images ({idx}/{len(image_configs)})"
            )

        images[key] = process_image(
            Path(path),
            image_type=img_type,
            no_downscaling=config.get("no_downscaling", False),
        )

    return images
