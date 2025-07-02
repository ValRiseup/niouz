import React from 'react';
import './ProgressDisplay.css';

const ProgressDisplay = ({ progress, message = 'Chargement...' }) => {
  return (
    <div className="progress-display">
      <div className="progress-container">
        <div className="progress-message">
          <span className="progress-icon">🤖</span>
          <p>{message}</p>
        </div>
        
        <div className="progress-bar-container">
          <div 
            className="progress-bar"
            style={{ width: `${progress}%` }}
          />
        </div>
        
        <div className="progress-percentage">
          {Math.round(progress)}%
        </div>
      </div>
    </div>
  );
};

export default ProgressDisplay; 