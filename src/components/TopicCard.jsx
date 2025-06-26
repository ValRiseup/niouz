import React, { useState } from 'react';
import './TopicCard.css';
import globeIcon from '../assets/icons/globe.svg';
import chevronIcon from '../assets/icons/chevron.svg';
import listIcon from '../assets/icons/list.svg';
import calendarIcon from '../assets/icons/calendar.svg';

const TopicCard = ({ topic }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className={`topic-card ${isExpanded ? 'expanded' : ''}`} onClick={() => setIsExpanded(!isExpanded)}>
      <div className="topic-card-image">
        <img src={topic.image} alt={topic.name} />
        {topic.category && <div className="topic-card-category">{topic.category}</div>}
      </div>
      <div className="topic-card-content">
        <h3 className="topic-card-title">{topic.name}</h3>
        <p className="topic-card-description">{topic.description}</p>
        <div className="topic-card-footer">
            <div className="topic-card-sources">
                <img src={globeIcon} alt="Sources" />
                <span>{topic.sources && Array.isArray(topic.sources) ? topic.sources.join(', ') : 'N/A'}</span>
            </div>
            <div className="topic-card-meta">
                <div className="topic-card-article-count">
                    <img src={listIcon} alt="Articles" />
                    <span>{topic.articles?.length || 0} Articles</span>
                </div>
                {topic.date_range && (
                    <div className="topic-card-date">
                        <img src={calendarIcon} alt="Date" />
                        <span>{topic.date_range}</span>
                    </div>
                )}
                <div className="topic-card-expand-indicator">
                  <img src={chevronIcon} alt="expand" className="chevron-icon" />
                </div>
            </div>
        </div>
        {topic.keywords && topic.keywords.length > 0 && (
            <div className="topic-card-keywords">
                {topic.keywords.map(keyword => <span key={keyword} className="keyword-chip">{keyword}</span>)}
            </div>
        )}
      </div>
      {isExpanded && (
        <div className="topic-card-articles">
          <h4>Articles in this topic:</h4>
          <ul>
            {topic.articles.map(article => (
              <li key={article.url}>
                <a href={article.url} target="_blank" rel="noopener noreferrer">
                  {article.title}
                  <span className="article-source-chip">{article.source}</span>
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default TopicCard; 