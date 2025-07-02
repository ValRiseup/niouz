import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import Masonry from 'react-masonry-css';
import NewsCard from './NewsCard';
import TopicCard from './TopicCard';
import SkeletonCard from './SkeletonCard';
import RefreshButton from './RefreshButton';
import './NewsFeed.css';

const ITEMS_PER_PAGE = 6;

const NewsFeed = ({ newsData, selectedSources, activeLanguage, viewMode, onFilterSourcesClick, onRefreshData, globalSearchTerm }) => {
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

  const filteredArticles = useMemo(() => {
    let articles = sortedArticles.filter(article => {
      const sourceMatch = selectedSources[article.source];
      const languageMatch = activeLanguage === 'all' || article.language === activeLanguage;
      return sourceMatch && languageMatch;
    });

    // Apply global search to articles
    if (globalSearchTerm) {
      articles = articles.filter(article => 
        article.title.toLowerCase().includes(globalSearchTerm.toLowerCase()) ||
        (article.summary && article.summary.toLowerCase().includes(globalSearchTerm.toLowerCase())) ||
        article.source.toLowerCase().includes(globalSearchTerm.toLowerCase()) ||
        (article.category && article.category.toLowerCase().includes(globalSearchTerm.toLowerCase()))
      );
    }

    return articles;
  }, [sortedArticles, selectedSources, activeLanguage, globalSearchTerm]);

  const processedTopics = useMemo(() => {
    let topics = newsData.topics || [];

    // Apply topic-specific search first
    if (searchTerm) {
        topics = topics.filter(topic => 
            topic.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            topic.description.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }

    // Apply global search to topics
    if (globalSearchTerm) {
      topics = topics.filter(topic => 
        topic.name.toLowerCase().includes(globalSearchTerm.toLowerCase()) ||
        topic.description.toLowerCase().includes(globalSearchTerm.toLowerCase()) ||
        topic.articles.some(article => 
          article.title.toLowerCase().includes(globalSearchTerm.toLowerCase()) ||
          article.source.toLowerCase().includes(globalSearchTerm.toLowerCase())
        )
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
  }, [newsData.topics, sortOrder, searchTerm, globalSearchTerm]);


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
        // show skeleton cards briefly
        setLoading(true);
        setTimeout(() => {
          setItems(prevItems => [
            ...prevItems,
            ...data.slice(prevItems.length, prevItems.length + ITEMS_PER_PAGE)
          ]);
        }, 50);
      }
    });
    if (node) observer.current.observe(node);
  }, [loading, items.length, data]);

  // deactivate loading when items updated
  useEffect(() => {
    setLoading(false);
  }, [items]);

  return (
    <>
      {/* Controls wrapper now only used for topic-specific utilities */}
      <div className="feed-controls-container">
        {viewMode === 'topics' && (
          <div className="topic-controls-horizontal">
            <div className="topic-controls-left">
              <div className="topic-search">
                <input 
                    type="text" 
                    placeholder="Filtrer les sujets..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            
            <div className="topic-controls-center" />
            
            <div className="topic-controls-right">
              <div className="topic-sort">
                  <span>Trier par:</span>
                  <button className={sortOrder === 'sources' ? 'active' : ''} onClick={() => setSortOrder('sources')}>Sources</button>
                  <button className={sortOrder === 'articles' ? 'active' : ''} onClick={() => setSortOrder('articles')}>Articles</button>
                  <button className={sortOrder === 'recency' ? 'active' : ''} onClick={() => setSortOrder('recency')}>Récence</button>
              </div>
            </div>
          </div>
        )}
        
        {globalSearchTerm && (
          <div className="search-results-count">
            {data.length} résultat{data.length !== 1 ? 's' : ''} trouvé{data.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>

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
            {globalSearchTerm ? '🔍' : (viewMode === 'articles' ? '📰' : '📁')}
          </div>
          <h3>
            {globalSearchTerm 
              ? 'Aucun résultat trouvé' 
              : (viewMode === 'articles' ? 'Aucun article trouvé' : 'Aucun sujet trouvé')
            }
          </h3>
          <p>
            {globalSearchTerm 
              ? `Aucun ${viewMode === 'articles' ? 'article' : 'sujet'} ne correspond à "${globalSearchTerm}".`
              : (viewMode === 'articles' 
                ? 'Aucun article ne correspond aux filtres sélectionnés.' 
                : 'Aucun sujet ne correspond aux critères de recherche.'
              )
            }
          </p>
          {!globalSearchTerm && viewMode === 'articles' && (
            <div className="no-articles-actions">
              <RefreshButton onRefreshData={onRefreshData} />
              <button 
                className="feed-action-button" 
                onClick={onFilterSourcesClick}
                aria-label="Modifier les filtres des sources"
              >
                Modifier les filtres
              </button>
            </div>
          )}
        </div>
      )}
    </>
  );
};

export default NewsFeed; 