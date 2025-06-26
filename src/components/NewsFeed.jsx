import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import Masonry from 'react-masonry-css';
import NewsCard from './NewsCard';
import TopicCard from './TopicCard';
import SkeletonCard from './SkeletonCard';
import { newsData } from '../data';
import './NewsFeed.css';

const ITEMS_PER_PAGE = 6;

const NewsFeed = ({ selectedSources, activeLanguage, viewMode }) => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const observer = useRef();
  
  // State for Topic View
  const [sortOrder, setSortOrder] = useState('recency'); // 'recency', 'articles', 'sources'
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
  const masonryBreakpointColumns = {
    default: 3,
    1024: 2,
    600: 1
  };

  useEffect(() => {
    setItems([]);
    setPage(1);
    setHasMore(true);
    setLoading(true);
    const timer = setTimeout(() => {
        setItems(data.slice(0, ITEMS_PER_PAGE));
        setHasMore(data.length > ITEMS_PER_PAGE);
        setLoading(false);
    }, 500);

    return () => clearTimeout(timer);
  }, [selectedSources, activeLanguage, viewMode, sortOrder, searchTerm]);
  
  const lastItemElementRef = useCallback(node => {
    if (loading) return;
    if (observer.current) observer.current.disconnect();
    observer.current = new IntersectionObserver(entries => {
        if (entries[0].isIntersecting && hasMore) {
            setPage(prevPage => prevPage + 1);
        }
    });
    if (node) observer.current.observe(node);
  }, [loading, hasMore]);

  useEffect(() => {
    if (page > 1) {
        const newItems = data.slice(0, page * ITEMS_PER_PAGE);
        setItems(newItems);
        setHasMore(newItems.length < data.length);
    }
  }, [page, data]);

  return (
    <main className="news-feed-container">
      <div className="news-feed-header">
        <h2>{viewMode === 'articles' ? "Fil d'Actualités de l'IA" : "Sujets d'Actualités de l'IA"}</h2>
        <p>{viewMode === 'articles' ? "Articles sélectionnés des meilleures sources IA" : "Sujets regroupés à partir de plusieurs sources"}</p>
      </div>

      {viewMode === 'topics' && (
        <div className="topic-controls">
            <div className="topic-search">
                <input 
                    type="text" 
                    placeholder="Search topics..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
            </div>
            <div className="topic-sort">
                <span>Sort by:</span>
                <button className={sortOrder === 'recency' ? 'active' : ''} onClick={() => setSortOrder('recency')}>Recency</button>
                <button className={sortOrder === 'articles' ? 'active' : ''} onClick={() => setSortOrder('articles')}>Articles</button>
                <button className={sortOrder === 'sources' ? 'active' : ''} onClick={() => setSortOrder('sources')}>Sources</button>
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
        <p className="no-articles-message">{viewMode === 'articles' ? "Aucun article trouvé" : "Aucun sujet trouvé"}.</p>
      )}
    </main>
  );
};

export default NewsFeed; 