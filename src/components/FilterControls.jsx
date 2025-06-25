import React, { useState } from 'react';
import SourceSelector from './SourceSelector';
import './FilterControls.css';

import listIcon from '../assets/icons/list.svg';
import calendarIcon from '../assets/icons/calendar.svg';
import trendingIcon from '../assets/icons/trending.svg';
import globeIcon from '../assets/icons/globe.svg';

const categories = [
    { key: 'all', icon: listIcon, title: 'Toutes les Actus' },
    { key: 'daily', icon: calendarIcon, title: 'Actus du Jour' },
    { key: 'trending', icon: trendingIcon, title: 'Tendances' },
    { key: 'global', icon: globeIcon, title: 'Couverture Globale' },
];

const FilterControls = ({
  activeCategory,
  onCategoryClick,
  groupedSources,
  selectedSources,
  setSelectedSources,
  onSoloSelect,
  activeLanguage,
  onLanguageChange,
}) => {
  const [showSourceSelector, setShowSourceSelector] = useState(false);

  return (
    <div className="filter-controls-container">
      <div className="filter-controls">
        <div className="categories-container">
          {categories.map((category) => (
            <button
              key={category.key}
              className={`category-button ${activeCategory === category.key ? 'active' : ''}`}
              onClick={() => onCategoryClick(category.key)}
            >
              <img src={category.icon} alt={`${category.title} icon`} className="category-icon" />
              <span>{category.title}</span>
            </button>
          ))}
        </div>
        <div className="right-controls">
          <div className="language-selector">
            <button className={`language-button ${activeLanguage === 'all' ? 'active' : ''}`} onClick={() => onLanguageChange('all')}>All</button>
            <button className={`language-button ${activeLanguage === 'en' ? 'active' : ''}`} onClick={() => onLanguageChange('en')}>EN</button>
            <button className={`language-button ${activeLanguage === 'fr' ? 'active' : ''}`} onClick={() => onLanguageChange('fr')}>FR</button>
          </div>
          <button className="sources-toggle-button" onClick={() => setShowSourceSelector(!showSourceSelector)}>
            {showSourceSelector ? 'Hide Sources' : 'Filter Sources'}
          </button>
        </div>
      </div>
      {showSourceSelector && (
        <div className="source-selector-wrapper">
          <SourceSelector
            groupedSources={groupedSources}
            selectedSources={selectedSources}
            setSelectedSources={setSelectedSources}
            onSoloSelect={onSoloSelect}
            activeLanguage={activeLanguage}
          />
        </div>
      )}
    </div>
  );
};

export default FilterControls; 