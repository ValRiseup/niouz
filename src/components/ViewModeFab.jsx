import React from 'react';
import './ViewModeFab.css';

const ViewModeFab = ({ viewMode, onViewModeChange }) => {
  const toggleMode = () => {
    onViewModeChange(viewMode === 'articles' ? 'topics' : 'articles');
  };

  return (
    <button
      className="view-fab-btn"
      onClick={toggleMode}
      aria-label={`Passer en mode ${viewMode === 'articles' ? 'Sujets' : 'Articles'}`}
      title={viewMode === 'articles' ? 'Voir les sujets' : 'Voir les articles'}
    >
      {viewMode === 'articles' ? '📰' : '📚'}
    </button>
  );
};

export default ViewModeFab; 