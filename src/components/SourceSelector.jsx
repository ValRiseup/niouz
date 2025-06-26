import React, { useMemo } from 'react';
import './SourceSelector.css';
import CloseIcon from '../assets/icons/close.svg?react';

// A new sub-component for the custom checkbox for better structure and accessibility.
const CustomCheckbox = ({ id, name, checked, onChange, label, count }) => (
    <div className="source-item">
        <label htmlFor={id} className="source-checkbox-label">
            <input 
                id={id}
                name={name}
                type="checkbox" 
                className="custom-checkbox-native"
                checked={checked}
                onChange={onChange}
            />
            <span className="custom-checkbox">
                <svg viewBox="0 0 12 9" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M1 4.5L4.5 8L11 1" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
            </span>
            <span className="source-name">{label}</span>
        </label>
        <span className="article-count">{count} articles</span>
    </div>
);

const SourceSelector = ({
  groupedSources,
  selectedSources,
  setSelectedSources,
  onSoloSelect,
  onClose // New prop for closing the panel
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
        <h3>Filtrer les Sources</h3>
        <div className="selection-controls">
          <button className="control-button" onClick={handleSelectAll}>Tout Sélectionner</button>
          <button className="control-button" onClick={handleDeselectAll}>Tout Déselectionner</button>
        </div>
      </div>

      <button className="close-button" onClick={onClose} aria-label="Fermer le filtre">
        <CloseIcon />
      </button>

      {Object.entries(groupedSources).map(([category, sources]) => (
        <div key={category} className="source-category">
          <h4>{category}</h4>
          <div className="source-list">
            {sources.map(source => (
                <div key={source.name} className="source-item">
                    <label htmlFor={source.name} className="source-checkbox-label">
                        <input
                            type="checkbox"
                            id={source.name}
                            className="custom-checkbox-native"
                            checked={selectedSources[source.name] || false}
                            onChange={() =>
                                setSelectedSources(prev => ({ ...prev, [source.name]: !prev[source.name] }))
                            }
                        />
                        <span className="custom-checkbox">
                           <svg viewBox="0 0 12 9" fill="none"><path d="M1 4.5L4.5 8L11 1" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                        </span>
                        <span className="source-name">{source.name}</span>
                    </label>
                    <span className="article-count">{source.count} articles</span>
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