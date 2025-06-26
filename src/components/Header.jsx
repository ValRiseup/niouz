import React, { useState, useEffect } from 'react';
import './Header.css';

// Import flag and globe icons
import globeIcon from '../assets/icons/globe.svg';
import flagGB from '../assets/icons/flag-gb.svg';
import flagFR from '../assets/icons/flag-fr.svg';
import logo from '/logo.svg';

const LanguageSwitcher = ({ activeLanguage, onLanguageChange }) => {
    return (
        <div className="language-selector" role="tablist" aria-label="Language">
            <button role="tab" aria-selected={activeLanguage === 'all'} className={`language-button ${activeLanguage === 'all' ? 'active' : ''}`} onClick={() => onLanguageChange('all')}>
                <img src={globeIcon} alt="All languages" />
            </button>
            <button role="tab" aria-selected={activeLanguage === 'en'} className={`language-button ${activeLanguage === 'en' ? 'active' : ''}`} onClick={() => onLanguageChange('en')}>
                <img src={flagGB} alt="English" />
            </button>
            <button role="tab" aria-selected={activeLanguage === 'fr'} className={`language-button ${activeLanguage === 'fr' ? 'active' : ''}`} onClick={() => onLanguageChange('fr')}>
                <img src={flagFR} alt="Français" />
            </button>
        </div>
    );
};

const Header = ({
    viewMode, 
    onViewModeChange, 
    activeLanguage, 
    onLanguageChange,
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
              <img src={logo} alt="Les Actualités de l'IA" />
            </div>
            <div className="header-divider"></div>
            <div className="view-mode-selector" role="tablist" aria-label="Content type">
                <button role="tab" aria-selected={viewMode === 'articles'} className={`view-mode-button ${viewMode === 'articles' ? 'active' : ''}`} onClick={() => onViewModeChange('articles')}>Articles</button>
                <button role="tab" aria-selected={viewMode === 'topics'} className={`view-mode-button ${viewMode === 'topics' ? 'active' : ''}`} onClick={() => onViewModeChange('topics')}>Sujets</button>
            </div>
        </div>
        <div className="header-right">
            <LanguageSwitcher activeLanguage={activeLanguage} onLanguageChange={onLanguageChange} />
        </div>
    </header>
  );
};

export default Header; 