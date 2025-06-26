import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import Masonry from 'react-masonry-css';
import NewsCard from './NewsCard';
import TopicCard from './TopicCard';
import SkeletonCard from './SkeletonCard';
import RefreshButton from './RefreshButton';
import { newsData } from '../data';
import './NewsFeed.css';
import FilterIcon from '../assets/icons/filter.svg?react';

const ITEMS_PER_PAGE = 6;

const NewsFeed = ({ selectedSources, activeLanguage, viewMode, onFilterSourcesClick }) => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const observer = useRef();

  // State for Topic View
  const [sortOrder, setSortOrder] = useState('sources'); // 'sources', 'recency', 'articles'
  const [searchTerm, setSearchTerm] = useState('');

  const sortedArticles = useMemo(() => (newsData.articles || []).sort((a, b) => {
    if (!a.date || !b.date) return 0;
    return new Date(b.date) - new Date(a.date);
  }), [newsData.articles]);

  const filteredArticles = useMemo(() => sortedArticles.filter(article => {
    const sourceMatch = selectedSources[article.source];
    const languageMatch = activeLanguage === 'all' || article.language === activeLanguage;
    return sourceMatch && languageMatch;
  }), [sortedArticles, selectedSources, activeLanguage]);

  const processedTopics = useMemo(() => {
    let topics = newsData.topics || [];

    // Search filter
    if (searchTerm) {
        topics = topics.filter(topic => 
            topic.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            topic.description.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }

    // Sorting
    return [...topics].sort((a, b) => {
        if (sortOrder === 'articles') {
            return b.articles.length - a.articles.length;
        }
        if (sortOrder === 'sources') {
            return b.sources.length - a.sources.length;
        }
        // Default: recency
        const dateA = a.articles.reduce((latest, article) => new Date(article.date) > latest ? new Date(article.date) : latest, new Date(0));
        const dateB = b.articles.reduce((latest, article) => new Date(article.date) > latest ? new Date(article.date) : latest, new Date(0));
        return dateB - dateA;
    });
  }, [newsData.topics, sortOrder, searchTerm]);


  const data = viewMode === 'articles' ? filteredArticles : processedTopics;

  // Breakpoints for Masonry layout
  const masonryBreakpointColumns = viewMode === 'topics' ? {
    default: 2,
    768: 1
  } : {
    default: 3,
    1024: 2,
    600: 1
  };

  useEffect(() => {
    setItems(data.slice(0, ITEMS_PER_PAGE));
    setLoading(false);
}, [data, viewMode]);

  // Infinite scroll logic
  const lastItemElementRef = useCallback(node => {
    if (loading) return;
    if (observer.current) observer.current.disconnect();
    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && items.length < data.length) {
        setItems(prevItems => [
            ...prevItems,
            ...data.slice(prevItems.length, prevItems.length + ITEMS_PER_PAGE)
        ]);
      }
    });
    if (node) observer.current.observe(node);
  }, [loading, items.length, data]);

  return (
    <>
      <div className="news-feed-header">
        <h2>{viewMode === 'articles' ? "Fil d'Actualités de l'IA" : "Sujets d'Actualités de l'IA"}</h2>
        <p>{viewMode === 'articles' ? "Articles sélectionnés des meilleures sources IA" : "Sujets regroupés à partir de plusieurs sources"}</p>
      </div>

      {viewMode === 'articles' && (
        <div className="feed-controls">
          <div className="feed-controls-left">
            <button 
              className="feed-action-button" 
              onClick={onFilterSourcesClick}
              aria-label="Ouvrir le filtre des sources"
            >
              <FilterIcon />
              <span>Sources</span>
            </button>
          </div>
          <div className="feed-controls-right">
            <RefreshButton />
          </div>
        </div>
      )}

      {viewMode === 'topics' && (
        <div className="topic-controls">
            <div className="topic-search">
                <input 
                    type="text" 
                    placeholder="Rechercher des sujets..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
            </div>
            <div className="topic-sort">
                <span>Trier par:</span>
                <button className={sortOrder === 'sources' ? 'active' : ''} onClick={() => setSortOrder('sources')}>Sources</button>
                <button className={sortOrder === 'articles' ? 'active' : ''} onClick={() => setSortOrder('articles')}>Articles</button>
                <button className={sortOrder === 'recency' ? 'active' : ''} onClick={() => setSortOrder('recency')}>Récence</button>
            </div>
        </div>
      )}

      <Masonry
        breakpointCols={masonryBreakpointColumns}
        className="masonry-grid"
        columnClassName="masonry-grid-column"
      >
        {items.map((item, index) => {
            const key = viewMode === 'articles' ? (item.url || index) : (item.id || index);
            const isLastItem = items.length === index + 1;
            return (
                <div 
                    key={key} 
                    ref={isLastItem ? lastItemElementRef : null} 
                    className="feed-item-wrap" 
                    style={{ animationDelay: `${index * 50}ms` }}
                >
                    {viewMode === 'articles' ? <NewsCard article={item} /> : <TopicCard topic={item} />}
                </div>
            );
        })}
      </Masonry>
      
      {loading && (
        <div className="skeleton-grid">
            {Array.from({ length: ITEMS_PER_PAGE }).map((_, index) => <SkeletonCard key={`skeleton-${index}`} />)}
        </div>
      )}

      {!loading && items.length === 0 && (
        <div className="no-articles-message">
          <div className="no-articles-icon">
            {viewMode === 'articles' ? '📰' : '📁'}
          </div>
          <h3>{viewMode === 'articles' ? 'Aucun article trouvé' : 'Aucun sujet trouvé'}</h3>
          <p>
            {viewMode === 'articles' 
              ? 'Aucun article ne correspond aux filtres sélectionnés.' 
              : 'Aucun sujet ne correspond aux critères de recherche.'
            }
          </p>
          {viewMode === 'articles' && (
            <div className="no-articles-actions">
              <RefreshButton />
              <button 
                className="feed-action-button" 
                onClick={onFilterSourcesClick}
                aria-label="Modifier les filtres des sources"
              >
                <FilterIcon />
                <span>Modifier les filtres</span>
              </button>
            </div>
          )}
        </div>
      )}
    </>
  );
};

export default NewsFeed; 