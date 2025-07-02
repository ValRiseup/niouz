import React from 'react';
import './SourceSelector.css';

const SourceSelector = ({ 
  availableSources, 
  selectedSources, 
  onSourcesChange, 
  selectedLanguage, 
  onLanguageChange 
}) => {
  const handleSourceToggle = (source) => {
    const newSelected = selectedSources.includes(source)
      ? selectedSources.filter(s => s !== source)
      : [...selectedSources, source];
    onSourcesChange(newSelected);
  };

  const handleSelectAll = () => {
    onSourcesChange(availableSources);
  };

  const handleSelectNone = () => {
    onSourcesChange([]);
  };

  const handleSelectFrench = () => {
    const frenchSources = availableSources.filter(source => 
      isFrenchSource(source)
    );
    onSourcesChange(frenchSources);
  };

  // Identification des sources françaises prioritaires
  const isFrenchSource = (source) => {
    const frenchSources = [
      'Le Figaro Politique', 'Le Monde Politique', 'Libération Politique', 
      'L\'Express Politique', 'Le Point Politique', 'Marianne', 'Mediapart',
      'L\'Obs Politique', 'France Inter Politique', 'Public Sénat', 
      'LCP Assemblée', 'La Croix Politique', 'France 24 Politique',
      'BFM Politique', 'LCI Politique', 'CNews Politique', 'L\'Opinion',
      'Assemblée Nationale', 'Sénat', 'Vie Publique', 'Service Public',
      'Conseil Constitutionnel', 'Ouest France Politique', 'Sud Ouest Politique',
      'La Dépêche Politique', 'Nice Matin Politique', 'Le Progrès Politique',
      'Euronews Politique', 'RFI Politique', 'TV5 Monde Info', 'Atlantico',
      'Causeur', 'Contrepoints', 'Slate France', 'Valeurs Actuelles',
      'L\'Humanité', 'Regards', 'IFOP', 'OpinionWay', 'BVA Opinion',
      'Ipsos France', 'CSA Research', 'CheckNews Libération',
      'Les Décodeurs Le Monde', 'AFP Factuel'
    ];
    return frenchSources.includes(source);
  };

  const isPrioritySource = (source) => {
    const prioritySources = [
      'Le Monde Politique', 'Le Figaro Politique', 'Mediapart',
      'France Inter Politique', 'Public Sénat', 'Assemblée Nationale',
      'Sénat', 'Libération Politique'
    ];
    return prioritySources.includes(source);
  };

  // Séparation des sources françaises et internationales
  const frenchSources = availableSources.filter(isFrenchSource);
  const internationalSources = availableSources.filter(source => !isFrenchSource(source));

  return (
    <div className="source-selector">
      <div className="selector-header">
        <h3 className="selector-title">🎯 Filtres & Sources</h3>
        <div className="selector-controls">
          <button className="control-btn french-btn" onClick={handleSelectFrench}>
            🇫🇷 Sources FR
          </button>
          <button className="control-btn" onClick={handleSelectAll}>
            Tout sélectionner
          </button>
          <button className="control-btn" onClick={handleSelectNone}>
            Tout désélectionner
          </button>
        </div>
      </div>

      <div className="selector-section">
        <h4 className="section-title">🌐 Langue</h4>
        <div className="language-options">
          <label className="language-option">
            <input
              type="radio"
              name="language"
              value="all"
              checked={selectedLanguage === 'all'}
              onChange={(e) => onLanguageChange(e.target.value)}
            />
            <span className="option-label">
              🌍 Toutes les langues
            </span>
          </label>
          <label className="language-option">
            <input
              type="radio"
              name="language"
              value="fr"
              checked={selectedLanguage === 'fr'}
              onChange={(e) => onLanguageChange(e.target.value)}
            />
            <span className="option-label">
              🇫🇷 Français
            </span>
          </label>
          <label className="language-option">
            <input
              type="radio"
              name="language"
              value="en"
              checked={selectedLanguage === 'en'}
              onChange={(e) => onLanguageChange(e.target.value)}
            />
            <span className="option-label">
              🇬🇧 Anglais
            </span>
          </label>
        </div>
      </div>

      {/* Section Sources Françaises */}
      <div className="selector-section french-priority">
        <h4 className="section-title">
          🇫🇷 Médias Français ({frenchSources.filter(s => selectedSources.includes(s)).length}/{frenchSources.length})
        </h4>
        <div className="sources-grid">
          {frenchSources.map((source) => (
            <label key={source} className="source-option french-source">
              <input
                type="checkbox"
                checked={selectedSources.includes(source)}
                onChange={() => handleSourceToggle(source)}
              />
              <span className="source-label">{source}</span>
              {isPrioritySource(source) && (
                <span className="source-priority-badge">Premium</span>
              )}
            </label>
          ))}
        </div>
      </div>

      {/* Section Sources Internationales */}
      {internationalSources.length > 0 && (
        <div className="selector-section">
          <h4 className="section-title">
            🌍 Médias Internationaux ({internationalSources.filter(s => selectedSources.includes(s)).length}/{internationalSources.length})
          </h4>
          <div className="sources-grid">
            {internationalSources.map((source) => (
              <label key={source} className="source-option">
                <input
                  type="checkbox"
                  checked={selectedSources.includes(source)}
                  onChange={() => handleSourceToggle(source)}
                />
                <span className="source-label">{source}</span>
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SourceSelector; 