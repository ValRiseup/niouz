#!/usr/bin/env python3
"""
Political Source Validator
Validates RSS feeds and assesses source quality for political news aggregation
"""

import json
import time
import concurrent.futures
from datetime import datetime, timedelta
from urllib.parse import urlparse
import logging
from typing import Dict, List, Optional, Tuple, Any
import re
import statistics

# Try to import optional dependencies
try:
    import feedparser
    import requests
    from bs4 import BeautifulSoup
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("Warning: Some dependencies are missing. Install with: pip install -r requirements_political_sources.txt")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('political_source_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PoliticalSourceValidator:
    """Validates political news sources for quality and reliability"""
    
    def __init__(self, config_file: str = "AI-NEWS-POLITICS/src/config_enhanced.json"):
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("Required dependencies not installed. Run: pip install -r requirements_political_sources.txt")
        
        self.config_file = config_file
        self.sources_data = self.load_sources()
        self.session = self.create_session()
        self.validation_results = {}
        
        # Political keywords for content relevance scoring
        self.political_keywords = [
            'election', 'parliament', 'government', 'policy', 'legislation',
            'candidate', 'vote', 'campaign', 'minister', 'president',
            'congress', 'senate', 'democracy', 'politics', 'political',
            'constitution', 'referendum', 'ballot', 'governance', 'coalition',
            'opposition', 'party', 'diplomat', 'treaty', 'regulation'
        ]
    
    def load_sources(self) -> Dict[str, Any]:
        """Load sources from configuration file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file {self.config_file} not found")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            return {}
    
    def create_session(self) -> requests.Session:
        """Create HTTP session with retry logic"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        return session
    
    def validate_rss_feed(self, url: str, timeout: int = 30) -> Dict[str, Any]:
        """Validate RSS feed accessibility and structure"""
        validation_result: Dict[str, Any] = {
            'accessible': False,
            'valid_rss': False,
            'entry_count': 0,
            'latest_entry_age': None,
            'errors': []
        }
        
        try:
            # Fetch RSS feed
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            # Parse RSS feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                validation_result['errors'].append(f"RSS parsing error: {feed.bozo_exception}")
                return validation_result
            
            validation_result['accessible'] = True
            validation_result['valid_rss'] = True
            validation_result['entry_count'] = len(feed.entries)
            
            # Check latest entry age
            if feed.entries:
                latest_entry = feed.entries[0]
                if hasattr(latest_entry, 'published_parsed') and latest_entry.published_parsed:
                    latest_time = datetime(*latest_entry.published_parsed[:6])
                    validation_result['latest_entry_age'] = (datetime.now() - latest_time).days
                elif hasattr(latest_entry, 'updated_parsed') and latest_entry.updated_parsed:
                    latest_time = datetime(*latest_entry.updated_parsed[:6])
                    validation_result['latest_entry_age'] = (datetime.now() - latest_time).days
            
        except requests.exceptions.RequestException as e:
            validation_result['errors'].append(f"HTTP error: {str(e)}")
        except Exception as e:
            validation_result['errors'].append(f"Unexpected error: {str(e)}")
        
        return validation_result
    
    def analyze_content_quality(self, url: str, sample_size: int = 5) -> Dict[str, Any]:
        """Analyze content quality of recent articles"""
        quality_metrics: Dict[str, Any] = {
            'avg_article_length': 0.0,
            'political_relevance_score': 0.0,
            'content_depth_score': 0.0,
            'multimedia_presence': 0.0,
            'analyzed_articles': 0
        }
        
        try:
            # Fetch and parse RSS feed
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            
            if not feed.entries:
                return quality_metrics
            
            # Sample recent articles
            sample_articles = feed.entries[:sample_size]
            article_scores = []
            
            for article in sample_articles:
                try:
                    article_metrics = self.analyze_single_article(article)
                    article_scores.append(article_metrics)
                    quality_metrics['analyzed_articles'] += 1
                except Exception as e:
                    logger.warning(f"Error analyzing article {article.get('link', 'unknown')}: {e}")
                    continue
            
            if article_scores:
                # Calculate averages
                quality_metrics['avg_article_length'] = float(statistics.mean(
                    [score['length'] for score in article_scores]
                ))
                quality_metrics['political_relevance_score'] = float(statistics.mean(
                    [score['political_relevance'] for score in article_scores]
                ))
                quality_metrics['content_depth_score'] = float(statistics.mean(
                    [score['content_depth'] for score in article_scores]
                ))
                quality_metrics['multimedia_presence'] = float(statistics.mean(
                    [score['multimedia'] for score in article_scores]
                ))
        
        except Exception as e:
            logger.error(f"Error analyzing content quality for {url}: {e}")
        
        return quality_metrics
    
    def analyze_single_article(self, article: Any) -> Dict[str, float]:
        """Analyze a single article for quality metrics"""
        metrics: Dict[str, float] = {
            'length': 0.0,
            'political_relevance': 0.0,
            'content_depth': 0.0,
            'multimedia': 0.0
        }
        
        # Get article content
        title = article.get('title', '')
        summary = article.get('summary', '')
        content = title + ' ' + summary
        
        # Remove HTML tags
        clean_content = BeautifulSoup(content, 'html.parser').get_text()
        
        # Calculate length
        metrics['length'] = float(len(clean_content.split()))
        
        # Political relevance score
        political_word_count = sum(1 for word in self.political_keywords 
                                 if word.lower() in clean_content.lower())
        metrics['political_relevance'] = float(min(political_word_count / 10, 1.0))
        
        # Content depth score (based on length and structure)
        if metrics['length'] > 300:
            metrics['content_depth'] = 1.0
        elif metrics['length'] > 150:
            metrics['content_depth'] = 0.7
        elif metrics['length'] > 50:
            metrics['content_depth'] = 0.4
        else:
            metrics['content_depth'] = 0.2
        
        # Multimedia presence
        if 'media_content' in article or 'media_thumbnail' in article:
            metrics['multimedia'] = 1.0
        elif '<img' in content:
            metrics['multimedia'] = 0.5
        
        return metrics
    
    def assess_update_frequency(self, url: str) -> Dict[str, Any]:
        """Assess how frequently a source updates"""
        frequency_metrics: Dict[str, Any] = {
            'updates_per_day': 0.0,
            'consistency_score': 0.0,
            'last_update_hours': None
        }
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            
            if not feed.entries:
                return frequency_metrics
            
            # Analyze publication times
            pub_times = []
            for entry in feed.entries[:20]:  # Check last 20 entries
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_times.append(datetime(*entry.published_parsed[:6]))
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_times.append(datetime(*entry.updated_parsed[:6]))
            
            if len(pub_times) >= 2:
                pub_times.sort(reverse=True)
                
                # Calculate updates per day
                time_span = (pub_times[0] - pub_times[-1]).days
                if time_span > 0:
                    frequency_metrics['updates_per_day'] = float(len(pub_times) / time_span)
                
                # Last update
                frequency_metrics['last_update_hours'] = float((datetime.now() - pub_times[0]).total_seconds() / 3600)
                
                # Consistency score (lower variance = higher consistency)
                intervals = [(pub_times[i] - pub_times[i+1]).total_seconds() 
                           for i in range(len(pub_times)-1)]
                if intervals:
                    variance = statistics.variance(intervals) if len(intervals) > 1 else 0
                    frequency_metrics['consistency_score'] = float(max(0, 1 - (variance / 86400)))  # Normalize by 24 hours
        
        except Exception as e:
            logger.error(f"Error assessing update frequency for {url}: {e}")
        
        return frequency_metrics
    
    def calculate_overall_quality_score(self, source_data: Dict[str, Any], validation_result: Dict[str, Any], 
                                      quality_metrics: Dict[str, Any], frequency_metrics: Dict[str, Any]) -> float:
        """Calculate overall quality score for a source"""
        score = 0.0
        
        # Base score from RSS validation (20%)
        if validation_result['valid_rss']:
            score += 0.2
            
            # Entry count bonus
            if validation_result['entry_count'] > 10:
                score += 0.05
            
            # Freshness bonus
            if validation_result['latest_entry_age'] is not None:
                if validation_result['latest_entry_age'] <= 1:
                    score += 0.1
                elif validation_result['latest_entry_age'] <= 7:
                    score += 0.05
        
        # Content quality score (40%)
        content_score = (
            quality_metrics['political_relevance_score'] * 0.4 +
            quality_metrics['content_depth_score'] * 0.4 +
            quality_metrics['multimedia_presence'] * 0.2
        )
        score += content_score * 0.4
        
        # Update frequency score (20%)
        frequency_score = 0.0
        if frequency_metrics['updates_per_day'] > 0:
            # Optimal frequency is 1-5 updates per day
            if 1 <= frequency_metrics['updates_per_day'] <= 5:
                frequency_score = 1.0
            elif frequency_metrics['updates_per_day'] > 5:
                frequency_score = max(0.5, 1.0 - (frequency_metrics['updates_per_day'] - 5) * 0.1)
            else:
                frequency_score = frequency_metrics['updates_per_day']
        
        score += frequency_score * 0.2
        
        # Source metadata bonus (20%)
        metadata_score = 0.0
        if source_data.get('quality', 0) >= 4:
            metadata_score += 0.5
        if source_data.get('fact_check_rating') == 'high':
            metadata_score += 0.3
        if source_data.get('verification_status') == 'verified':
            metadata_score += 0.2
        
        score += metadata_score * 0.2
        
        return min(score, 1.0)
    
    def validate_source(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single source comprehensively"""
        source_name = source_data.get('name', 'Unknown')
        source_url = source_data.get('url', '')
        
        logger.info(f"Validating source: {source_name}")
        
        # RSS validation
        rss_result = self.validate_rss_feed(source_url)
        
        # Content quality analysis
        quality_result = self.analyze_content_quality(source_url)
        
        # Update frequency assessment
        frequency_result = self.assess_update_frequency(source_url)
        
        # Calculate overall score
        overall_score = self.calculate_overall_quality_score(
            source_data, rss_result, quality_result, frequency_result
        )
        
        # Compile results
        validation_summary = {
            'source_name': source_name,
            'source_url': source_url,
            'source_metadata': source_data,
            'rss_validation': rss_result,
            'content_quality': quality_result,
            'update_frequency': frequency_result,
            'overall_score': overall_score,
            'validation_timestamp': datetime.now().isoformat(),
            'status': 'passed' if overall_score >= 0.6 else 'failed'
        }
        
        return validation_summary
    
    def validate_all_sources(self, max_workers: int = 10) -> Dict[str, Any]:
        """Validate all sources using parallel processing"""
        all_results: Dict[str, Any] = {}
        
        # Flatten sources from all categories
        all_sources = []
        for category, sources in self.sources_data.items():
            for source in sources:
                source['category'] = category
                all_sources.append(source)
        
        logger.info(f"Starting validation of {len(all_sources)} sources")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all validation tasks
            future_to_source = {
                executor.submit(self.validate_source, source): source 
                for source in all_sources
            }
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    result = future.result()
                    all_results[result['source_name']] = result
                except Exception as e:
                    logger.error(f"Error validating {source.get('name', 'Unknown')}: {e}")
                    all_results[source.get('name', 'Unknown')] = {
                        'source_name': source.get('name', 'Unknown'),
                        'status': 'error',
                        'error': str(e)
                    }
        
        return all_results
    
    def generate_validation_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive validation report"""
        report = []
        report.append("# Political Sources Validation Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary statistics
        total_sources = len(results)
        passed_sources = sum(1 for r in results.values() if r.get('status') == 'passed')
        failed_sources = sum(1 for r in results.values() if r.get('status') == 'failed')
        error_sources = sum(1 for r in results.values() if r.get('status') == 'error')
        
        report.append("## Summary")
        report.append(f"- Total Sources: {total_sources}")
        report.append(f"- Passed: {passed_sources} ({passed_sources/total_sources*100:.1f}%)")
        report.append(f"- Failed: {failed_sources} ({failed_sources/total_sources*100:.1f}%)")
        report.append(f"- Errors: {error_sources} ({error_sources/total_sources*100:.1f}%)")
        report.append("")
        
        # Top performing sources
        valid_results = [r for r in results.values() if r.get('overall_score') is not None]
        if valid_results:
            top_sources = sorted(valid_results, key=lambda x: x['overall_score'], reverse=True)[:10]
            
            report.append("## Top 10 Sources by Quality Score")
            for i, source in enumerate(top_sources, 1):
                report.append(f"{i}. {source['source_name']}: {source['overall_score']:.3f}")
            report.append("")
        
        # Sources needing attention
        failed_results = [r for r in results.values() if r.get('status') == 'failed']
        if failed_results:
            report.append("## Sources Requiring Attention")
            for source in failed_results:
                report.append(f"- {source['source_name']}: {source.get('overall_score', 0):.3f}")
                if source.get('rss_validation', {}).get('errors'):
                    for error in source['rss_validation']['errors']:
                        report.append(f"  - {error}")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        if failed_sources > 0:
            report.append(f"1. Remove or replace {failed_sources} failing sources")
        if error_sources > 0:
            report.append(f"2. Investigate {error_sources} sources with validation errors")
        
        avg_score = statistics.mean([r['overall_score'] for r in valid_results]) if valid_results else 0
        report.append(f"3. Current average quality score: {avg_score:.3f}")
        report.append("4. Target quality score: 0.80 or higher")
        
        return "\n".join(report)
    
    def save_results(self, results: Dict[str, Any], filename: str = "political_sources_validation_results.json"):
        """Save validation results to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Results saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")

def main():
    """Main function to run source validation"""
    if not DEPENDENCIES_AVAILABLE:
        print("Error: Required dependencies not installed.")
        print("Please install with: pip install -r requirements_political_sources.txt")
        return
    
    validator = PoliticalSourceValidator()
    
    # Run validation
    results = validator.validate_all_sources()
    
    # Generate and save report
    report = validator.generate_validation_report(results)
    
    # Save results
    validator.save_results(results)
    
    # Save report
    with open("political_sources_validation_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("Validation complete! Check the following files:")
    print("- political_sources_validation_results.json")
    print("- political_sources_validation_report.md")
    print("- political_source_validation.log")

if __name__ == "__main__":
    main()