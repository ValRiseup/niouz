import React from 'react';
import './NewsCard.css';

const NewsCard = ({ article, isInTopic = false }) => {
  const formatDate = (dateString) => {
    if (!dateString) return '';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('fr-FR', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      return '';
    }
  };

  const getSourceCategoryIcon = (category) => {
    const icons = {
      'Politique France': '🇫🇷',
      'Politique Internationale': '🌍',
      'Europe & UE': '🇪🇺',
      'Analyses & Opinion': '💭',
      'Sondages & Data': '📊'
    };
    return icons[category] || '📰';
  };

  const handleCardClick = () => {
    if (article.url) {
      window.open(article.url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <article 
      className={`news-card ${isInTopic ? 'in-topic' : ''}`}
      onClick={handleCardClick}
    >
      <div className="card-image-container">
        {article.image ? (
          <img 
            src={article.image} 
            alt={article.title}
            className="card-image"
            onError={(e) => {
              e.target.style.display = 'none';
            }}
          />
        ) : (
          <div className="card-placeholder">
            <span className="placeholder-icon">🏛️</span>
          </div>
        )}
        
        {article.source_category && (
          <div className="card-category-badge">
            <span className="category-icon">
              {getSourceCategoryIcon(article.source_category)}
            </span>
            <span className="category-text">{article.source_category}</span>
          </div>
        )}
      </div>

      <div className="card-content">
        <div className="card-header">
          <h3 className="card-title">{article.title}</h3>
        </div>

        {article.summary && (
          <div className="card-summary">
            <p>{article.summary.substring(0, 150)}...</p>
          </div>
        )}

        <div className="card-footer">
          <div className="card-meta">
            <span className="card-source">
              📺 {article.source}
            </span>
            {article.date && (
              <span className="card-date">
                📅 {formatDate(article.date)}
              </span>
            )}
            {article.reading_time && (
              <span className="card-reading-time">
                ⏱️ {article.reading_time} min
              </span>
            )}
          </div>

          <div className="card-language">
            <span className={`language-badge ${article.language}`}>
              {article.language === 'fr' ? '🇫🇷 FR' : '🇬🇧 EN'}
            </span>
          </div>
        </div>
      </div>

      <div className="card-hover-overlay">
        <span className="hover-text">Cliquer pour lire l'article</span>
        <span className="hover-icon">🔗</span>
      </div>
    </article>
  );
};

export default NewsCard; 