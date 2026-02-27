"""Flask web server for the bingo card generator.

Provides a web interface to generate bingo cards while maintaining
compatibility with the existing CLI tool.
"""

import os
from pathlib import Path
from typing import Any

from flask import Flask, render_template_string, request, jsonify
from werkzeug.exceptions import BadRequest, NotFound

from create_bingo_card import (
    load_bingo_data,
    get_random_bingo_items,
    generate_bingo_html_card,
    resolve_path,
    validate_hex_color,
)
from image_processor import process_all_images
from themes import get_theme, list_themes

app = Flask(__name__)

# Configure Flask app
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Get the directory where this app.py file is located
APP_DIR = Path(__file__).parent.resolve()

def get_default_config() -> dict[str, Any]:
    """Get default configuration for bingo card generation.
    
    Returns:
        Default configuration dictionary with paths resolved relative to app directory.
    """
    return {
        "csv_file": str(APP_DIR / "Bingo Tiles.csv"),
        "image_path": str(APP_DIR / "images" / "default_background.png"),
        "h_bingo_image_path": str(APP_DIR / "images" / "hexy_bald.png"),
        "bingo_image_path": str(APP_DIR / "images" / "rat_king.png"),
        "double_bingo_image_path": str(APP_DIR / "images" / "rat_king.png"),
        "super_bingo_image_path": str(APP_DIR / "images" / "god_gamer.png"),
        "tile_size": 5,
        "free_center": False,
        "output": "bingo.html",
        "no_downscaling": False,
        "background_color": "#1e2328",
    }


def validate_request_params(theme: str, size: str) -> tuple[str, int]:
    """Validate and sanitize request parameters.
    
    Args:
        theme: Theme name from URL
        size: Grid size from URL (should be like "5x5")
        
    Returns:
        Tuple of (validated_theme, validated_size)
        
    Raises:
        BadRequest: If parameters are invalid
    """
    # Validate theme
    available_themes = list_themes()
    if theme not in available_themes:
        raise BadRequest(f"Invalid theme '{theme}'. Available themes: {', '.join(available_themes)}")
    
    # Validate size format (e.g., "5x5")
    if 'x' not in size:
        raise BadRequest(f"Invalid size format '{size}'. Expected format like '5x5'")
    
    try:
        width_str, height_str = size.split('x')
        width, height = int(width_str), int(height_str)
        
        if width != height:
            raise BadRequest(f"Grid must be square. Got {width}x{height}")
        
        if width < 3 or width > 10:
            raise BadRequest(f"Grid size must be between 3x3 and 10x10. Got {width}x{height}")
            
        return theme, width
        
    except ValueError:
        raise BadRequest(f"Invalid size format '{size}'. Expected format like '5x5'")


@app.route('/')
def index():
    """Landing page with theme and size selection."""
    themes = list_themes()
    theme_configs = {theme: get_theme(theme) for theme in themes}
    
    landing_page_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bingo Card Generator</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #1e2328, #2d3748);
            color: #e2fcff;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            width: 100%;
            text-align: center;
            background: rgba(45, 55, 72, 0.8);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
        }
        
        h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #7303c0, #18f2b2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            font-size: 1.2rem;
            margin-bottom: 40px;
            opacity: 0.8;
        }
        
        .form-group {
            margin-bottom: 30px;
            text-align: left;
        }
        
        label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        select {
            width: 100%;
            padding: 15px;
            font-size: 1rem;
            border: 2px solid #4a5568;
            border-radius: 10px;
            background: #2d3748;
            color: #e2fcff;
            cursor: pointer;
        }
        
        select:focus {
            outline: none;
            border-color: #7303c0;
            box-shadow: 0 0 10px rgba(115, 3, 192, 0.3);
        }
        
        .theme-preview {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .theme-card {
            padding: 20px;
            border-radius: 10px;
            border: 2px solid transparent;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .theme-card:hover {
            transform: translateY(-5px);
            border-color: currentColor;
        }
        
        .generate-btn {
            background: linear-gradient(45deg, #7303c0, #b5179e);
            color: white;
            border: none;
            padding: 20px 40px;
            font-size: 1.2rem;
            font-weight: bold;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 20px;
        }
        
        .generate-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(115, 3, 192, 0.4);
        }
        
        .size-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .size-option {
            padding: 15px;
            border: 2px solid #4a5568;
            border-radius: 10px;
            background: #2d3748;
            color: #e2fcff;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
        }
        
        .size-option:hover {
            border-color: #7303c0;
            background: rgba(115, 3, 192, 0.1);
            color: #e2fcff;
            text-decoration: none;
        }
        
        @media (max-width: 600px) {
            h1 { font-size: 2rem; }
            .container { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Bingo Card Generator 🎲</h1>
        <p class="subtitle">Create interactive bingo cards with custom themes and sizes</p>
        
        <form id="bingoForm">
            <div class="form-group">
                <label for="theme">Choose a Theme:</label>
                <select id="theme" name="theme">
                    {% for theme_id, theme_config in themes.items() %}
                    <option value="{{ theme_id }}">{{ theme_config.name }}</option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="form-group">
                <label>Choose Grid Size:</label>
                <div class="size-grid">
                    <div class="size-option" onclick="selectSize('3x3')">
                        <strong>3×3</strong><br>
                        <small>Quick Game</small>
                    </div>
                    <div class="size-option" onclick="selectSize('5x5')">
                        <strong>5×5</strong><br>
                        <small>Classic</small>
                    </div>
                    <div class="size-option" onclick="selectSize('7x7')">
                        <strong>7×7</strong><br>
                        <small>Challenge</small>
                    </div>
                </div>
            </div>
        </form>
        
        <div style="margin-top: 40px; opacity: 0.7;">
            <p><strong>Available Themes:</strong></p>
            <div style="margin-top: 15px; text-align: left;">
                {% for theme_id, theme_config in themes.items() %}
                <div style="margin: 10px 0;">
                    <strong>{{ theme_config.name }}</strong>: 
                    {{ theme_config.emojis.decorations[0] if theme_config.emojis.decorations else '🎮' }}
                    {% if theme_id == 'alien' %}Space/alien themed with neon effects{% endif %}
                    {% if theme_id == 'ghost' %}Spooky ghost hunt with eerie vibes{% endif %}
                    {% if theme_id == 'thanksgiving' %}Warm autumn feast celebration{% endif %}
                    {% if theme_id == 'christmas' %}Festive holiday wonderland{% endif %}
                    {% if theme_id == 'new_year' %}Sparkling celebration theme{% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <script>
        function selectSize(size) {
            const theme = document.getElementById('theme').value;
            const url = `/bingo/${theme}/${size}`;
            window.open(url, '_blank');
        }
        
        // Add keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.key === '3') selectSize('3x3');
            if (e.key === '5') selectSize('5x5');
            if (e.key === '7') selectSize('7x7');
        });
        
        // Theme preview hover effects
        document.getElementById('theme').addEventListener('change', function() {
            console.log('Selected theme:', this.value);
        });
    </script>
</body>
</html>
    """
    
    return render_template_string(landing_page_template, themes=theme_configs)


@app.route('/bingo/<theme>/<size>')
def generate_bingo(theme: str, size: str):
    """Generate and serve an interactive bingo card."""
    try:
        # Validate parameters
        validated_theme, grid_size = validate_request_params(theme, size)
        
        # Get theme configuration
        theme_config = get_theme(validated_theme)
        
        # Set up configuration
        config = get_default_config()
        config["tile_size"] = grid_size
        config["free_center"] = grid_size % 2 == 1  # Free center for odd sizes
        config["background_color"] = theme_config["colors"]["background"]
        
        # Validate that default files exist
        csv_file_path = resolve_path(config["csv_file"])
        if not csv_file_path.exists():
            raise NotFound(f"Bingo data file not found: {csv_file_path}")
        
        # Load bingo data
        all_bingo_items = load_bingo_data(csv_file_path)
        
        # Check if we have enough items for the requested size
        required_items = grid_size ** 2
        if len(all_bingo_items) < required_items:
            raise BadRequest(
                f"Not enough bingo items for {grid_size}x{grid_size} grid. "
                f"Need at least {required_items}, but only have {len(all_bingo_items)}."
            )
        
        # Generate random grid
        initial_items = get_random_bingo_items(
            all_bingo_items, 
            free_center=config["free_center"], 
            tile_size=grid_size
        )
        
        # Process images
        try:
            images = process_all_images(config)
        except FileNotFoundError as e:
            # If default images don't exist, create a minimal config
            app.logger.warning(f"Image not found: {e}. Using fallback.")
            images = {
                "background": "",
                "h_bingo": "",
                "bingo": "",
                "double_bingo": "",
                "super_bingo": "",
            }
        
        # Load template (resolve relative to this app.py file)
        template_path = APP_DIR / "bingo.jinja"
        if not template_path.exists():
            raise NotFound(f"Template file not found: {template_path}")
        
        with template_path.open(encoding="utf-8") as f:
            template_content = f.read()
        
        # Build template data
        template_data = {
            "initial_items": initial_items,
            "all_bingo_items": [item.replace('"', '\\"') for item in all_bingo_items],  # Escape quotes
            "image": images["background"],
            "h_bingo_image": images["h_bingo"],
            "bingo_image": images["bingo"],
            "double_bingo_image": images["double_bingo"],
            "super_bingo_image": images["super_bingo"],
            "N_options": len(all_bingo_items),
            "background_color": config["background_color"],
            "theme": theme_config,
        }
        
        # Render template
        from jinja2 import Template
        template = Template(template_content)
        html_content = template.render(template_data)
        
        return html_content
        
    except (BadRequest, NotFound):
        # Re-raise HTTP errors
        raise
    except Exception as e:
        app.logger.error(f"Error generating bingo card: {e}")
        return f"Error generating bingo card: {str(e)}", 500


@app.route('/api/themes')
def api_themes():
    """API endpoint to get available themes."""
    themes = list_themes()
    theme_data = {}
    
    for theme_name in themes:
        config = get_theme(theme_name)
        theme_data[theme_name] = {
            "name": config["name"],
            "colors": config["colors"],
            "emojis": config["emojis"]
        }
    
    return jsonify(theme_data)


@app.route('/health')
def health_check():
    """Health check endpoint for deployment monitoring."""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "themes": len(list_themes())
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with a friendly message."""
    return f"""
    <h1>Page Not Found</h1>
    <p>The page you're looking for doesn't exist.</p>
    <p><a href="/">← Back to Bingo Generator</a></p>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
        h1 {{ color: #7303c0; }}
        a {{ color: #b5179e; }}
    </style>
    """, 404


@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors with helpful information."""
    return f"""
    <h1>Bad Request</h1>
    <p>{error.description}</p>
    <p><a href="/">← Back to Bingo Generator</a></p>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
        h1 {{ color: #dc2626; }}
        a {{ color: #b5179e; }}
    </style>
    """, 400


if __name__ == '__main__':
    # Development server settings
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"Starting Bingo Card Generator Web Server...")
    print(f"Available themes: {', '.join(list_themes())}")
    print(f"Server running at http://{host}:{port}")
    
    app.run(host=host, port=port, debug=debug_mode)