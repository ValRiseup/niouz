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
from datetime import datetime, timezone
import argparse
from database import db_manager

# Configure the Gemini client
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
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
    
    print(f"🌐 [POLITIQUE] Starting {source_name} ({lang}) - {url}", flush=True)
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

            print(f"🔍 [DETAILS] Fetching article details for: {entry.link}", flush=True)
            _, _, links, article_image = get_article_details(entry.link)
            
            summary = entry.summary if 'summary' in entry else ''

            summary_text = BeautifulSoup(summary, 'html.parser').get_text()
            words = re.findall(r'\\w+', summary_text)
            word_count = len(words)
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
                'summary': summary,
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
    Uses the Gemini API to analyze political articles, group them into topics, and generate summaries.
    """
    print(f"\n🧠 [GEMINI] ===== STARTING POLITICAL ANALYSIS =====", flush=True)
    print(f"🧠 [GEMINI] Total articles to analyze: {len(articles)}", flush=True)
    
    print(f"🧠 [GEMINI] Preparing article data for political analysis...", flush=True)
    prompt_articles = []
    sources_count = {}
    languages_count = {}
    
    for i, article in enumerate(articles):
        snippet = ' '.join(article.get('summary', '').split()[:50])
        prompt_articles.append({
            "url": article["url"],
            "title": article["title"],
            "source": article.get("source", "Unknown"),
            "date": article.get("date", ""),
            "snippet": snippet
        })
        
        source = article.get("source", "Unknown")
        lang = article.get("language", "unknown")
        sources_count[source] = sources_count.get(source, 0) + 1
        languages_count[lang] = languages_count.get(lang, 0) + 1
        
        if (i + 1) % 10 == 0:
            print(f"🧠 [GEMINI] Processed {i + 1}/{len(articles)} articles for prompt", flush=True)
    
    print(f"🧠 [GEMINI] Data prepared: {len(prompt_articles)} articles from {len(sources_count)} sources", flush=True)

    prompt = f"""Tu es un expert analyste politique et journaliste. Ta tâche est d'analyser des articles d'actualité politique et de les regrouper intelligemment en sujets politiques cohérents.

RÈGLES D'ANALYSE POUR L'ACTUALITÉ POLITIQUE :
- Regroupe les articles qui traitent du même événement politique, annonce, scandale ou développement de politique publique
- Recherche les entités politiques communes (politiciens, partis, institutions, lois) et les thèmes
- Minimum 2 articles par sujet, maximum 8 articles par sujet
- Priorise les histoires à fort impact couvertes par plusieurs sources
- Crée 3-10 sujets au total selon la diversité du contenu

CRITÈRES DE REGROUPEMENT POLITIQUE :
1. Même personnalité politique (discours, controverses, nominations)
2. Même parti politique ou coalition (stratégies, conflits internes, annonces)
3. Même politique ou législation (lois, réformes, changements réglementaires)
4. Même scandale ou controverse politique (enquêtes, procédures judiciaires)
5. Même élection ou processus électoral (campagnes, résultats, analyses)
6. Même décision institutionnelle (parlement, gouvernement, tribunaux)
7. Même événement de relations internationales ou de diplomatie
8. Même débat de politique sociale ou économique

FORMAT DE SORTIE - Retourne uniquement cette structure JSON :
{{
  "topics": [
    {{
      "name": "Titre politique concis (max 8 mots)",
      "summary": "Résumé journalistique de 2-3 phrases combinant tous les articles avec contexte politique",
      "description": "Une phrase captivante décrivant la signification politique",
      "article_urls": ["url1", "url2", ...],
      "keywords": ["nom_politicien", "parti", "domaine_politique"],
      "category": "Un parmi : National, International, Elections, Politique, Scandale, Parlement"
    }}
  ]
}}

ARTICLES POLITIQUES À ANALYSER :
{json.dumps(prompt_articles[:100], indent=2)}
"""

    print(f"🧠 [GEMINI] Initializing Gemini model for political analysis: gemini-1.5-flash", flush=True)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    try:
        print(f"🧠 [GEMINI] ===== ENVOI DE LA DEMANDE D'ANALYSE POLITIQUE =====", flush=True)
        
        start_time = time.time()
        response = model.generate_content(
            prompt,
            request_options={"timeout": 120}
        )
        end_time = time.time()
        
        print(f"🧠 [GEMINI] ✅ Analyse politique terminée en {end_time - start_time:.2f} secondes", flush=True)
        
        if not response.text:
            print("🧠 [GEMINI] ❌ ERROR: Empty response from Gemini", flush=True)
            return []
        
        print(f"🧠 [GEMINI] ===== RÉPONSE D'ANALYSE POLITIQUE GEMINI =====", flush=True)
        print(response.text[:1000] + "..." if len(response.text) > 1000 else response.text, flush=True)
        
        cleaned_response_text = response.text.strip()
        
        if cleaned_response_text.startswith('```'):
            print(f"🧠 [GEMINI] Removing code block markers from response", flush=True)
            cleaned_response_text = re.sub(r'^```[a-z]*\n?', '', cleaned_response_text, flags=re.MULTILINE)
            cleaned_response_text = re.sub(r'\n?```$', '', cleaned_response_text)
        
        json_match = re.search(r'\{.*\}', cleaned_response_text, re.DOTALL)
        if json_match:
            cleaned_response_text = json_match.group(0)
        
        try:
            gemini_result = json.loads(cleaned_response_text)
            print(f"🧠 [GEMINI] ✅ JSON d'analyse politique analysé avec succès", flush=True)
        except json.JSONDecodeError as e:
            print(f"🧠 [GEMINI] ❌ JSON Parse Error: {e}", flush=True)
            return []
            
        gemini_topics = gemini_result.get("topics", [])
        
        print(f"🧠 [GEMINI] Trouvé {len(gemini_topics)} sujets politiques", flush=True)
        
        if len(gemini_topics) == 0:
            return []

        final_topics = []
        topics_with_articles = 0
        
        for i, gemini_topic in enumerate(gemini_topics):
            topic_articles = [
                article for article in articles 
                if article["url"] in gemini_topic.get("article_urls", [])
            ]
            
            if not topic_articles:
                continue

            dates = [datetime.fromisoformat(article["date"].replace("Z", "+00:00")) for article in topic_articles if article.get("date")]
            min_date = min(dates) if dates else None
            max_date = max(dates) if dates else None

            date_range_str = ""
            if min_date and max_date:
                if min_date.date() == max_date.date():
                    date_range_str = min_date.strftime("%d %b %Y")
                else:
                    date_range_str = f"{min_date.strftime('%d %b')} - {max_date.strftime('%d %b %Y')}"

            sources = sorted(list(set(article['source'] for article in topic_articles)))

            topic = {
                "id": f"politics_topic_{i}",
                "name": gemini_topic.get("name", "Sujet Politique"),
                "summary": gemini_topic.get("summary", ""),
                "description": gemini_topic.get("description", ""),
                "articles": topic_articles,
                "sources": sources,
                "image": topic_articles[0].get('image') if topic_articles else None,
                "keywords": gemini_topic.get("keywords", []),
                "category": gemini_topic.get("category", "National"),
                "date_range": date_range_str,
            }
            final_topics.append(topic)
            topics_with_articles += 1
            
        print(f"🧠 [GEMINI] ===== ANALYSE POLITIQUE TERMINÉE =====", flush=True)
        print(f"🧠 [GEMINI] Sujets politiques créés : {topics_with_articles}", flush=True)
        
        return final_topics

    except Exception as e:
        print(f"🧠 [GEMINI] ❌ ERREUR CRITIQUE : {e}", flush=True)
        return []

def main():
    parser = argparse.ArgumentParser(description='Political News Scraper with Gemini-powered topic generation')
    parser.add_argument('--all', action='store_true', 
                        help='Fetch ALL articles, ignoring timestamp filter (for development/testing)')
    parser.add_argument('--reset-timestamp', action='store_true',
                        help='Reset the timestamp file before scraping')
    args = parser.parse_args()
    
    print(f"🚀 [SCRAPER] ===== DÉMARRAGE DU SCRAPER POLITIQUE =====", flush=True)
    
    if args.reset_timestamp:
        print(f"🕒 [TIMESTAMP] Resetting timestamp file...", flush=True)
        if os.path.exists(TIMESTAMP_FILE):
            os.remove(TIMESTAMP_FILE)
    
    source_categories = get_source_categories()
    last_pull_timestamp = get_last_pull_timestamp() if not args.all else None
    
    if args.all:
        print(f"🚀 [SCRAPER] Mode: RÉCUPÉRATION DE TOUS LES ARTICLES POLITIQUES", flush=True)
    else:
        print(f"🚀 [SCRAPER] Mode: NOUVEAUX ARTICLES POLITIQUES SEULEMENT", flush=True)
        print(f"🚀 [SCRAPER] Last pull timestamp: {last_pull_timestamp}", flush=True)
    
    tasks = []
    for category_name, sources in source_categories.items():
        for source_info in sources:
            tasks.append({'source_info': source_info, 'category_name': category_name})

    all_articles = []
    all_articles_lock = Lock()
    
    print(f"🚀 [SCRAPER] Démarrage du scraping politique parallèle : {len(tasks)} sources", flush=True)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_task = {executor.submit(process_source, task['source_info'], task['category_name'], all_articles_lock, all_articles, last_pull_timestamp, args.all): task for task in tasks}
        
        processed_sources = 0
        for future in concurrent.futures.as_completed(future_to_task, timeout=300):
            processed_sources += 1
            progress = (processed_sources / len(tasks)) * 100
            print(f"PROGRESS:{progress:.2f}:Sources Politiques", flush=True)

    print(f"🚀 [SCRAPER] Scraping politique terminé : {len(all_articles)} articles collectés", flush=True)
    
    # Remove duplicates
    unique_articles = []
    seen_titles = set()
    for article in all_articles:
        if article['title'] not in seen_titles:
            unique_articles.append(article)
            seen_titles.add(article['title'])

    print(f"🚀 [SCRAPER] Articles politiques uniques : {len(unique_articles)}", flush=True)

    if unique_articles:
        most_recent_date = max(
            datetime.fromisoformat(article["date"].replace("Z", "+00:00")) 
            for article in unique_articles if article.get("date")
        )
        set_last_pull_timestamp(most_recent_date)
        
        print(f"🧠 [GEMINI] Début de la génération de sujets politiques avec {len(unique_articles)} articles...", flush=True)
        topics = generate_topics_with_gemini(unique_articles)
        
        # Save all data
        db_manager.save_articles(unique_articles)
        db_manager.save_topics(topics)
        
        # Generate data.js for frontend
        data_js_content = f"""// Generated political news data - {datetime.now().isoformat()}
export const newsData = {json.dumps(unique_articles, indent=2, ensure_ascii=False)};

export const topicsData = {json.dumps(topics, indent=2, ensure_ascii=False)};

export const lastUpdated = "{datetime.now().isoformat()}";
"""
        
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../src/data.js')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(data_js_content)
        
        print(f"✅ [TERMINÉ] Analyse des actualités politiques terminée !", flush=True)
        print(f"✅ [TERMINÉ] Sujets : {len(topics)}, Articles : {len(unique_articles)}", flush=True)

if __name__ == "__main__":
    main() 