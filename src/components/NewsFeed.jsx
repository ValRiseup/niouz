import React, { useState, useEffect, useRef, useCallback } from 'react';
import NewsCard from './NewsCard';
import SkeletonCard from './SkeletonCard';
import { newsData } from '../data';
import './NewsFeed.css';

const ARTICLES_PER_PAGE = 6;

const NewsFeed = ({ activeCategory, selectedSources, activeLanguage }) => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const observer = useRef();

  const sortedArticles = [...newsData].sort((a, b) => {
    if (!a.date || !b.date) return 0;
    return new Date(b.date) - new Date(a.date);
  });

  const filteredArticles = sortedArticles.filter(article => {
    const categoryMatch = activeCategory === 'all' || article.category === activeCategory;
    const sourceMatch = selectedSources[article.source];
    const languageMatch = activeLanguage === 'all' || article.language === activeLanguage;
    return categoryMatch && sourceMatch && languageMatch;
  });

  useEffect(() => {
    setArticles([]);
    setPage(1);
    setHasMore(true);
    setLoading(true);
    const timer = setTimeout(() => {
        setArticles(filteredArticles.slice(0, ARTICLES_PER_PAGE));
        setHasMore(filteredArticles.length > ARTICLES_PER_PAGE);
        setLoading(false);
    }, 500);

    return () => clearTimeout(timer);
  }, [activeCategory, selectedSources, activeLanguage]);
  
  const lastArticleElementRef = useCallback(node => {
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
        const newArticles = filteredArticles.slice(0, page * ARTICLES_PER_PAGE);
        setArticles(newArticles);
        setHasMore(newArticles.length < filteredArticles.length);
    }
  }, [page, filteredArticles]);

  return (
    <main className="news-feed-container">
      <div className="news-feed-header">
        <h2>Fil d'Actualités de l'IA</h2>
        <p>Articles sélectionnés des meilleures sources IA</p>
      </div>
      <div className="news-feed">
        {articles.map((article, index) => {
            if (articles.length === index + 1) {
                return <div ref={lastArticleElementRef} key={`${activeCategory}-${index}`}><NewsCard article={article} /></div>
            } else {
                return <NewsCard key={`${activeCategory}-${index}`} article={article} />
            }
        })}
        {loading && Array.from({ length: ARTICLES_PER_PAGE }).map((_, index) => <SkeletonCard key={`skeleton-${index}`} />)}
        {!loading && articles.length === 0 && (
          <p className="no-articles-message">Aucun article trouvé dans cette catégorie.</p>
        )}
      </div>
    </main>
  );
};

export default NewsFeed; 