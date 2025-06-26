import React, { useState, useEffect, useMemo } from 'react';
import './index.css';
import Header from './components/Header';
import NewsFeed from './components/NewsFeed';
import Footer from './components/Footer';
import ScrollToTopButton from './components/ScrollToTopButton';
import SourceSelector from './components/SourceSelector';
import { newsData } from './data';
import configUrl from './config.json?url';

function App() {
  const [activeLanguage, setActiveLanguage] = useState('all');
  const [sourceCategories, setSourceCategories] = useState(null);
  const [viewMode, setViewMode] = useState('articles'); // 'articles' or 'topics'
  const [showSourceSelector, setShowSourceSelector] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
        document.body.style.backgroundPositionY = `${window.scrollY * 0.5}px`;
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
  
  if (!sourceCategories) {
    return <div>Loading configuration...</div>;
  }

  return (
    <div className="App">
      <Header 
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        activeLanguage={activeLanguage}
        onLanguageChange={setActiveLanguage}
      />
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
          selectedSources={selectedSources}
          activeLanguage={activeLanguage}
          viewMode={viewMode}
          onFilterSourcesClick={() => setShowSourceSelector(s => !s)}
        />
      </main>
      <Footer />
      <ScrollToTopButton />
    </div>
  )
}

export default App;
