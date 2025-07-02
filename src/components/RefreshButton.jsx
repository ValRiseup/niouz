import React, { useState, useRef, useEffect } from 'react';
import RefreshIcon from '../assets/icons/refresh.svg?react';
import DotsIcon from '../assets/icons/dots.svg?react';
import './RefreshButton.css';

const RefreshButton = ({ onRefreshData }) => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleRefresh = (mode = 'normal') => {
    if (isRefreshing) return;
    
    setIsRefreshing(true);
    setShowDropdown(false);
    
    // Build URL with appropriate parameters
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001';
    let url = `${apiUrl}/refresh-data`;
    if (mode === 'all') {
      url += '?mode=all';
    } else if (mode === 'reset') {
      url += '?mode=reset';
    }
    
    const eventSource = new EventSource(url);

    eventSource.onmessage = (event) => {
      const data = event.data;
      if (data === 'DONE') {
        // Refresh completed successfully
        setTimeout(() => {
          if (onRefreshData) {
            onRefreshData();
          }
          setIsRefreshing(false);
        }, 500);
        eventSource.close();
      } else if (data.startsWith('ERROR:')) {
        // Handle errors
        console.error('Refresh error:', data.substring(6));
        eventSource.close();
        setTimeout(() => {
          setIsRefreshing(false);
        }, 1000);
      }
    };

    eventSource.onerror = () => {
      console.error('Error connecting to refresh service');
      eventSource.close();
      setTimeout(() => {
        setIsRefreshing(false);
      }, 1000);
    };
  };

  const handleNormalRefresh = () => handleRefresh('normal');
  const handleFullRefresh = () => handleRefresh('all');
  const handleResetRefresh = () => handleRefresh('reset');
  
  const toggleDropdown = () => setShowDropdown(!showDropdown);

  return (
    <div className="refresh-container">
      <button 
        className={`feed-action-button icon-only ${isRefreshing ? 'refreshing' : ''}`}
        onClick={handleNormalRefresh} 
        disabled={isRefreshing}
        aria-label="Actualiser le fil d'actualités"
        title={isRefreshing ? "Actualisation en cours..." : "Actualiser les articles"}
      >
        <RefreshIcon />
      </button>
      
      <div className="refresh-dropdown" ref={dropdownRef}>
        <button 
          className={`feed-action-button icon-only dropdown-toggle ${showDropdown ? 'active' : ''}`}
          onClick={toggleDropdown} 
          disabled={isRefreshing}
          aria-label="Options d'actualisation"
        >
          <DotsIcon />
        </button>
        
        {showDropdown && (
          <div className="dropdown-menu">
            <button 
              className="dropdown-item" 
              onClick={handleNormalRefresh}
              disabled={isRefreshing}
            >
              <RefreshIcon />
              <div>
                <span>Nouveaux articles</span>
                <small>Articles récents uniquement</small>
              </div>
            </button>
            
            <button 
              className="dropdown-item" 
              onClick={handleFullRefresh}
              disabled={isRefreshing}
            >
              <RefreshIcon />
              <div>
                <span>Tous les articles</span>
                <small>Récupération complète</small>
              </div>
            </button>
            
            <button 
              className="dropdown-item reset" 
              onClick={handleResetRefresh}
              disabled={isRefreshing}
            >
              <RefreshIcon />
              <div>
                <span>Réinitialiser</span>
                <small>Reset timestamp + actualisation</small>
              </div>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default RefreshButton; 