import sqlite3
import json
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='news.db'):
        self.db_path = os.path.join(os.path.dirname(__file__), db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Articles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    source TEXT NOT NULL,
                    source_category TEXT,
                    image TEXT,
                    date TEXT,
                    reading_time INTEGER,
                    language TEXT,
                    summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Topics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS topics (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    summary TEXT,
                    description TEXT,
                    category TEXT,
                    date_range TEXT,
                    keywords TEXT,
                    sources TEXT,
                    image TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Topic-Article relationship table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS topic_articles (
                    topic_id TEXT,
                    article_url TEXT,
                    FOREIGN KEY (topic_id) REFERENCES topics (id),
                    FOREIGN KEY (article_url) REFERENCES articles (url),
                    PRIMARY KEY (topic_id, article_url)
                )
            ''')
            
            conn.commit()
    
    def save_articles(self, articles):
        """Save articles to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for article in articles:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO articles 
                        (title, url, source, source_category, image, date, reading_time, language, summary)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        article['title'],
                        article['url'],
                        article['source'],
                        article.get('source_category'),
                        article.get('image'),
                        article.get('date'),
                        article.get('reading_time'),
                        article.get('language'),
                        article.get('summary')
                    ))
                except sqlite3.Error as e:
                    print(f"Error saving article {article['title']}: {e}")
            
            conn.commit()
    
    def save_topics(self, topics):
        """Save topics and their article relationships"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for topic in topics:
                try:
                    # Save topic
                    cursor.execute('''
                        INSERT OR REPLACE INTO topics 
                        (id, name, summary, description, category, date_range, keywords, sources, image)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        topic['id'],
                        topic['name'],
                        topic.get('summary'),
                        topic.get('description'),
                        topic.get('category'),
                        topic.get('date_range'),
                        json.dumps(topic.get('keywords', [])),
                        json.dumps(topic.get('sources', [])),
                        topic.get('image')
                    ))
                    
                    # Clear existing topic-article relationships
                    cursor.execute('DELETE FROM topic_articles WHERE topic_id = ?', (topic['id'],))
                    
                    # Save topic-article relationships
                    for article in topic.get('articles', []):
                        cursor.execute('''
                            INSERT INTO topic_articles (topic_id, article_url)
                            VALUES (?, ?)
                        ''', (topic['id'], article['url']))
                        
                except sqlite3.Error as e:
                    print(f"Error saving topic {topic['name']}: {e}")
            
            conn.commit()
    
    def get_all_articles(self):
        """Retrieve all articles from database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM articles ORDER BY date DESC')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_topics(self):
        """Retrieve all topics with their articles"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get topics
            cursor.execute('SELECT * FROM topics ORDER BY created_at DESC')
            topics = []
            
            for row in cursor.fetchall():
                topic = dict(row)
                topic['keywords'] = json.loads(topic['keywords']) if topic['keywords'] else []
                topic['sources'] = json.loads(topic['sources']) if topic['sources'] else []
                
                # Get articles for this topic
                cursor.execute('''
                    SELECT a.* FROM articles a
                    JOIN topic_articles ta ON a.url = ta.article_url
                    WHERE ta.topic_id = ?
                    ORDER BY a.date DESC
                ''', (topic['id'],))
                
                topic['articles'] = [dict(article_row) for article_row in cursor.fetchall()]
                topics.append(topic)
            
            return topics

# Global instance
db_manager = DatabaseManager() 