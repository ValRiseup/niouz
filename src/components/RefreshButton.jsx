import React, { useState } from 'react';
import ProgressDisplay from './ProgressDisplay';
import './RefreshButton.css';

const RefreshButton = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [sourceName, setSourceName] = useState('');

  const handleRefresh = () => {
    setIsRefreshing(true);
    setProgress(0);
    setSourceName('Initializing...');
    
    const eventSource = new EventSource('http://127.0.0.1:5001/refresh-data');

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
          window.location.reload();
        }, 1500);
        eventSource.close();
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

  return (
    <div className="refresh-container">
      <button 
        className="refresh-button" 
        onClick={handleRefresh} 
        disabled={isRefreshing}
      >
        {isRefreshing ? 'Refreshing...' : 'Refresh Feed'}
      </button>
      {isRefreshing && <ProgressDisplay progress={progress} sourceName={sourceName} />}
    </div>
  );
};

export default RefreshButton; 