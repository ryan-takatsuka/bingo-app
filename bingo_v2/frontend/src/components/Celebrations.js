import React, { useEffect, useState } from 'react';
import '../styles/Celebrations.css';

// Single Bingo Celebration
export const SingleBingoCelebration = ({ onComplete }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onComplete && onComplete();
    }, 3000);
    
    return () => clearTimeout(timer);
  }, [onComplete]);
  
  return (
    <div className="bingo-celebration single-bingo">
      <div className="bingo-message">BINGO!</div>
    </div>
  );
};

// Double Bingo Celebration
export const DoubleBingoCelebration = ({ onComplete, celebrationImage }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      onComplete && onComplete();
    }, 5000);
    
    return () => clearTimeout(timer);
  }, [onComplete]);
  
  return (
    <div className="bingo-celebration double-bingo">
      <div className="bingo-message">DOUBLE BINGO!</div>
      <div className="cosmic-background"></div>
      
      {celebrationImage && (
        <div className="celebration-image-wrapper">
          <img 
            src={`data:image/png;base64,${celebrationImage}`}
            alt="Celebration"
            className={`celebration-image ${imageLoaded ? 'loaded' : ''}`}
            onLoad={() => setImageLoaded(true)}
          />
        </div>
      )}
    </div>
  );
};

// H-Bingo Celebration
export const HBingoCelebration = ({ onComplete, hBingoImage }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      onComplete && onComplete();
    }, 5000);
    
    return () => clearTimeout(timer);
  }, [onComplete]);
  
  return (
    <div className="h-bingo-celebration">
      <div className="h-bingo-message">H-BINGO!</div>
      <div className="h-background"></div>
      
      {hBingoImage && (
        <div className="h-bingo-container">
          <div className="h-image-wrapper">
            <img 
              src={`data:image/png;base64,${hBingoImage}`}
              alt="H-Bingo"
              className={`h-image ${imageLoaded ? 'loaded' : ''}`}
              onLoad={() => setImageLoaded(true)}
            />
          </div>
        </div>
      )}
    </div>
  );
};

// Super Bingo Celebration (Complete Board)
export const SuperBingoCelebration = ({ onComplete, celebrationImage }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      onComplete && onComplete();
    }, 6000);
    
    return () => clearTimeout(timer);
  }, [onComplete]);
  
  return (
    <div className="bingo-celebration complete-celebration">
      <div className="bingo-message">SUPER BINGO!</div>
      <div className="cosmic-vortex"></div>
      
      {celebrationImage && (
        <div className="mothership-container">
          <img 
            src={`data:image/png;base64,${celebrationImage}`}
            alt="Mothership"
            className={`mothership ${imageLoaded ? 'loaded' : ''}`}
            onLoad={() => setImageLoaded(true)}
          />
          <div className="mothership-beam"></div>
        </div>
      )}
    </div>
  );
};

// Main Celebration Manager
const Celebrations = ({ celebrationType, onComplete, images }) => {
  if (!celebrationType) return null;
  
  switch (celebrationType) {
    case 'single':
      return <SingleBingoCelebration onComplete={onComplete} />;
    case 'double':
      return <DoubleBingoCelebration onComplete={onComplete} celebrationImage={images?.celebration} />;
    case 'h-pattern':
      return <HBingoCelebration onComplete={onComplete} hBingoImage={images?.hBingo} />;
    case 'complete':
      return <SuperBingoCelebration onComplete={onComplete} celebrationImage={images?.celebration} />;
    default:
      return null;
  }
};

export default Celebrations;