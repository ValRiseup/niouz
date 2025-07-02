import React, { useState } from 'react';
import NewsCard from './NewsCard.jsx';
import TopicCard from './TopicCard.jsx';
import './NewsFeed.css';

const NewsFeed = ({ content, viewMode, isLoading }) => {
  const [expandedTopics, setExpandedTopics] = useState(new Set());

  const toggleTopicExpansion = (topicId) => {
    const newExpanded = new Set(expandedTopics);
    if (newExpanded.has(topicId)) {
      newExpanded.delete(topicId);
    } else {
      newExpanded.add(topicId);
    }
    setExpandedTopics(newExpanded);
  };

  if (isLoading) {
    return (
      <div className="news-feed loading">
        <div className="loading-message">
          <span className="loading-icon">🔄</span>
          <p>Chargement des actualités politiques...</p>
        </div>
      </div>
    );
  }

  if (!content || content.length === 0) {
    return (
      <div className="news-feed empty">
        <div className="empty-message">
          <span className="empty-icon">📭</span>
          <h3>Aucun contenu trouvé</h3>
          <p>
            {viewMode === 'topics' 
              ? 'Aucun sujet politique ne correspond aux critères de recherche.'
              : 'Aucun article ne correspond aux critères de recherche.'
            }
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="news-feed">
      <div className="feed-header">
        <h2 className="feed-title">
          {viewMode === 'topics' ? '📚 Sujets Politiques' : '📰 Articles Politiques'}
        </h2>
        <span className="feed-count">
          {content.length} {viewMode === 'topics' ? 'sujets' : 'articles'}
        </span>
      </div>

      <div className={`feed-grid ${viewMode === 'topics' ? 'topics-grid' : 'articles-grid'}`}>
        {viewMode === 'topics' ? (
          content.map((topic) => (
            <TopicCard
              key={topic.id}
              topic={topic}
              isExpanded={expandedTopics.has(topic.id)}
              onToggleExpansion={() => toggleTopicExpansion(topic.id)}
            />
          ))
        ) : (
          content.map((article, index) => (
            <NewsCard
              key={`${article.url}-${index}`}
              article={article}
            />
          ))
        )}
      </div>

      {content.length > 0 && (
        <div className="feed-footer">
          <p className="feed-summary">
            {viewMode === 'topics' 
              ? `${content.length} sujets politiques analysés par IA`
              : `${content.length} articles de sources politiques vérifiées`
            }
          </p>
        </div>
      )}
    </div>
  );
};

export default NewsFeed; 