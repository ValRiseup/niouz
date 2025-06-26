"""
Database configuration and models for AI News platform
"""

import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import StaticPool
import json

Base = declarative_base()

# Association table for many-to-many relationship between articles and topics
article_topics = Table(
    'article_topics',
    Base.metadata,
    Column('article_id', Integer, ForeignKey('articles.id'), primary_key=True),
    Column('topic_id', Integer, ForeignKey('topics.id'), primary_key=True)
)

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False)
    source = Column(String(100), nullable=False)
    source_category = Column(String(100))
    image = Column(String(1000))
    date = Column(DateTime(timezone=True))
    reading_time = Column(Integer)
    language = Column(String(10))
    summary = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    # Many-to-many relationship with topics
    topics = relationship("Topic", secondary=article_topics, back_populates="articles")
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'source': self.source,
            'source_category': self.source_category,
            'image': self.image,
            'date': self.date.isoformat() if self.date else None,
            'reading_time': self.reading_time,
            'language': self.language,
            'summary': self.summary,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Topic(Base):
    __tablename__ = 'topics'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    summary = Column(Text)
    description = Column(Text)
    keywords = Column(Text)  # JSON string
    category = Column(String(100))
    date_range = Column(String(100))
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    # Many-to-many relationship with articles
    articles = relationship("Article", secondary=article_topics, back_populates="topics")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'summary': self.summary,
            'description': self.description,
            'keywords': json.loads(self.keywords) if self.keywords else [],
            'category': self.category,
            'date_range': self.date_range,
            'articles': [article.to_dict() for article in self.articles],
            'sources': list(set(article.source for article in self.articles)),
            'image': self.articles[0].image if self.articles else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.init_database()
    
    def init_database(self):
        """Initialize database connection"""
        database_url = self.get_database_url()
        
        if database_url.startswith('sqlite'):
            # SQLite configuration
            self.engine = create_engine(
                database_url,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False}
            )
        else:
            # PostgreSQL configuration
            self.engine = create_engine(database_url)
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
        print(f"✅ [DB] Database initialized with URL: {database_url.split('@')[0]}@****")
    
    def get_database_url(self):
        """Get database URL from environment or default to SQLite"""
        # Try Railway PostgreSQL first
        if os.environ.get('DATABASE_URL'):
            return os.environ.get('DATABASE_URL')
        
        # Try Railway private networking
        if os.environ.get('DATABASE_PRIVATE_URL'):
            return os.environ.get('DATABASE_PRIVATE_URL')
        
        # Fallback to SQLite
        db_path = os.path.join(os.path.dirname(__file__), 'news.db')
        return f'sqlite:///{db_path}'
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def cleanup_old_articles(self, keep_count=1000):
        """Keep only the last N articles and their associated topics"""
        session = self.get_session()
        try:
            # Get total count
            total_articles = session.query(Article).count()
            
            if total_articles <= keep_count:
                print(f"📊 [DB] {total_articles} articles in database (under limit of {keep_count})")
                return
            
            # Get articles to delete (oldest ones)
            articles_to_delete = session.query(Article)\
                .order_by(Article.created_at.desc())\
                .offset(keep_count)\
                .all()
            
            print(f"🗑️  [DB] Cleaning up {len(articles_to_delete)} old articles (keeping {keep_count})")
            
            # Delete old articles (cascading will handle article_topics)
            for article in articles_to_delete:
                session.delete(article)
            
            # Clean up orphaned topics (topics with no articles)
            orphaned_topics = session.query(Topic)\
                .filter(~Topic.articles.any())\
                .all()
            
            for topic in orphaned_topics:
                session.delete(topic)
            
            session.commit()
            print(f"✅ [DB] Cleanup completed. Removed {len(orphaned_topics)} orphaned topics")
            
        except Exception as e:
            session.rollback()
            print(f"❌ [DB] Cleanup error: {e}")
        finally:
            session.close()
    
    def get_recent_articles(self, limit=50, language=None):
        """Get recent articles with optional language filter"""
        session = self.get_session()
        try:
            query = session.query(Article).order_by(Article.created_at.desc())
            
            if language and language != 'all':
                query = query.filter(Article.language == language)
            
            articles = query.limit(limit).all()
            return [article.to_dict() for article in articles]
        finally:
            session.close()
    
    def get_recent_topics(self, limit=20):
        """Get recent topics with their articles"""
        session = self.get_session()
        try:
            topics = session.query(Topic)\
                .order_by(Topic.created_at.desc())\
                .limit(limit)\
                .all()
            return [topic.to_dict() for topic in topics]
        finally:
            session.close()
    
    def store_articles_and_topics(self, articles_data, topics_data):
        """Store articles and topics in database"""
        session = self.get_session()
        try:
            # Store articles first
            article_objects = {}
            for article_data in articles_data:
                # Check if article already exists
                existing = session.query(Article).filter_by(url=article_data['url']).first()
                if existing:
                    article_objects[article_data['url']] = existing
                    continue
                
                # Create new article
                article = Article(
                    title=article_data['title'],
                    url=article_data['url'],
                    source=article_data['source'],
                    source_category=article_data.get('source_category'),
                    image=article_data.get('image'),
                    date=datetime.fromisoformat(article_data['date'].replace('Z', '+00:00')) if article_data.get('date') else None,
                    reading_time=article_data.get('reading_time'),
                    language=article_data.get('language'),
                    summary=article_data.get('summary')
                )
                session.add(article)
                session.flush()  # Get the ID
                article_objects[article_data['url']] = article
            
            # Store topics and link to articles
            for topic_data in topics_data:
                topic = Topic(
                    name=topic_data['name'],
                    summary=topic_data.get('summary'),
                    description=topic_data.get('description'),
                    keywords=json.dumps(topic_data.get('keywords', [])),
                    category=topic_data.get('category'),
                    date_range=topic_data.get('date_range')
                )
                
                # Link articles to topic
                for article_data in topic_data.get('articles', []):
                    if article_data['url'] in article_objects:
                        topic.articles.append(article_objects[article_data['url']])
                
                session.add(topic)
            
            session.commit()
            print(f"✅ [DB] Stored {len(article_objects)} articles and {len(topics_data)} topics")
            
            # Cleanup old articles
            self.cleanup_old_articles()
            
        except Exception as e:
            session.rollback()
            print(f"❌ [DB] Storage error: {e}")
            raise
        finally:
            session.close()

# Global database manager instance
db_manager = DatabaseManager() 