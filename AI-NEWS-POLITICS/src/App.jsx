import React, { useState, useEffect, useMemo, useCallback } from 'react';

// Tentative d'importer les données - fallback si le fichier n'existe pas encore
let newsData = [];
let topicsData = [];

try {
  const dataModule = await import('./data.js');
  newsData = dataModule.newsData || [];
  topicsData = dataModule.topicsData || [];
} catch (error) {
  console.log('Data file not found, using empty arrays');
}

import Header from './components/Header.jsx';
import NewsFeed from './components/NewsFeed.jsx';
import Footer from './components/Footer.jsx';
import SourceSelector from './components/SourceSelector.jsx';
import RefreshButton from './components/RefreshButton.jsx';
import ProgressDisplay from './components/ProgressDisplay.jsx';
import ScrollToTopButton from './components/ScrollToTopButton.jsx';

import './index.css';

function App() {
  const [articles, setArticles] = useState(newsData);
  const [topics, setTopics] = useState(topicsData);
  const [selectedSources, setSelectedSources] = useState([]);
  const [selectedLanguage, setSelectedLanguage] = useState('all');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshProgress, setRefreshProgress] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('topics'); // 'topics' ou 'articles'

  // Extraire toutes les sources disponibles
  const availableSources = useMemo(() => {
    const sources = new Set();
    articles.forEach(article => {
      if (article.source) {
        sources.add(article.source);
      }
    });
    return Array.from(sources).sort();
  }, [articles]);

  // Filtrer les articles/sujets selon les critères sélectionnés
  const filteredContent = useMemo(() => {
    let content = viewMode === 'topics' ? topics : articles;
    
    // Filtrage par sources
    if (selectedSources.length > 0) {
      if (viewMode === 'topics') {
        content = content.filter(topic => 
          topic.sources && topic.sources.some(source => selectedSources.includes(source))
        );
      } else {
        content = content.filter(article => selectedSources.includes(article.source));
      }
    }

    // Filtrage par langue
    if (selectedLanguage !== 'all') {
      if (viewMode === 'topics') {
        content = content.filter(topic => 
          topic.articles && topic.articles.some(article => article.language === selectedLanguage)
        );
      } else {
        content = content.filter(article => article.language === selectedLanguage);
      }
    }

    // Filtrage par terme de recherche
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      if (viewMode === 'topics') {
        content = content.filter(topic => 
          topic.name.toLowerCase().includes(searchLower) ||
          topic.description.toLowerCase().includes(searchLower) ||
          topic.keywords.some(keyword => keyword.toLowerCase().includes(searchLower))
        );
      } else {
        content = content.filter(article => 
          article.title.toLowerCase().includes(searchLower) ||
          (article.summary && article.summary.toLowerCase().includes(searchLower))
        );
      }
    }

    return content;
  }, [articles, topics, selectedSources, selectedLanguage, searchTerm, viewMode]);

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    setRefreshProgress(0);

    try {
      // Simulation du processus de rafraîchissement
      const interval = setInterval(() => {
        setRefreshProgress(prev => {
          if (prev >= 90) {
            clearInterval(interval);
            return prev;
          }
          return prev + Math.random() * 10;
        });
      }, 500);

      // Tentative de rechargement des données
      try {
        const response = await fetch('/api/refresh', { method: 'POST' });
        if (response.ok) {
          const newData = await response.json();
          setArticles(newData.articles || []);
          setTopics(newData.topics || []);
        }
      } catch (apiError) {
        console.log('API refresh failed, data unchanged');
      }

      clearInterval(interval);
      setRefreshProgress(100);
      
      setTimeout(() => {
        setIsRefreshing(false);
        setRefreshProgress(0);
      }, 1000);

    } catch (error) {
      console.error('Refresh failed:', error);
      setIsRefreshing(false);
      setRefreshProgress(0);
    }
  }, []);

  return (
    <div className="App">
      {/* Dynamic Background Elements */}
      <div className="parallax-bg"></div>
      
      <Header 
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        totalItems={viewMode === 'topics' ? topics.length : articles.length}
        filteredCount={filteredContent.length}
      />
      
      <main className="main-content">
        {/* Enhanced Controls Section with Glass Effect */}
        <section className="controls-section">
          <div className="source-selector-container floating-element">
            <SourceSelector
              availableSources={availableSources}
              selectedSources={selectedSources}
              onSourcesChange={setSelectedSources}
              selectedLanguage={selectedLanguage}
              onLanguageChange={setSelectedLanguage}
            />
          </div>
          
          <div className="refresh-container floating-element">
            <RefreshButton 
              onRefresh={handleRefresh}
              isRefreshing={isRefreshing}
            />
          </div>
        </section>

        {/* Progress Display with Enhanced Glass Effect */}
        {isRefreshing && (
          <div className="progress-container slide-in">
            <ProgressDisplay 
              progress={refreshProgress}
              message="Récupération des actualités politiques..."
            />
          </div>
        )}

        {/* Enhanced News Feed Container */}
        <section className="news-feed-container fade-in">
          <NewsFeed 
            content={filteredContent}
            viewMode={viewMode}
            isLoading={isRefreshing}
          />
        </section>
      </main>

      <ScrollToTopButton />
      <Footer />
    </div>
  );
}

export default App; 