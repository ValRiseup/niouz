import React, { useState } from 'react';
import './TopicCard.css';
import ChevronIcon from '../assets/icons/chevron.svg?react';
import GlobeIcon from '../assets/icons/globe.svg?react';

const TopicCard = ({ topic }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  // Calculate coverage stats
  const sourcesCount = topic.sources?.length || 0;
  const articlesCount = topic.articles?.length || 0;
  const uniqueSources = [...new Set(topic.articles?.map(a => a.source) || [])];
  
  // Group articles by source for better presentation
  const articlesBySource = topic.articles?.reduce((acc, article) => {
    if (!acc[article.source]) {
      acc[article.source] = [];
    }
    acc[article.source].push(article);
    return acc;
  }, {}) || {};

  // Get latest and earliest dates
  const dates = topic.articles?.map(a => new Date(a.date)).filter(d => !isNaN(d)) || [];
  const latestDate = dates.length > 0 ? new Date(Math.max(...dates)) : null;
  const earliestDate = dates.length > 0 ? new Date(Math.min(...dates)) : null;
  
  const formatDate = (date) => {
    return date.toLocaleDateString('fr-FR', { 
      day: 'numeric', 
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className={`topic-card ${isExpanded ? 'expanded' : ''}`}>
        <div className="topic-card-image">
            <img src={topic.image} alt={topic.name} />
            {topic.category && <div className="topic-card-category">{topic.category}</div>}
            <div className="topic-card-coverage-badge">
                <GlobeIcon />
                <span>{sourcesCount} sources</span>
            </div>
        </div>
        <div className="topic-card-content">
            <h3 className="topic-card-title">{topic.name}</h3>
            
            {/* Enhanced factual summary */}
            <div className="topic-card-summary">
                {topic.summary && (
                    <p className="topic-card-description">{topic.summary}</p>
                )}
                
                {/* Coverage overview */}
                <div className="topic-coverage-overview">
                    <div className="coverage-stat">
                        <span className="coverage-number">{articlesCount}</span>
                        <span className="coverage-label">articles</span>
                    </div>
                    <div className="coverage-stat">
                        <span className="coverage-number">{sourcesCount}</span>
                        <span className="coverage-label">médias</span>
                    </div>
                    {latestDate && (
                        <div className="coverage-stat">
                            <span className="coverage-number">{formatDate(latestDate)}</span>
                            <span className="coverage-label">dernière maj</span>
                        </div>
                    )}
                </div>

                {/* Sources preview */}
                {uniqueSources.length > 0 && (
                    <div className="topic-sources-preview">
                        <span className="sources-label">Couverture médiatique :</span>
                        <div className="sources-list">
                            {uniqueSources.slice(0, 4).map((source, index) => (
                                <span key={index} className="source-chip">
                                    {source}
                                    {articlesBySource[source].length > 1 && (
                                        <span className="source-count">×{articlesBySource[source].length}</span>
                                    )}
                                </span>
                            ))}
                            {uniqueSources.length > 4 && (
                                <span className="source-chip more">+{uniqueSources.length - 4} autres</span>
                            )}
                        </div>
                    </div>
                )}
            </div>

            {topic.keywords && topic.keywords.length > 0 && (
                <div className="topic-card-keywords">
                    {topic.keywords.slice(0, 5).map((keyword, index) => (
                        <span key={index} className="keyword-chip">{keyword}</span>
                    ))}
                    {topic.keywords.length > 5 && (
                        <span className="keyword-chip more">+{topic.keywords.length - 5}</span>
                    )}
                </div>
            )}
            
            {topic.articles && topic.articles.length > 0 && (
                <button 
                    className="topic-card-expand-button"
                    onClick={toggleExpanded}
                    aria-expanded={isExpanded}
                >
                    <span>Voir tous les articles ({articlesCount})</span>
                    <ChevronIcon className="topic-card-expand-indicator" />
                </button>
            )}
        </div>
        
        {isExpanded && topic.articles && topic.articles.length > 0 && (
            <div className="topic-card-articles">
                <h4>Couverture complète du sujet ({articlesCount} articles)</h4>
                
                {/* Group by source for better readability */}
                {Object.entries(articlesBySource)
                    .sort(([,a], [,b]) => b.length - a.length) // Sort by number of articles per source
                    .map(([source, articles]) => (
                    <div key={source} className="source-group">
                        <div className="source-group-header">
                            <h5>{source}</h5>
                            <span className="source-article-count">{articles.length} article{articles.length > 1 ? 's' : ''}</span>
                        </div>
                        <ul className="source-articles">
                            {articles.map((article, index) => (
                                <li key={index}>
                                    <a href={article.url} target="_blank" rel="noopener noreferrer">
                                        <div className="article-info">
                                            <span className="article-title">{article.title}</span>
                                            <span className="article-date">{formatDate(new Date(article.date))}</span>
                                        </div>
                                    </a>
                                </li>
                            ))}
                        </ul>
                    </div>
                ))}
            </div>
        )}
    </div>
  );
};

export default TopicCard; 