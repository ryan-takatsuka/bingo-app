import React from 'react';
import { Link } from 'react-router-dom';

function HomePage() {
  return (
    <div className="home-page">
      <h1>Welcome to Bingo App V2</h1>
      <p>A modern web-based bingo application</p>

      <div className="action-buttons">
        <Link to="/play" className="btn btn-primary">
          Play Bingo
        </Link>
        <Link to="/settings" className="btn btn-secondary">
          Settings
        </Link>
      </div>

      <div className="features">
        <h2>Features</h2>
        <ul>
          <li>Randomized bingo cards</li>
          <li>Interactive gameplay</li>
          <li>Customizable settings</li>
          <li>Save and load your progress</li>
        </ul>
      </div>
    </div>
  );
}

export default HomePage;