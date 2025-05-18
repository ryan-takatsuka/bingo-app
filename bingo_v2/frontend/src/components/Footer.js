import React from 'react';
import '../styles/Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <p>&copy; {new Date().getFullYear()} Bingo App V2</p>
        <div className="footer-links">
          <a href="https://www.twitch.tv" target="_blank" rel="noopener noreferrer">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M11.571 4.714h1.715v5.143H11.57zm4.715 0H18v5.143h-1.714zM6 0L1.714 4.286v15.428h5.143V24l4.286-4.286h3.428L22.286 12V0zm14.571 11.143l-3.428 3.428h-3.429l-3 3v-3H6.857V1.714h13.714Z"/>
            </svg>
            <span>Twitch</span>
          </a>
          <span className="separator">•</span>
          <a href="#" onClick={(e) => {
            e.preventDefault();
            alert('About: Bingo App V2 is a refactored version of the original Bingo App, now with a modern interface and engaging features.');
          }}>About</a>
          <span className="separator">•</span>
          <a href="#" onClick={(e) => {
            e.preventDefault();
            alert('Contact us at support@bingoapp.example.com');
          }}>Contact</a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;