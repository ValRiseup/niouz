import React, { useState, useEffect } from 'react';
import RefreshButton from './RefreshButton';
import './Header.css';

const Header = ({
    viewMode, 
    onViewModeChange, 
    activeLanguage, 
    onLanguageChange,
    onFilterSourcesClick
}) => {
    const [isScrolled, setIsScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 10);
        };
        window.addEventListener('scroll', handleScroll, { passive: true });
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

  return (
    <header className={`header ${isScrolled ? 'scrolled' : ''}`}>
        <div className="header-left">
            <div className="logo">
              <h1>Les Actualités de l'IA</h1>
            </div>
            <div className="header-divider"></div>
            <div className="view-mode-selector" role="tablist" aria-label="Content type">
                <button role="tab" aria-selected={viewMode === 'articles'} className={`view-mode-button ${viewMode === 'articles' ? 'active' : ''}`} onClick={() => onViewModeChange('articles')}>Articles</button>
                <button role="tab" aria-selected={viewMode === 'topics'} className={`view-mode-button ${viewMode === 'topics' ? 'active' : ''}`} onClick={() => onViewModeChange('topics')}>Sujets</button>
            </div>
        </div>
        <div className="header-right">
            <div className="language-selector" role="tablist" aria-label="Language">
                <button role="tab" aria-selected={activeLanguage === 'all'} className={`language-button ${activeLanguage === 'all' ? 'active' : ''}`} onClick={() => onLanguageChange('all')}>Toutes</button>
                <button role="tab" aria-selected={activeLanguage === 'en'} className={`language-button ${activeLanguage === 'en' ? 'active' : ''}`} onClick={() => onLanguageChange('en')}>EN</button>
                <button role="tab" aria-selected={activeLanguage === 'fr'} className={`language-button ${activeLanguage === 'fr' ? 'active' : ''}`} onClick={() => onLanguageChange('fr')}>FR</button>
            </div>
            <button className="sources-toggle-button" onClick={onFilterSourcesClick}>
                Filtres
            </button>
            <RefreshButton />
        </div>
    </header>
  );
};

export default Header; 