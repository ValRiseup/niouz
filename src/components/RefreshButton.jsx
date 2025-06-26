import React, { useState, useRef, useEffect } from 'react';
import ProgressDisplay from './ProgressDisplay';
import RefreshIcon from '../assets/icons/refresh.svg?react';
import DotsIcon from '../assets/icons/dots.svg?react';
import './RefreshButton.css';

const RefreshButton = ({ onRefreshData }) => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [sourceName, setSourceName] = useState('');
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
    setIsRefreshing(true);
    setProgress(0);
    setShowDropdown(false);
    
    // Set initial message based on mode
    const modeMessages = {
      normal: 'Actualisation des nouveaux articles...',
      all: 'Récupération de TOUS les articles...',
      reset: 'Réinitialisation et actualisation...'
    };
    setSourceName(modeMessages[mode] || 'Initializing...');
    
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
      if (data.startsWith('PROGRESS:')) {
        const [, progressValue, name] = data.split(':');
        setProgress(parseFloat(progressValue));
        setSourceName(name);
      } else if (data === 'DONE') {
        setProgress(100);
        setSourceName('Feed refreshed successfully!');
        setTimeout(() => {
          if (onRefreshData) {
            onRefreshData();
          }
          setIsRefreshing(false);
          setSourceName('');
          setProgress(0);
        }, 1500);
        eventSource.close();
      } else if (data.startsWith('ERROR:FATAL: GEMINI_API_KEY')) {
        setSourceName(data.substring(12));
        eventSource.close();
        setTimeout(() => setIsRefreshing(false), 10000);
      } else if (data.startsWith('ERROR:')) {
        setSourceName(`Error: ${data.substring(6)}`);
        eventSource.close();
        setTimeout(() => {
          setIsRefreshing(false);
          setSourceName('');
          setProgress(0);
        }, 3000);
      }
    };

    eventSource.onerror = () => {
      setSourceName('Error connecting to the server.');
      eventSource.close();
      setTimeout(() => {
        setIsRefreshing(false);
        setSourceName('');
        setProgress(0);
      }, 3000);
    };
  };

  const handleNormalRefresh = () => handleRefresh('normal');
  const handleFullRefresh = () => handleRefresh('all');
  const handleResetRefresh = () => handleRefresh('reset');
  
  const toggleDropdown = () => setShowDropdown(!showDropdown);

  return (
    <div className="refresh-container">
      <div className="refresh-button-group">
        <button 
          className={`feed-action-button icon-only refresh-main ${isRefreshing ? 'refreshing' : ''}`}
          onClick={handleNormalRefresh} 
          disabled={isRefreshing}
          aria-label="Actualiser le fil d'actualités"
        >
          <RefreshIcon />
        </button>
        
        <div className="refresh-dropdown" ref={dropdownRef}>
          <button 
            className={`feed-action-button icon-only refresh-menu ${showDropdown ? 'active' : ''}`}
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
                <div>
                  <RefreshIcon />
                  <div>
                    <span>Nouveaux articles</span>
                    <small>Articles récents uniquement</small>
                  </div>
                </div>
              </button>
              
              <button 
                className="dropdown-item" 
                onClick={handleFullRefresh}
                disabled={isRefreshing}
              >
                <div>
                  <RefreshIcon />
                  <div>
                    <span>Tous les articles</span>
                    <small>Récupération complète</small>
                  </div>
                </div>
              </button>
              
              <button 
                className="dropdown-item reset" 
                onClick={handleResetRefresh}
                disabled={isRefreshing}
              >
                <div>
                  <RefreshIcon />
                  <div>
                    <span>Réinitialiser</span>
                    <small>Reset timestamp + actualisation</small>
                  </div>
                </div>
              </button>
            </div>
          )}
        </div>
      </div>
      
      {isRefreshing && <ProgressDisplay progress={progress} sourceName={sourceName} />}
    </div>
  );
};

export default RefreshButton; 