from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from werkzeug.utils import secure_filename
import random
import base64
from PIL import Image
from io import BytesIO
import csv

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images')
app.config['DATA_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload and data directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_image_size_kb(img, format="PNG"):
    """Get the size of an image in kilobytes."""
    buffer = BytesIO()
    img.save(buffer, format=format)
    size_bytes = len(buffer.getvalue())
    return size_bytes / 1024

def scale_image_to_target_size(img, target_size_kb=250.0, format="PNG"):
    """Scale an image down to meet a target file size in KB."""
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

def create_image_encoding_from_path(image_path, target_size_kb=250.0, no_downscaling=False, image_type="background"):
    """Convert an image to a base64 encoded string for embedding in HTML."""
    if not os.path.exists(image_path):
        return None

    # Set appropriate target size based on image type
    if image_type == "h_bingo" or image_type == "celebration":
        # Use 50KB limit for celebration images
        actual_target_size_kb = 50.0
    else:
        # Use default (250KB) for background image
        actual_target_size_kb = target_size_kb

    # Read image from path
    img = Image.open(image_path)

    # Create a square canvas with padding to preserve aspect ratio
    original_width, original_height = img.size
    max_dimension = max(original_width, original_height)
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

    # Save new image to local buffer
    buffer = BytesIO()
    square_img.save(buffer, format="PNG")
    buffer.seek(0)
    img_bytes = buffer.read()

    # Encode image with base64 and return string
    base64_encoded_result_bytes = base64.b64encode(img_bytes)
    return base64_encoded_result_bytes.decode("ascii")

def load_bingo_data(csv_file_path):
    """Load bingo tile values from a CSV file."""
    if not os.path.exists(csv_file_path):
        return []

    with open(csv_file_path, 'r') as f:
        # Read lines, strip whitespace, and filter out empty lines
        lines = [line.strip() for line in f.readlines()]
        return list(set([line for line in lines if line]))

def get_random_bingo_items(items, free_center=False, tile_size=5):
    """Generate a randomized 2D grid of bingo items."""
    # For odd-sized grids with free center, we need one less item
    required_items = tile_size ** 2
    if free_center and tile_size % 2 == 1:
        required_items -= 1
    
    # Check that there are enough items
    if len(items) < required_items:
        return None

    # Get randomized list of items
    randomized_items = random.sample(items, required_items)

    # Create the bingo data to fill the grid
    bingo_data = []
    item_number = 0
    
    for row in range(tile_size):
        row_data = []
        for col in range(tile_size):
            # Check if this is the center tile and free_center is enabled
            if free_center and tile_size % 2 == 1:
                center_index = tile_size // 2
                if row == center_index and col == center_index:
                    row_data.append("FREE")
                    continue
            
            row_data.append(randomized_items[item_number])
            item_number += 1
        bingo_data.append(row_data)

    return bingo_data

@app.route('/api/bingo-tiles', methods=['GET'])
def get_bingo_tiles():
    """Get all available bingo tiles from the CSV file."""
    csv_file = request.args.get('csv_file', 'bingo_tiles.csv')
    csv_path = os.path.join(app.config['DATA_FOLDER'], secure_filename(csv_file))

    # Use default if file doesn't exist
    if not os.path.exists(csv_path):
        csv_path = os.path.join(app.config['DATA_FOLDER'], 'bingo_tiles.csv')

    tiles = load_bingo_data(csv_path)
    return jsonify(tiles)

@app.route('/api/bingo-card', methods=['GET'])
def get_bingo_card():
    """Generate a randomized bingo card."""
    # Get parameters from request
    csv_file = request.args.get('csv_file', 'bingo_tiles.csv')
    tile_size = int(request.args.get('tile_size', 5))
    free_center = request.args.get('free_center', 'false').lower() == 'true'

    # Load bingo tiles
    csv_path = os.path.join(app.config['DATA_FOLDER'], secure_filename(csv_file))

    # Use default if file doesn't exist
    if not os.path.exists(csv_path):
        csv_path = os.path.join(app.config['DATA_FOLDER'], 'bingo_tiles.csv')

    tiles = load_bingo_data(csv_path)

    # Generate random bingo card
    bingo_card = get_random_bingo_items(tiles, free_center, tile_size)

    if bingo_card is None:
        return jsonify({
            'error': f'Not enough unique items in the CSV file for the bingo size {tile_size}x{tile_size}.'
        }), 400

    return jsonify({
        'card': bingo_card,
        'all_tiles': tiles
    })

@app.route('/api/images/<image_type>', methods=['GET'])
def get_image(image_type):
    """Get a base64 encoded image for the bingo card."""
    image_name = request.args.get('name', 'default')
    no_downscaling = request.args.get('no_downscaling', 'false').lower() == 'true'

    # Determine image path based on type
    if image_type == 'background':
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{secure_filename(image_name)}.png")
        if not os.path.exists(image_path):
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'default_background.png')
    elif image_type == 'h_bingo':
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{secure_filename(image_name)}.png")
        if not os.path.exists(image_path):
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'hexy_bald.png')
    elif image_type == 'celebration':
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{secure_filename(image_name)}.png")
        if not os.path.exists(image_path):
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'rat_king.png')
    else:
        return jsonify({'error': 'Invalid image type'}), 400

    # Create base64 encoding of the image
    image_encoding = create_image_encoding_from_path(
        image_path,
        no_downscaling=no_downscaling,
        image_type=image_type
    )

    if image_encoding is None:
        return jsonify({'error': 'Image not found'}), 404

    return jsonify({'image': image_encoding})

@app.route('/api/images/process', methods=['POST'])
def process_image():
    """Process and optimize an uploaded image"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
        
    file = request.files['image']
    image_type = request.form.get('type', 'background')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_' + filename)
        file.save(temp_path)
        
        # Process the image
        try:
            img = Image.open(temp_path)
            
            # Determine target size based on image type
            target_size_kb = 50.0 if image_type in ['h_bingo', 'celebration'] else 250.0
            
            # Scale image if needed
            if get_image_size_kb(img) > target_size_kb:
                img = scale_image_to_target_size(img, target_size_kb)
            
            # Save processed image
            final_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            img.save(final_path, 'PNG')
            
            # Clean up temp file
            os.remove(temp_path)
            
            # Return base64 encoding
            encoding = create_image_encoding_from_path(final_path)
            
            return jsonify({
                'filename': filename,
                'image': encoding,
                'size_kb': get_image_size_kb(img)
            })
            
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/images/optimize', methods=['POST'])
def optimize_image():
    """Optimize an existing image file"""
    data = request.get_json()
    filename = data.get('filename')
    image_type = data.get('type', 'background')
    
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
        
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
        
    try:
        img = Image.open(file_path)
        original_size = get_image_size_kb(img)
        
        # Determine target size
        target_size_kb = 50.0 if image_type in ['h_bingo', 'celebration'] else 250.0
        
        # Optimize if needed
        if original_size > target_size_kb:
            img = scale_image_to_target_size(img, target_size_kb)
            img.save(file_path, 'PNG')
            
        return jsonify({
            'filename': filename,
            'original_size_kb': original_size,
            'optimized_size_kb': get_image_size_kb(img),
            'image': create_image_encoding_from_path(file_path)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/images/list', methods=['GET'])
def list_images():
    """List all available images"""
    try:
        images = {
            'background': [],
            'h_bingo': [],
            'celebration': []
        }
        
        # Default images
        default_mappings = {
            'default_background.png': 'background',
            'hexy_bald.png': 'h_bingo',
            'rat_king.png': 'celebration',
            'hexydobby.jpg': 'celebration'
        }
        
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if allowed_file(filename):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Categorize image
                category = default_mappings.get(filename, 'background')
                
                # Get file info
                img = Image.open(file_path)
                images[category].append({
                    'filename': filename,
                    'size_kb': get_image_size_kb(img),
                    'dimensions': f"{img.width}x{img.height}"
                })
                img.close()
        
        return jsonify(images)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Settings management
settings_store = {}

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings"""
    default_settings = {
        'grid_size': '5x5',
        'free_center': True,
        'background_color': '#0a0a30',
        'background_image': 'default_background.png',
        'h_bingo_image': 'hexy_bald.png',
        'celebration_image': 'rat_king.png'
    }
    return jsonify({**default_settings, **settings_store})

@app.route('/api/settings/save', methods=['POST'])
def save_settings():
    """Save settings"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate settings
    valid_grid_sizes = ['3x3', '5x5', '7x7']
    if 'grid_size' in data and data['grid_size'] not in valid_grid_sizes:
        return jsonify({'error': 'Invalid grid size'}), 400
    
    # Update settings
    settings_store.update(data)
    
    return jsonify({
        'message': 'Settings saved',
        'settings': {**settings_store}
    })

@app.route('/api/settings/reset', methods=['POST'])
def reset_settings():
    """Reset settings to defaults"""
    settings_store.clear()
    return jsonify({'message': 'Settings reset to defaults'})

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """Upload an image for use in the bingo card."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    image_type = request.form.get('type', 'background')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Create base64 encoding of the image
        image_encoding = create_image_encoding_from_path(
            file_path,
            no_downscaling=False,
            image_type=image_type
        )

        return jsonify({
            'success': True,
            'filename': filename,
            'image': image_encoding
        })

    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/upload-csv', methods=['POST'])
def upload_csv():
    """Upload a CSV file with bingo tile values."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['DATA_FOLDER'], filename)
        file.save(file_path)

        # Load and validate the CSV
        tiles = load_bingo_data(file_path)

        return jsonify({
            'success': True,
            'filename': filename,
            'tile_count': len(tiles)
        })

    return jsonify({'error': 'File must be a CSV'}), 400

@app.route('/api/available-files', methods=['GET'])
def get_available_files():
    """Get lists of available image and CSV files."""
    # Get all image files
    image_files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if allowed_file(filename):
            image_files.append(filename)

    # Get all CSV files
    csv_files = []
    for filename in os.listdir(app.config['DATA_FOLDER']):
        if filename.endswith('.csv'):
            csv_files.append(filename)

    return jsonify({
        'images': image_files,
        'csv_files': csv_files
    })

# Serve the React app in production
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join('..', 'frontend', 'build', path)):
        return send_from_directory(os.path.join('..', 'frontend', 'build'), path)
    return send_from_directory(os.path.join('..', 'frontend', 'build'), 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)