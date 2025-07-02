import React, { useState, useEffect, useMemo } from 'react';
import './index.css';
import Header from './components/Header';
import NewsFeed from './components/NewsFeed';
import Footer from './components/Footer';
import ScrollToTopButton from './components/ScrollToTopButton';
import ViewModeFab from './components/ViewModeFab';
import SourceSelector from './components/SourceSelector';
import { useNewsData } from './hooks/useNewsData';
import configUrl from './config.json?url';

function App() {
  const [activeLanguage, setActiveLanguage] = useState('all');
  const [sourceCategories, setSourceCategories] = useState(null);
  const [viewMode, setViewMode] = useState('articles'); // 'articles' or 'topics'
  const [showSourceSelector, setShowSourceSelector] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [globalSearchTerm, setGlobalSearchTerm] = useState('');
  const [autoRefreshing, setAutoRefreshing] = useState(false);
  
  // Fetch news data from API
  const { newsData, loading: newsDataLoading, error: newsDataError, refetch } = useNewsData(refreshTrigger);

  useEffect(() => {
    const handleScroll = () => {
        const yOffset = Math.min(window.scrollY * 0.2, 300);
        document.body.style.backgroundPositionY = `${yOffset}px`;

        // Auto refresh when scrolled to very top
        if (window.scrollY === 0 && !autoRefreshing) {
          setAutoRefreshing(true);
          refetch();
          // allow refresh again after 5 seconds
          setTimeout(() => setAutoRefreshing(false), 5000);
        }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    fetch(configUrl)
      .then(response => response.json())
      .then(data => setSourceCategories(data));
  }, []);

  const groupedSources = useMemo(() => {
    if (!sourceCategories) return {};
    const articles = newsData.articles || [];
    return Object.entries(sourceCategories).reduce((acc, [category, sources]) => {
      acc[category] = sources.map(source => ({
        ...source,
        count: articles.filter(article => article.source === source.name).length
      }));
      return acc;
    }, {});
  }, [sourceCategories, newsData]);
  
  const categoryOrder = useMemo(() => {
    if (!sourceCategories) return [];
    return ["General News & Impact", "Business & Startups", "Community & Blogs", "Technical"];
  }, [sourceCategories]);

  const orderedGroupedSources = useMemo(() => {
    if (!sourceCategories) return {};
    const ordered = {};
    categoryOrder.forEach(category => {
      if (groupedSources[category]) {
        ordered[category] = groupedSources[category].sort((a,b) => b.quality - a.quality);
      }
    });
    return ordered;
  }, [groupedSources, categoryOrder, sourceCategories]);

  const allSources = useMemo(() => {
    if (!orderedGroupedSources) return [];
    return Object.values(orderedGroupedSources).flat().map(s => s.name)
  }, [orderedGroupedSources]);

  const [selectedSources, setSelectedSources] = useState({});

  useEffect(() => {
    if(allSources.length > 0) {
      let savedSources = {};
      try {
        const saved = localStorage.getItem('selectedSources');
        if (saved) {
          const parsed = JSON.parse(saved);
          if (typeof parsed === 'object' && parsed !== null) {
            savedSources = parsed;
          }
        }
      } catch (error) {
        console.error("Could not load or parse selected sources from local storage", error);
      }
      
      setSelectedSources(allSources.reduce((acc, source) => {
        acc[source] = savedSources.hasOwnProperty(source) ? savedSources[source] : true;
        return acc;
      }, {}));
    }
  }, [allSources]);


  useEffect(() => {
    if (Object.keys(selectedSources).length > 0) {
      localStorage.setItem('selectedSources', JSON.stringify(selectedSources));
    }
  }, [selectedSources]);

  const handleSoloSelect = (soloSource) => {
    const newSelectedSources = allSources.reduce((acc, source) => {
      acc[source] = source === soloSource;
      return acc;
    }, {});
    setSelectedSources(newSelectedSources);
  };
  
  // Reset global search when switching view modes
  useEffect(() => {
    setGlobalSearchTerm('');
  }, [viewMode]);

  if (!sourceCategories || newsDataLoading) {
    return (
      <div className="loading-container" style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '1.1em',
        color: '#6b7280'
      }}>
        Loading {!sourceCategories ? 'configuration' : 'news data'}...
        {newsDataError && (
          <div style={{ color: '#ef4444', marginTop: '10px' }}>
            Error: {newsDataError}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="App">
      <Header 
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        activeLanguage={activeLanguage}
        onLanguageChange={setActiveLanguage}
        onFilterSourcesClick={() => setShowSourceSelector(s => !s)}
        onRefreshData={refetch}
        globalSearchTerm={globalSearchTerm}
        setGlobalSearchTerm={setGlobalSearchTerm}
      />
      <div className="content-wrapper">
        <main className="main-container">
          {showSourceSelector && (
            <SourceSelector
              groupedSources={orderedGroupedSources}
              selectedSources={selectedSources}
              setSelectedSources={setSelectedSources}
              onSoloSelect={handleSoloSelect}
              onClose={() => setShowSourceSelector(false)}
            />
          )}
          <NewsFeed
            newsData={newsData}
            selectedSources={selectedSources}
            activeLanguage={activeLanguage}
            viewMode={viewMode}
            onFilterSourcesClick={() => setShowSourceSelector(s => !s)}
            onRefreshData={refetch}
            globalSearchTerm={globalSearchTerm}
          />
        </main>
        <Footer />
        <ScrollToTopButton />
        <ViewModeFab viewMode={viewMode} onViewModeChange={setViewMode} />
      </div>
    </div>
  )
}

export default App;
