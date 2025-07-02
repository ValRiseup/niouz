import React, { useState, useEffect } from 'react';
import './Header.css';

const Header = ({ 
  searchTerm, 
  onSearchChange, 
  viewMode, 
  onViewModeChange, 
  totalItems, 
  filteredCount 
}) => {
  const [currentPlatform, setCurrentPlatform] = useState('politics');

  // Detect current platform based on port
  useEffect(() => {
    const port = window.location.port;
    if (port === '5178' || port === '5179') {
      setCurrentPlatform('politics');
    } else {
      setCurrentPlatform('ai');
    }
  }, []);

  const categories = [
    {
      id: 'ai',
      name: 'Intelligence Artificielle',
      icon: '🤖',
      description: 'IA, ML, Tech',
      url: 'http://localhost:5177',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    {
      id: 'politics',
      name: 'Politique',
      icon: '🏛️',
      description: 'France & International',
      url: 'http://localhost:5178',
      gradient: 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)'
    }
  ];

  const currentCategory = categories.find(cat => cat.id === currentPlatform) || categories[1];

  const handleCategoryChange = (category) => {
    if (category.url && category.id !== currentPlatform) {
      window.location.href = category.url;
    }
  };

  return (
    <header className="header">
      <div className="header-container">
        <div className="header-top">
          <div className="header-left">
            <div className="category-selector">
              <div className="current-category" style={{ background: currentCategory.gradient }}>
                <span className="category-icon">{currentCategory.icon}</span>
                <div className="category-info">
                  <span className="category-name">{currentCategory.name}</span>
                  <span className="category-desc">{currentCategory.description}</span>
                </div>
                <span className="dropdown-arrow">▼</span>
              </div>
              
              <div className="category-dropdown">
                {categories.map((category) => (
                  <div
                    key={category.id}
                    className={`category-option ${category.id === currentPlatform ? 'active' : ''}`}
                    onClick={() => handleCategoryChange(category)}
                    style={{ background: category.gradient }}
                  >
                    <span className="option-icon">{category.icon}</span>
                    <div className="option-info">
                      <span className="option-name">{category.name}</span>
                      <span className="option-desc">{category.description}</span>
                    </div>
                    {category.id === currentPlatform && <span className="active-indicator">✓</span>}
                  </div>
                ))}
              </div>
            </div>
            
            <div className="title-section">
              <h1 className="header-title">
                Les Actualités {currentCategory.name === 'Intelligence Artificielle' ? 'IA' : 'Politiques'}
              </h1>
              <p className="header-subtitle">
                Analyse intelligente par IA • {currentCategory.description}
              </p>
            </div>
          </div>
          
          <div className="header-right">
            <div className="search-container">
              <input
                type="text"
                placeholder={`Rechercher ${currentCategory.name === 'Intelligence Artificielle' ? 'OpenAI, GPT, IA...' : 'politicien, parti, sujet...'}`}
                value={searchTerm}
                onChange={(e) => onSearchChange(e.target.value)}
                className="search-input"
              />
              <span className="search-icon">🔍</span>
            </div>
          </div>
        </div>

        <div className="header-bottom">
          <div className="view-mode-selector">
            <button
              className={`view-mode-btn ${viewMode === 'topics' ? 'active' : ''}`}
              onClick={() => onViewModeChange('topics')}
            >
              <span className="btn-icon">📚</span>
              Sujets {currentCategory.name === 'Intelligence Artificielle' ? 'IA' : 'Politiques'}
            </button>
            <button
              className={`view-mode-btn ${viewMode === 'articles' ? 'active' : ''}`}
              onClick={() => onViewModeChange('articles')}
            >
              <span className="btn-icon">📰</span>
              Articles
            </button>
          </div>

          <div className="header-stats">
            <span className="stats-item">
              {filteredCount} / {totalItems} {viewMode === 'topics' ? 'sujets' : 'articles'}
            </span>
            <span className="platform-badge">
              {currentCategory.icon} {currentCategory.name}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header; 