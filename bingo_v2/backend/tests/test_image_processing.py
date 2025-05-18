import unittest
import os
import base64
from PIL import Image
from io import BytesIO
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, create_image_encoding_from_path, scale_image_to_target_size, get_image_size_kb


class TestImageProcessing(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.test_image_path = os.path.join(os.path.dirname(__file__), '..', '..', 'images', 'default_background.png')
        
    def test_get_image_size_kb(self):
        """Test that image size calculation works correctly"""
        # Create a test image
        img = Image.new('RGB', (100, 100), color='red')
        size_kb = get_image_size_kb(img)
        self.assertGreater(size_kb, 0)
        self.assertLess(size_kb, 10)  # A 100x100 red image should be small
    
    def test_scale_image_to_target_size(self):
        """Test image scaling to target size"""
        # Create a large test image with complex pattern to increase file size
        img = Image.new('RGB', (2000, 2000), color='blue')
        # Add some variation to increase file size
        pixels = img.load()
        for i in range(0, 2000, 10):
            for j in range(0, 2000, 10):
                pixels[i, j] = (i % 256, j % 256, (i + j) % 256)
        
        original_size = get_image_size_kb(img)
        
        # Scale it down to 50KB
        scaled_img = scale_image_to_target_size(img, target_size_kb=50.0)
        scaled_size = get_image_size_kb(scaled_img)
        
        self.assertLessEqual(scaled_size, 50.0)
        self.assertLess(scaled_size, original_size)
    
    def test_create_image_encoding_from_path(self):
        """Test image encoding from file path"""
        if not os.path.exists(self.test_image_path):
            self.skipTest(f"Test image not found at {self.test_image_path}")
            
        encoding = create_image_encoding_from_path(self.test_image_path)
        self.assertIsNotNone(encoding)
        
        # Verify it's valid base64
        try:
            decoded = base64.b64decode(encoding)
            img = Image.open(BytesIO(decoded))
            self.assertIsNotNone(img)
        except Exception as e:
            self.fail(f"Failed to decode base64 image: {e}")
    
    def test_image_api_endpoints(self):
        """Test image API endpoints"""
        # Test background image endpoint
        response = self.app.get('/api/images/background?name=default')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('image', data)
        
        # Test h_bingo image endpoint
        response = self.app.get('/api/images/h_bingo?name=default')
        self.assertEqual(response.status_code, 200)
        
        # Test celebration image endpoint
        response = self.app.get('/api/images/celebration?name=default')
        self.assertEqual(response.status_code, 200)
        
        # Test invalid image type
        response = self.app.get('/api/images/invalid')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()