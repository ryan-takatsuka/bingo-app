import unittest
import os
import json
import base64
from io import BytesIO
from PIL import Image
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app


class TestAPIEndpoints(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
    def test_process_image_endpoint(self):
        """Test the image processing endpoint"""
        # Create a test image
        img = Image.new('RGB', (100, 100), color='red')
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # Send to API
        response = self.app.post('/api/images/process',
                                data={'type': 'background', 'image': (img_io, 'test.png')},
                                content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('filename', data)
        self.assertIn('image', data)
        self.assertIn('size_kb', data)
    
    def test_optimize_image_endpoint(self):
        """Test the image optimization endpoint"""
        # First upload an image
        img = Image.new('RGB', (1000, 1000), color='green')
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], 'test_optimize.png')
        img.save(img_path)
        
        # Optimize it
        response = self.app.post('/api/images/optimize',
                                json={'filename': 'test_optimize.png', 'type': 'background'})
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('original_size_kb', data)
        self.assertIn('optimized_size_kb', data)
        
        # Clean up
        if os.path.exists(img_path):
            os.remove(img_path)
    
    def test_list_images_endpoint(self):
        """Test the list images endpoint"""
        response = self.app.get('/api/images/list')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('background', data)
        self.assertIn('h_bingo', data)
        self.assertIn('celebration', data)
    
    def test_settings_endpoints(self):
        """Test settings management endpoints"""
        # Save settings
        test_settings = {
            'grid_size': '7x7',
            'free_center': True,
            'background_color': '#0a0a30'
        }
        
        response = self.app.post('/api/settings/save',
                                json=test_settings)
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('message', data)
        self.assertIn('settings', data)
        
        # Get settings
        response = self.app.get('/api/settings')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['grid_size'], '7x7')
        
        # Reset settings
        response = self.app.post('/api/settings/reset')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()