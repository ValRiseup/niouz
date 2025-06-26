import React from 'react';
import './NewsCard.css';

const NewsCard = ({ article }) => {

  const timeAgo = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '';

    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    const rtf = new Intl.RelativeTimeFormat('fr-FR', { numeric: 'auto' });

    let interval = Math.floor(seconds / 31536000);
    if (interval >= 1) {
      return rtf.format(-interval, 'year');
    }
    interval = Math.floor(seconds / 2592000);
    if (interval >= 1) {
      return rtf.format(-interval, 'month');
    }
    interval = Math.floor(seconds / 86400);
    if (interval >= 1) {
      return rtf.format(-interval, 'day');
    }
    interval = Math.floor(seconds / 3600);
    if (interval >= 1) {
      return rtf.format(-interval, 'hour');
    }
    interval = Math.floor(seconds / 60);
    if (interval >= 1) {
      return rtf.format(-interval, 'minute');
    }
    return rtf.format(0, 'second');
  };

  const readingTimeText = `${article.reading_time} min de lecture`;

  return (
    <a href={article.url} target="_blank" rel="noopener noreferrer" className="news-card-link">
        <div className="news-card">
            <img 
              src={article.image} 
              alt={article.title} 
              className="news-image" 
              onError={(e) => { e.target.onerror = null; e.target.src=`https://picsum.photos/seed/${article.title}/400/300`}}
            />
            <div className="news-content">
                <p className="news-source">{article.source}</p>
                <h3>{article.title}</h3>
                <div className="news-meta">
                  {article.date && <span className="news-date">{timeAgo(article.date)}</span>}
                  {article.date && article.reading_time && <span className="news-dot">·</span>}
                  {article.reading_time && <span className="news-reading-time">{readingTimeText}</span>}
                </div>
            </div>
        </div>
    </a>
  );
};

export default NewsCard; 