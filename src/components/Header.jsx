import React, { useState, useEffect } from 'react';
import './Header.css';
import RefreshButton from './RefreshButton';
import FilterIcon from '../assets/icons/filter.svg?react';

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
    onFilterSourcesClick,
    onRefreshData,
    globalSearchTerm,
    setGlobalSearchTerm,
}) => {
    const [isScrolled, setIsScrolled] = useState(false);
    const [currentPlatform, setCurrentPlatform] = useState('ai');

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
            name: 'IA',
            fullName: 'Intelligence Artificielle',
            icon: '🤖',
            description: 'IA, ML, Tech',
            url: 'http://localhost:5177',
            gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        },
        {
            id: 'politics',
            name: 'Politique',
            fullName: 'Politique',
            icon: '🏛️',
            description: 'France & International',
            url: 'http://localhost:5178',
            gradient: 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)'
        }
    ];

    const currentCategory = categories.find(cat => cat.id === currentPlatform) || categories[0];

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 10);
        };
        window.addEventListener('scroll', handleScroll, { passive: true });
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const handleCategoryChange = (category) => {
        if (category.url && category.id !== currentPlatform) {
            window.location.href = category.url;
        }
    };

    return (
        <header className={`header ${isScrolled ? 'scrolled' : ''}`}>
            <div className="header-container">
                <div className="header-main">
                    <div className="header-left">
                        <div className="category-selector-simple">
                            <div className="current-category-simple" style={{ background: currentCategory.gradient }}>
                                <span className="category-icon">{currentCategory.icon}</span>
                                <span className="category-name">{currentCategory.name}</span>
                                <span className="dropdown-arrow">▼</span>
                            </div>
                            
                            <div className="category-dropdown-simple">
                                {categories.map((category) => (
                                    <div
                                        key={category.id}
                                        className={`category-option-simple ${category.id === currentPlatform ? 'active' : ''}`}
                                        onClick={() => handleCategoryChange(category)}
                                    >
                                        <span className="option-icon">{category.icon}</span>
                                        <span className="option-name">{category.fullName}</span>
                                        {category.id === currentPlatform && <span className="active-indicator">✓</span>}
                                    </div>
                                ))}
                            </div>
                        </div>
                        
                        <div className="title-section-simple">
                            <h1 className="header-title-simple">
                                Les Actualités {currentCategory.name}
                            </h1>
                        </div>
                    </div>

                    <div className="header-center">
                        {/* Global search within header */}
                        <div className="global-search-wrapper header-search">
                            <div className="search-icon">🔍</div>
                            <input
                                type="text"
                                placeholder={viewMode === 'articles' ? 'Rechercher des articles...' : 'Rechercher des sujets...'}
                                value={globalSearchTerm}
                                onChange={(e) => setGlobalSearchTerm(e.target.value)}
                                className="global-search-input"
                            />
                            {globalSearchTerm && (
                                <button
                                    className="clear-search-button"
                                    onClick={() => setGlobalSearchTerm('')}
                                    aria-label="Effacer la recherche"
                                >
                                    ✕
                                </button>
                            )}
                        </div>
                    </div>

                    <div className="header-right">
                        {/* Filter sources */}
                        {viewMode === 'articles' && (
                            <button
                                className="feed-action-button icon-only"
                                onClick={onFilterSourcesClick}
                                aria-label="Filtrer les sources"
                            >
                                <FilterIcon />
                            </button>
                        )}

                        {/* Refresh */}
                        <RefreshButton onRefreshData={onRefreshData} />
                        <LanguageSwitcher activeLanguage={activeLanguage} onLanguageChange={onLanguageChange} />
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header; 