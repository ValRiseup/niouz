import React from 'react';
import './NewsCard.css';

const NewsCard = ({ article }) => {

  const timeAgo = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '';

    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    let interval = seconds / 31536000;
    if (interval > 1) {
        const years = Math.floor(interval);
        return years + (years === 1 ? " year ago" : " years ago");
    }
    interval = seconds / 2592000;
    if (interval > 1) {
        const months = Math.floor(interval);
        return months + (months === 1 ? " month ago" : " months ago");
    }
    interval = seconds / 86400;
    if (interval > 1) {
        const days = Math.floor(interval);
        return days + (days === 1 ? " day ago" : " days ago");
    }
    interval = seconds / 3600;
    if (interval > 1) {
        const hours = Math.floor(interval);
        return hours + (hours === 1 ? " hour ago" : " hours ago");
    }
    interval = seconds / 60;
    if (interval > 1) {
        const minutes = Math.floor(interval);
        return minutes + (minutes === 1 ? " minute ago" : " minutes ago");
    }
    return "just now";
  };

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
                  {article.reading_time && <span className="news-reading-time">{article.reading_time} min read</span>}
                </div>
            </div>
        </div>
    </a>
  );
};

export default NewsCard; 