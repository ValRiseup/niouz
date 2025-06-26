import React, { useMemo } from 'react';
import './SourceSelector.css';

const SourceSelector = ({
  groupedSources,
  selectedSources,
  setSelectedSources,
  onSoloSelect,
  activeLanguage
}) => {
  const allSources = useMemo(() => Object.values(groupedSources).flat().map(s => s.name), [groupedSources]);

  const handleSelectAll = () => {
    setSelectedSources(allSources.reduce((acc, source) => {
      acc[source] = true;
      return acc;
    }, {}));
  };

  const handleDeselectAll = () => {
    setSelectedSources(allSources.reduce((acc, source) => {
      acc[source] = false;
      return acc;
    }, {}));
  };

  const handleSoloClick = (e, source) => {
    e.stopPropagation();
    onSoloSelect(source);
  };

  return (
    <div className="source-selector-container">
      <div className="source-selector-header">
        <h3>Filter Sources</h3>
        <div className="selection-controls">
          <button onClick={handleSelectAll}>Select All</button>
          <button onClick={handleDeselectAll}>Deselect All</button>
        </div>
      </div>

      {Object.entries(groupedSources).map(([category, sources]) => (
        <div key={category} className="source-category">
          <h4>{category}</h4>
          <div className="source-list">
            {sources.map(source => (
              <div key={source.name} className="source-item">
                <input
                  type="checkbox"
                  id={source.name}
                  checked={selectedSources[source.name] || false}
                  onChange={() =>
                    setSelectedSources(prev => ({ ...prev, [source.name]: !prev[source.name] }))
                  }
                />
                <label htmlFor={source.name}>
                  <span className="source-name">{source.name}</span>
                  <span className="article-count">{source.count} articles</span>
                </label>
                <button onClick={() => onSoloSelect(source.name)} className="solo-button">
                  Solo
                </button>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default SourceSelector; 