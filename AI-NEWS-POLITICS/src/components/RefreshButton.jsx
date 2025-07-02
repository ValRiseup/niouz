import React from 'react';
import './RefreshButton.css';

const RefreshButton = ({ onRefresh, isRefreshing }) => {
  return (
    <button 
      className={`refresh-button ${isRefreshing ? 'refreshing' : ''}`}
      onClick={onRefresh}
      disabled={isRefreshing}
    >
      <span className="refresh-icon">
        {isRefreshing ? '🔄' : '🔄'}
      </span>
      <span className="refresh-text">
        {isRefreshing ? 'Actualisation...' : 'Actualiser'}
      </span>
    </button>
  );
};

export default RefreshButton; 