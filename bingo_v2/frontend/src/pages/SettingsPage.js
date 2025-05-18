import React, { useState, useEffect } from 'react';
import '../styles/Settings.css';

function SettingsPage() {
  const [settings, setSettings] = useState({
    grid_size: '5x5',
    free_center: true,
    theme: 'dark', // 'dark' or 'light'
    background_image: 'default_background', // Keep default images
    h_bingo_image: 'hexy_bald',
    celebration_image: 'rat_king'
  });
  
  const [images, setImages] = useState({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  // Load current settings
  useEffect(() => {
    loadSettings();
    loadAvailableImages();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await fetch('/api/settings');
      const data = await response.json();
      setSettings(data);
    } catch (err) {
      console.error('Error loading settings:', err);
    }
  };

  const loadAvailableImages = async () => {
    try {
      const response = await fetch('/api/images/list');
      const data = await response.json();
      setImages(data);
    } catch (err) {
      console.error('Error loading images:', err);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newSettings = {
      ...settings,
      [name]: type === 'checkbox' ? checked : value
    };
    setSettings(newSettings);
    
    // Apply theme change immediately
    if (name === 'theme') {
      document.documentElement.setAttribute('data-theme', value);
    }
  };

  const handleImageUpload = async (e, imageType) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('image', file);
    formData.append('type', imageType);

    setLoading(true);
    try {
      const response = await fetch('/api/images/process', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(`Image uploaded successfully: ${data.filename}`);
        loadAvailableImages();
        
        // Update settings with new image
        const imageKey = `${imageType}_image`;
        setSettings({
          ...settings,
          [imageKey]: data.filename.replace('.png', '').replace('.jpg', '')
        });
      } else {
        setMessage('Error uploading image');
      }
    } catch (err) {
      setMessage('Error uploading image');
      console.error('Upload error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch('/api/settings/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
      });
      
      // Clear saved bingo state when settings change
      sessionStorage.removeItem('bingoState');

      if (response.ok) {
        setMessage('Settings saved successfully!');
      } else {
        setMessage('Error saving settings');
      }
    } catch (err) {
      setMessage('Error saving settings');
      console.error('Save error:', err);
    }
  };

  const handleReset = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/settings/reset', {
        method: 'POST'
      });

      if (response.ok) {
        setMessage('Settings reset to defaults');
        loadSettings();
      }
    } catch (err) {
      console.error('Reset error:', err);
    }
  };

  return (
    <div className="settings-page" style={{ backgroundColor: settings.background_color }}>
      <h1>Settings</h1>

      {message && (
        <div className="message">
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit} className="settings-form">
        <div className="form-section">
          <h2>Game Settings</h2>
          
          <div className="form-group">
            <label htmlFor="grid_size">Card Size</label>
            <select
              id="grid_size"
              name="grid_size"
              value={settings.grid_size}
              onChange={handleChange}
            >
              <option value="3x3">3x3</option>
              <option value="5x5">5x5 (Standard)</option>
              <option value="7x7">7x7</option>
            </select>
          </div>

          <div className="form-group checkbox">
            <input
              type="checkbox"
              id="free_center"
              name="free_center"
              checked={settings.free_center}
              onChange={handleChange}
            />
            <label htmlFor="free_center">Free Center Tile (odd grids only)</label>
          </div>
        </div>

        <div className="form-section">
          <h2>Appearance</h2>
          
          <div className="form-group">
            <label>Theme</label>
            <div className="theme-selector">
              <label className="theme-option">
                <input
                  type="radio"
                  name="theme"
                  value="dark"
                  checked={settings.theme === 'dark'}
                  onChange={handleChange}
                />
                <span>🌙 Dark Mode</span>
              </label>
              <label className="theme-option">
                <input
                  type="radio"
                  name="theme"
                  value="light"
                  checked={settings.theme === 'light'}
                  onChange={handleChange}
                />
                <span>☀️ Light Mode</span>
              </label>
            </div>
          </div>
        </div>


        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            Save Settings
          </button>
          <button type="button" className="btn btn-secondary" onClick={handleReset}>
            Reset to Defaults
          </button>
        </div>
      </form>
    </div>
  );
}

export default SettingsPage;