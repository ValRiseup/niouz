import React from 'react';
import './ProgressDisplay.css';

const ProgressDisplay = ({ progress, sourceName }) => {
  return (
    <div className="progress-display">
      <div className="progress-bar-container">
        <div 
          className="progress-bar" 
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <div className="progress-text">
        <span className="progress-percentage">{Math.round(progress)}%</span>
        <span className="progress-source">{sourceName}</span>
      </div>
    </div>
  );
};

export default ProgressDisplay; 