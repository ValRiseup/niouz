import React from 'react';
import NewsCard from './NewsCard.jsx';
import './TopicCard.css';

const TopicCard = ({ topic, isExpanded, onToggleExpansion }) => {
  const getCategoryIcon = (category) => {
    const icons = {
      'National': '🏛️',
      'International': '🌍',
      'Elections': '🗳️',
      'Policy': '📋',
      'Scandal': '⚡',
      'Parliament': '🏢',
      'Politique': '🏛️'
    };
    return icons[category] || '📰';
  };

  const getCategoryColor = (category) => {
    const colors = {
      'National': '#dc2626',
      'International': '#059669',
      'Elections': '#7c3aed',
      'Policy': '#0891b2',
      'Scandal': '#ea580c',
      'Parliament': '#1d4ed8',
      'Politique': '#dc2626'
    };
    return colors[category] || '#6b7280';
  };

  return (
    <div className="topic-card">
      <div className="topic-header">
        <div className="topic-main-info">
          <div className="topic-category">
            <span className="category-icon">{getCategoryIcon(topic.category)}</span>
            <span 
              className="category-label"
              style={{ color: getCategoryColor(topic.category) }}
            >
              {topic.category}
            </span>
          </div>
          
          <h3 className="topic-title">{topic.name}</h3>
          
          <p className="topic-description">{topic.description}</p>
          
          {topic.summary && (
            <div className="topic-summary">
              <p>{topic.summary}</p>
            </div>
          )}
        </div>

        <div className="topic-meta">
          <div className="topic-stats">
            <span className="stat-item">
              📰 {topic.articles?.length || 0} articles
            </span>
            <span className="stat-item">
              📺 {topic.sources?.length || 0} sources
            </span>
            {topic.date_range && (
              <span className="stat-item">
                📅 {topic.date_range}
              </span>
            )}
          </div>

          {topic.keywords && topic.keywords.length > 0 && (
            <div className="topic-keywords">
              {topic.keywords.slice(0, 5).map((keyword, index) => (
                <span key={index} className="keyword-tag">
                  {keyword}
                </span>
              ))}
            </div>
          )}

          {topic.sources && topic.sources.length > 0 && (
            <div className="topic-sources">
              <strong>Sources :</strong> {topic.sources.join(', ')}
            </div>
          )}
        </div>
      </div>

      {topic.articles && topic.articles.length > 0 && (
        <div className="topic-articles-section">
          <button 
            className="expand-button"
            onClick={onToggleExpansion}
          >
            <span className="expand-icon">
              {isExpanded ? '📖' : '👁️'}
            </span>
            {isExpanded ? 'Masquer les articles' : `Voir les ${topic.articles.length} articles`}
            <span className="expand-arrow">
              {isExpanded ? '↑' : '↓'}
            </span>
          </button>

          {isExpanded && (
            <div className="topic-articles-grid">
              {topic.articles.map((article, index) => (
                <div key={`${article.url}-${index}`} className="topic-article-wrapper">
                  <NewsCard article={article} isInTopic={true} />
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TopicCard; 