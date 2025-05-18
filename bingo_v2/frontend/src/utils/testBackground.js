// Test if we can fetch the background image
async function testBackgroundImage() {
  try {
    const response = await fetch('/api/images/background?name=default_background');
    console.log('Response status:', response.status);
    console.log('Response headers:', response.headers);
    
    const data = await response.json();
    console.log('Image data exists:', !!data.image);
    console.log('Image data length:', data.image ? data.image.length : 0);
    
    if (data.image) {
      // Try to create an image element
      const img = new Image();
      img.src = `data:image/png;base64,${data.image}`;
      img.onload = () => console.log('Image loaded successfully');
      img.onerror = (err) => console.error('Image failed to load:', err);
    }
  } catch (err) {
    console.error('Error fetching background image:', err);
  }
}

// Run the test
testBackgroundImage();