import feedparser
import json
import random
from bs4 import BeautifulSoup
import time
import re
import os
import requests
import concurrent.futures
from threading import Lock
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import google.generativeai as genai
from google.generativeai import types
from datetime import datetime, timezone
import argparse
from database import db_manager

# Configure the Gemini client
# Make sure to set the GEMINI_API_KEY environment variable
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
    # Per user feedback: Make error about missing API key visible on the frontend.
    print("ERROR:FATAL: GEMINI_API_KEY environment variable not set. Please set it to enable topic generation.", flush=True)
    exit(1)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
]

TIMESTAMP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'last_pull_timestamp.txt')

def get_last_pull_timestamp():
    """Reads the timestamp of the last successful pull."""
    if not os.path.exists(TIMESTAMP_FILE):
        return None
    with open(TIMESTAMP_FILE, 'r') as f:
        try:
            return datetime.fromisoformat(f.read().strip().replace('Z', '+00:00'))
        except ValueError:
            return None

def set_last_pull_timestamp(timestamp):
    """Writes the timestamp of the most recent article to the file."""
    with open(TIMESTAMP_FILE, 'w') as f:
        f.write(timestamp.isoformat())

def get_requests_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        read=3,
        connect=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 503, 504),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def get_source_categories():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '../src/config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_article_details(url):
    session = get_requests_session()
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')
        
        og_image = soup.find('meta', property='og:image')
        image = og_image['content'] if og_image and og_image.get('content') else None

        article_body = soup.find('article') or soup.find('main') or soup.body
        if article_body:
            links = [a['href'] for a in article_body.find_all('a', href=True)]
            
            if not image:
                images = article_body.find_all('img')
                for img in images:
                    if img.get('src'):
                        try:
                            width = int(img.get('width', '0'))
                            height = int(img.get('height', '0'))
                            if width > 300 and height > 150:
                                image = img['src']
                                break
                        except (ValueError, TypeError):
                            continue

            # OPTIMIZATION: Removed expensive text processing. Return None for unused values.
            return None, None, links, image
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️  [DETAILS] Could not fetch article URL {url}: {e}", flush=True)
    except Exception as e:
        print(f"⚠️  [DETAILS] Error processing article {url}: {e}", flush=True)
    
    return None, None, [], None

def find_image(entry, article_image):
    if article_image:
        return article_image
    if 'media_content' in entry and entry.media_content:
        for media in entry.media_content:
            if media.get('medium') == 'image' and 'url' in media:
                return media['url']
    if 'media_thumbnail' in entry and entry.media_thumbnail:
        return entry.media_thumbnail[0]['url']
    
    content_to_check = ""
    if 'summary' in entry:
        content_to_check += entry.summary
    if 'content' in entry:
        for c in entry.content:
            content_to_check += c.value

    if content_to_check:
        soup = BeautifulSoup(content_to_check, 'html.parser')
        img_tag = soup.find('img')
        if img_tag and img_tag.get('src'):
            return img_tag['src']
    
    return f"https://picsum.photos/seed/{random.randint(1, 1000)}/400/300"

def process_source(source_info, category_name, all_articles_lock, all_articles, last_pull_timestamp, ignore_timestamp=False):
    source_name = source_info['name']
    url = source_info['url']
    lang = source_info['lang']
    
    print(f"🌐 [SCRAPING] Starting {source_name} ({lang}) - {url}", flush=True)
    if ignore_timestamp:
        print(f"🕒 [TIMESTAMP] Ignoring timestamp filter - fetching ALL articles", flush=True)
    
    try:
        session = get_requests_session()
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        print(f"📡 [HTTP] Fetching RSS feed for {source_name}...", flush=True)
        response = session.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        print(f"✅ [HTTP] Successfully fetched {source_name} (Status: {response.status_code})", flush=True)
        feed = feedparser.parse(response.content)
        print(f"📋 [RSS] Parsed {len(feed.entries)} entries from {source_name}", flush=True)

        articles_processed = 0
        articles_skipped = 0
        
        for entry in feed.entries:
            print(f"📰 [ARTICLE] Processing: {entry.title[:60]}..." if len(entry.title) > 60 else f"📰 [ARTICLE] Processing: {entry.title}", flush=True)
            
            if source_name == 'Maddyness' and 'intelligence artificielle' not in entry.title.lower() and 'ia' not in entry.title.lower():
                print(f"⏭️  [FILTER] Skipping Maddyness article (not AI-related): {entry.title}", flush=True)
                articles_skipped += 1
                continue
            
            if source_name == 'Chain of Thought' and 'Become a paid subscriber' in entry.description:
                print(f"⏭️  [FILTER] Skipping Chain of Thought paywall article", flush=True)
                articles_skipped += 1
                continue

            published_date = None
            if 'published_parsed' in entry and entry.published_parsed:
                published_date = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', entry.published_parsed)
            elif 'updated_parsed' in entry and entry.updated_parsed:
                published_date = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', entry.updated_parsed)

            if published_date and last_pull_timestamp and not ignore_timestamp:
                article_date = datetime.strptime(published_date, '%Y-%m-%dT%H:%M:%S.000Z').replace(tzinfo=timezone.utc)
                if article_date <= last_pull_timestamp:
                    print(f"⏭️  [TIMESTAMP] Skipping old article from {article_date.strftime('%Y-%m-%d %H:%M')}", flush=True)
                    articles_skipped += 1
                    continue

            # This call is now much more lightweight.
            print(f"🔍 [DETAILS] Fetching article details for: {entry.link}", flush=True)
            _, _, links, article_image = get_article_details(entry.link)
            
            summary = entry.summary if 'summary' in entry else ''

            # OPTIMIZATION: Calculate reading time from summary to avoid costly full-page scrapes.
            summary_text = BeautifulSoup(summary, 'html.parser').get_text()
            words = re.findall(r'\\w+', summary_text)
            word_count = len(words)
            # Heuristic to make reading times more realistic for short summaries
            if word_count > 10 and word_count < 150:
                word_count = word_count + 150
            reading_time = max(1, round(word_count / 200))

            article = {
                'title': entry.title,
                'url': entry.link,
                'source': source_name,
                'source_category': category_name,
                'image': find_image(entry, article_image),
                'date': published_date,
                'reading_time': reading_time,
                'language': lang,
                'links': links,
                'summary': summary, # Keep the original summary for context
            }
            with all_articles_lock:
                all_articles.append(article)
                articles_processed += 1
                print(f"✅ [SAVED] Article saved: {entry.title} (Reading time: {reading_time}min)", flush=True)
                
        print(f"📊 [SUMMARY] {source_name}: {articles_processed} articles processed, {articles_skipped} skipped", flush=True)
        
    except Exception as e:
        print(f"❌ [ERROR] Could not parse feed from {source_name}: {e}", flush=True)

def generate_topics_with_gemini(articles):
    """
    Uses the Gemini API to analyze articles, group them into topics, and generate summaries.
    """
    print(f"\n🧠 [GEMINI] ===== STARTING AI ANALYSIS =====", flush=True)
    print(f"🧠 [GEMINI] Total articles to analyze: {len(articles)}", flush=True)
    
    # Prepare the data for the prompt, providing more context
    print(f"🧠 [GEMINI] Preparing article data for AI analysis...", flush=True)
    prompt_articles = []
    sources_count = {}
    languages_count = {}
    
    for i, article in enumerate(articles):
        # Provide title, source, date, and a snippet of the summary
        snippet = ' '.join(article.get('summary', '').split()[:50])
        prompt_articles.append({
            "url": article["url"],
            "title": article["title"],
            "source": article.get("source", "Unknown"),
            "date": article.get("date", ""),
            "snippet": snippet
        })
        
        # Count sources and languages for analytics
        source = article.get("source", "Unknown")
        lang = article.get("language", "unknown")
        sources_count[source] = sources_count.get(source, 0) + 1
        languages_count[lang] = languages_count.get(lang, 0) + 1
        
        if (i + 1) % 10 == 0:
            print(f"🧠 [GEMINI] Processed {i + 1}/{len(articles)} articles for prompt", flush=True)
    
    print(f"🧠 [GEMINI] Data prepared: {len(prompt_articles)} articles from {len(sources_count)} sources", flush=True)
    print(f"🧠 [GEMINI] Sources distribution: {dict(list(sources_count.items())[:5])}", flush=True)
    print(f"🧠 [GEMINI] Languages: {languages_count}", flush=True)

    prompt = f"""You are an expert AI news analyst. Your task is to analyze articles and intelligently group them into coherent topics.

ANALYSIS RULES:
- Group articles that discuss the same event, product, company announcement, or research breakthrough
- Look for common entities (companies, products, people, technologies) and themes
- Minimum 2 articles per topic, maximum 8 articles per topic
- Prioritize high-impact stories that involve multiple sources covering the same event
- Create 3-10 total topics depending on content diversity

GROUPING CRITERIA:
1. Same company announcements (e.g., OpenAI releases, Google AI updates)
2. Same product/technology (e.g., GPT-4, Claude, specific AI tools)
3. Same regulatory/policy developments (e.g., EU AI Act, AI safety regulations)
4. Same research breakthroughs or scientific papers
5. Same industry events or conferences
6. Same controversy or debate topic

OUTPUT FORMAT - Return only this JSON structure:
{{
  "topics": [
    {{
      "name": "Concise topic title (max 8 words)",
      "summary": "2-3 sentence journalistic summary combining all articles",
      "description": "One compelling sentence describing the topic",
      "article_urls": ["url1", "url2", ...],
      "keywords": ["keyword1", "keyword2", "keyword3"],
      "category": "One of: Corporate, Technology, Research, Ethics, Community"
    }}
  ]
}}

ARTICLES TO ANALYZE:
{json.dumps(prompt_articles[:100], indent=2)}
"""

    print(f"🧠 [GEMINI] Initializing Gemini model: gemini-1.5-flash", flush=True)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt_size = len(prompt)
    print(f"🧠 [GEMINI] Prompt size: {prompt_size} characters ({prompt_size/1000:.1f}K)", flush=True)
    
    try:
        print(f"🧠 [GEMINI] ===== SENDING REQUEST TO GEMINI =====", flush=True)
        print(f"🧠 [GEMINI] Analyzing {len(articles)} articles with Gemini API...", flush=True)
        print(f"🧠 [GEMINI] Request timeout: 120 seconds", flush=True)
        
        start_time = time.time()
        response = model.generate_content(
            prompt,
            request_options={"timeout": 120}
        )
        end_time = time.time()
        
        print(f"🧠 [GEMINI] ✅ Response received in {end_time - start_time:.2f} seconds", flush=True)
        
        if not response.text:
            print("🧠 [GEMINI] ❌ ERROR: Empty response from Gemini", flush=True)
            return []
        
        response_size = len(response.text)
        print(f"🧠 [GEMINI] Response size: {response_size} characters ({response_size/1000:.1f}K)", flush=True)
        print(f"🧠 [GEMINI] ===== GEMINI RAW RESPONSE =====", flush=True)
        print(response.text[:1000] + "..." if len(response.text) > 1000 else response.text, flush=True)
        print(f"🧠 [GEMINI] ===== END RAW RESPONSE =====", flush=True)
        
        # Clean the response to ensure it's valid JSON
        print(f"🧠 [GEMINI] ===== PARSING AI RESPONSE =====", flush=True)
        print(f"🧠 [GEMINI] Cleaning response text for JSON parsing...", flush=True)
        cleaned_response_text = response.text.strip()
        
        # Remove code block markers if present
        if cleaned_response_text.startswith('```'):
            print(f"🧠 [GEMINI] Removing code block markers from response", flush=True)
            cleaned_response_text = re.sub(r'^```[a-z]*\n?', '', cleaned_response_text, flags=re.MULTILINE)
            cleaned_response_text = re.sub(r'\n?```$', '', cleaned_response_text)
        
        # Attempt to find JSON in the response
        json_match = re.search(r'\{.*\}', cleaned_response_text, re.DOTALL)
        if json_match:
            print(f"🧠 [GEMINI] Found JSON block in response", flush=True)
            cleaned_response_text = json_match.group(0)
        
        print(f"🧠 [GEMINI] Parsing JSON response...", flush=True)
        try:
            gemini_result = json.loads(cleaned_response_text)
            print(f"🧠 [GEMINI] ✅ JSON parsed successfully", flush=True)
        except json.JSONDecodeError as e:
            print(f"🧠 [GEMINI] ❌ JSON Parse Error: {e}", flush=True)
            print(f"🧠 [GEMINI] Problematic JSON: {cleaned_response_text[:500]}...", flush=True)
            return []
            
        gemini_topics = gemini_result.get("topics", [])
        
        print(f"🧠 [GEMINI] ===== AI ANALYSIS RESULTS =====", flush=True)
        print(f"🧠 [GEMINI] Found {len(gemini_topics)} topics in Gemini's response", flush=True)
        
        if len(gemini_topics) == 0:
            print("🧠 [GEMINI] ⚠️  WARNING: No topics generated by Gemini", flush=True)
            return []
            
        # Log each topic found
        for i, topic in enumerate(gemini_topics):
            print(f"🧠 [GEMINI] Topic {i+1}: '{topic.get('name', 'Unnamed')}' ({len(topic.get('article_urls', []))} articles)", flush=True)

        # Create the final topic objects by linking back to the original articles
        print(f"🧠 [GEMINI] ===== BUILDING FINAL TOPICS =====", flush=True)
        final_topics = []
        topics_with_articles = 0
        topics_without_articles = 0
        
        for i, gemini_topic in enumerate(gemini_topics):
            print(f"🧠 [GEMINI] Processing topic {i+1}: '{gemini_topic.get('name', 'Unnamed')}'", flush=True)
            
            topic_articles = [
                article for article in articles 
                if article["url"] in gemini_topic.get("article_urls", [])
            ]
            
            print(f"🧠 [GEMINI] Found {len(topic_articles)} matching articles for this topic", flush=True)
            
            if not topic_articles:
                print(f"🧠 [GEMINI] ❌ Skipping topic '{gemini_topic.get('name', 'Unnamed')}' - no matching articles found", flush=True)
                topics_without_articles += 1
                continue

            # Calculate date range for the topic
            dates = [datetime.fromisoformat(article["date"].replace("Z", "+00:00")) for article in topic_articles if article.get("date")]
            min_date = min(dates) if dates else None
            max_date = max(dates) if dates else None

            date_range_str = ""
            if min_date and max_date:
                if min_date.date() == max_date.date():
                    date_range_str = min_date.strftime("%b %d, %Y")
                else:
                    date_range_str = f"{min_date.strftime('%b %d')} - {max_date.strftime('%b %d, %Y')}"

            sources = sorted(list(set(article['source'] for article in topic_articles)))
            print(f"🧠 [GEMINI] Topic sources: {sources}", flush=True)

            topic = {
                "id": f"topic_{i}",
                "name": gemini_topic.get("name", "Unnamed Topic"),
                "summary": gemini_topic.get("summary", ""),
                "description": gemini_topic.get("description", ""),
                "articles": topic_articles,
                "sources": sources,
                "image": topic_articles[0].get('image') if topic_articles else None,
                "keywords": gemini_topic.get("keywords", []),
                "category": gemini_topic.get("category", "General"),
                "date_range": date_range_str,
            }
            final_topics.append(topic)
            topics_with_articles += 1
            print(f"🧠 [GEMINI] ✅ Topic '{topic['name']}' created successfully", flush=True)
            
        print(f"🧠 [GEMINI] ===== FINAL RESULTS =====", flush=True)
        print(f"🧠 [GEMINI] Topics created: {topics_with_articles}", flush=True)
        print(f"🧠 [GEMINI] Topics skipped: {topics_without_articles}", flush=True)
        print(f"🧠 [GEMINI] ===== AI ANALYSIS COMPLETE =====", flush=True)
        
        return final_topics

    except Exception as e:
        # Per user feedback: Send a specific error to the frontend
        print(f"🧠 [GEMINI] ❌ CRITICAL ERROR: {e}", flush=True)
        print(f"🧠 [GEMINI] Error type: {type(e).__name__}", flush=True)
        print(f"🧠 [GEMINI] ===== RAW RESPONSE (if available) =====", flush=True)
        print(response.text if 'response' in locals() else "No response received.", flush=True)
        print(f"🧠 [GEMINI] ===== END ERROR DETAILS =====", flush=True)
        return []

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AI News Scraper with Gemini-powered topic generation')
    parser.add_argument('--all', action='store_true', 
                        help='Fetch ALL articles, ignoring timestamp filter (for development/testing)')
    parser.add_argument('--reset-timestamp', action='store_true',
                        help='Reset the timestamp file before scraping')
    args = parser.parse_args()
    
    print(f"🚀 [SCRAPER] ===== STARTING AI NEWS SCRAPER =====", flush=True)
    print(f"🚀 [SCRAPER] Loading source configurations...", flush=True)
    
    # Reset timestamp if requested
    if args.reset_timestamp:
        print(f"🕒 [TIMESTAMP] Resetting timestamp file...", flush=True)
        if os.path.exists(TIMESTAMP_FILE):
            os.remove(TIMESTAMP_FILE)
        print(f"🕒 [TIMESTAMP] ✅ Timestamp file reset", flush=True)
    
    source_categories = get_source_categories()
    last_pull_timestamp = get_last_pull_timestamp() if not args.all else None
    
    if args.all:
        print(f"🚀 [SCRAPER] Mode: FETCH ALL ARTICLES (ignoring timestamp)", flush=True)
        print(f"🚀 [SCRAPER] Last pull timestamp: IGNORED", flush=True)
    else:
        print(f"🚀 [SCRAPER] Mode: FETCH NEW ARTICLES ONLY", flush=True)
        print(f"🚀 [SCRAPER] Last pull timestamp: {last_pull_timestamp}", flush=True)
    
    print(f"🚀 [SCRAPER] Source categories: {list(source_categories.keys())}", flush=True)

    tasks = []
    for category_name, sources in source_categories.items():
        print(f"🚀 [SCRAPER] Category '{category_name}': {len(sources)} sources", flush=True)
        for source_info in sources:
            tasks.append({'source_info': source_info, 'category_name': category_name})

    total_sources = len(tasks)
    processed_sources = 0
    all_articles = []
    all_articles_lock = Lock()
    
    print(f"🚀 [SCRAPER] ===== STARTING PARALLEL SCRAPING =====", flush=True)
    print(f"🚀 [SCRAPER] Total sources to process: {total_sources}", flush=True)
    print(f"🚀 [SCRAPER] Max workers: 20", flush=True)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_task = {executor.submit(process_source, task['source_info'], task['category_name'], all_articles_lock, all_articles, last_pull_timestamp, args.all): task for task in tasks}
        
        for future in concurrent.futures.as_completed(future_to_task, timeout=300):
            task = future_to_task[future]
            source_name = task['source_info']['name']
            try:
                future.result() 
            except Exception as e:
                print(f"Error processing {source_name}: {e}", flush=True)
            
            processed_sources += 1
            progress = (processed_sources / total_sources) * 100
            print(f"PROGRESS:{progress:.2f}:{source_name}", flush=True)

    print(f"🚀 [SCRAPER] ===== SCRAPING COMPLETE =====", flush=True)
    print(f"🚀 [SCRAPER] Total articles collected: {len(all_articles)}", flush=True)
    print(f"🚀 [SCRAPER] Running duplicate detection...", flush=True)
    
    unique_articles = []
    seen_titles = set()
    duplicates_removed = 0
    
    for article in all_articles:
        if article['title'] not in seen_titles:
            unique_articles.append(article)
            seen_titles.add(article['title'])
        else:
            duplicates_removed += 1

    print(f"🚀 [SCRAPER] Unique articles: {len(unique_articles)}", flush=True)
    print(f"🚀 [SCRAPER] Duplicates removed: {duplicates_removed}", flush=True)

    if not unique_articles:
        print(f"🚀 [SCRAPER] ❌ No new articles found since last pull. Exiting.", flush=True)
        return

    print(f"🚀 [SCRAPER] ===== PREPARING FOR AI ANALYSIS =====", flush=True)
    print(f"🚀 [SCRAPER] Sending {len(unique_articles)} unique articles to Gemini...", flush=True)

    # Generate topics using Gemini
    topics = generate_topics_with_gemini(unique_articles)
    print(f"🚀 [SCRAPER] ===== AI ANALYSIS RESULTS =====", flush=True)
    print(f"🚀 [SCRAPER] Generated {len(topics)} topics from {len(unique_articles)} articles", flush=True)

    # Store data in database
    print(f"🚀 [SCRAPER] ===== STORING IN DATABASE =====", flush=True)
    
    # Calculate some statistics
    total_sources = len(set(article['source'] for article in unique_articles))
    languages = set(article['language'] for article in unique_articles)
    
    print(f"🚀 [SCRAPER] ===== FINAL STATISTICS =====", flush=True)
    print(f"🚀 [SCRAPER] Total articles: {len(unique_articles)}", flush=True)
    print(f"🚀 [SCRAPER] Total sources: {total_sources}", flush=True)
    print(f"🚀 [SCRAPER] Languages: {languages}", flush=True)
    print(f"🚀 [SCRAPER] Topics generated: {len(topics)}", flush=True)

    # Store articles and topics in database
    try:
        print(f"🗄️  [DB] Storing {len(unique_articles)} articles and {len(topics)} topics in database...", flush=True)
        db_manager.store_articles_and_topics(unique_articles, topics)
        
        # Also keep the JSON file for backward compatibility (frontend migration)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, '../src/data.js')
        output_data = {
            "articles": unique_articles,
            "topics": topics
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("export const newsData = ")
            json.dump(output_data, f, indent=4, ensure_ascii=False)
            f.write(";")
        
        file_size = os.path.getsize(output_path) / 1024  # KB
        print(f"🗄️  [DB] ✅ Data stored in database successfully", flush=True)
        print(f"📄 [JSON] ✅ Backup JSON file written ({file_size:.1f} KB)", flush=True)
        
    except Exception as e:
        print(f"🗄️  [DB] ❌ Database storage error: {e}", flush=True)
        # Fallback to JSON file only
        print(f"🗄️  [DB] Falling back to JSON file storage", flush=True)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, '../src/data.js')
        output_data = {
            "articles": unique_articles,
            "topics": topics
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("export const newsData = ")
            json.dump(output_data, f, indent=4, ensure_ascii=False)
            f.write(";")
        
        file_size = os.path.getsize(output_path) / 1024  # KB
        print(f"📄 [JSON] ✅ JSON file written successfully ({file_size:.1f} KB)", flush=True)

    if unique_articles and not args.all:
        latest_article_date = max(
            datetime.strptime(a['date'], '%Y-%m-%dT%H:%M:%S.000Z').replace(tzinfo=timezone.utc) 
            for a in unique_articles if a.get('date')
        )
        print(f"🚀 [SCRAPER] Latest article date: {latest_article_date.isoformat()}", flush=True)
        set_last_pull_timestamp(latest_article_date)
        print(f"🚀 [SCRAPER] ✅ Updated last pull timestamp", flush=True)
    elif args.all:
        print(f"🚀 [SCRAPER] ⚠️  Skipping timestamp update (--all mode)", flush=True)

    print(f"🚀 [SCRAPER] ===== SCRAPER COMPLETE =====", flush=True)
    print(f"🚀 [SCRAPER] 🎉 AI News scraping and analysis finished!", flush=True)

if __name__ == "__main__":
    main() 