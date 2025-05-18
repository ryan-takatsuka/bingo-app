import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import '../styles/Header.css';

const Header = () => {
  const location = useLocation();

  // Function to check if the link is active
  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <header className="header">
      <div className="header-content">
        <h1 className="logo">
          <Link to="/">Bingo App V2</Link>
        </h1>
        <nav className="nav">
          <ul>
            <li>
              <Link to="/" className={isActive('/')}>Home</Link>
            </li>
            <li>
              <Link to="/play" className={isActive('/play')}>Play</Link>
            </li>
            <li>
              <Link to="/settings" className={isActive('/settings')}>Settings</Link>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;