import React, { useEffect, useState, Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './styles/App.css';
import './styles/themes.css';
import Header from './components/Header';
import Footer from './components/Footer';

// Lazy load pages for better performance
const HomePage = lazy(() => import('./pages/HomePage'));
const BingoCardPage = lazy(() => import('./pages/BingoCardPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));

function App() {
  const [theme, setTheme] = useState('dark');
  
  // Load theme from settings
  useEffect(() => {
    const loadTheme = async () => {
      try {
        const response = await fetch('/api/settings');
        const data = await response.json();
        if (data.theme) {
          setTheme(data.theme);
          document.documentElement.setAttribute('data-theme', data.theme);
        }
      } catch (err) {
        console.error('Error loading theme:', err);
      }
    };
    
    loadTheme();
  }, []);
  
  return (
    <Router>
      <div className="app">
        <Header />
        <main className="main-content">
          <Suspense fallback={
            <div className="loading-container">
              <div className="loading-spinner">🛸</div>
              <p>Loading...</p>
            </div>
          }>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/play" element={<BingoCardPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </Suspense>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;