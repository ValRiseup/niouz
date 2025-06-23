import React, { useState, useMemo } from 'react';
import './SourceSelector.css';
import EyeIcon from '../assets/icons/eye.svg?react';

const SourceSelector = ({ groupedSources, selectedSources, setSelectedSources, onSoloSelect, activeLanguage }) => {
  const categories = Object.keys(groupedSources);
  const [activeTab, setActiveTab] = useState(categories[0]);

  const filteredSources = useMemo(() => {
    if (!groupedSources[activeTab]) return [];
    return groupedSources[activeTab].filter(source => 
      (activeLanguage === 'all' || source.lang === activeLanguage) && source.count > 0
    );
  }, [activeTab, activeLanguage, groupedSources]);

  const allVisibleSelected = useMemo(() => {
    return filteredSources.every(s => selectedSources[s.name]);
  }, [filteredSources, selectedSources]);
  
  const handleSelectAll = () => {
    const allVisibleSources = filteredSources.map(s => s.name);
    
    const newSelectedSources = { ...selectedSources };
    allVisibleSources.forEach(source => {
      newSelectedSources[source] = !allVisibleSelected;
    });
    setSelectedSources(newSelectedSources);
  };

  const handleToggle = (source) => {
    setSelectedSources(prev => ({ ...prev, [source]: !prev[source] }));
  };

  const handleSoloClick = (e, source) => {
    e.stopPropagation();
    onSoloSelect(source);
  };

  return (
    <div className="source-selector-container">
      <div className="source-tabs">
        {categories.map(category => (
          <button
            key={category}
            className={`tab-button ${activeTab === category ? 'active' : ''}`}
            onClick={() => setActiveTab(category)}
          >
            {category}
          </button>
        ))}
      </div>
      <div className="source-list-header">
        <button className="select-all-button" onClick={handleSelectAll}>
          {allVisibleSelected ? 'Deselect All' : 'Select All'}
        </button>
      </div>
      <div className="source-list">
        {filteredSources.map(source => (
          <div key={source.name} className="source-item">
            <label className="source-checkbox">
              <input
                type="checkbox"
                checked={selectedSources[source.name] || false}
                onChange={() => handleToggle(source.name)}
              />
              <span className="checkmark"></span>
            </label>
            <div className="quality-dot-container">
                <span className={`quality-dot quality-${source.quality}`}></span>
                <span className="tooltip-text">Quality: {source.quality}/5</span>
            </div>
            <span className="source-name">{source.name}</span>
            <span className="article-count">({source.count})</span>
            <button className="solo-button" onClick={(e) => handleSoloClick(e, source.name)}>
              <EyeIcon />
              <span>Solo</span>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SourceSelector; 