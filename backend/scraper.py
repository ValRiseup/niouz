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
from datetime import datetime

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
        print(f"Could not fetch article URL {url}: {e}", flush=True)
    
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

def process_source(source_info, category_name, all_articles_lock, all_articles):
    source_name = source_info['name']
    url = source_info['url']
    lang = source_info['lang']
    
    try:
        session = get_requests_session()
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        response = session.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        feed = feedparser.parse(response.content)

        for entry in feed.entries:
            if source_name == 'Maddyness' and 'intelligence artificielle' not in entry.title.lower() and 'ia' not in entry.title.lower():
                continue
            
            if source_name == 'Chain of Thought' and 'Become a paid subscriber' in entry.description:
                continue

            published_date = None
            if 'published_parsed' in entry and entry.published_parsed:
                published_date = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', entry.published_parsed)
            elif 'updated_parsed' in entry and entry.updated_parsed:
                published_date = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', entry.updated_parsed)

            # This call is now much more lightweight.
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
    except Exception as e:
        print(f"Could not parse feed from {source_name}: {e}", flush=True)

def generate_topics_with_gemini(articles):
    """
    Uses the Gemini API to analyze articles, group them into topics, and generate summaries.
    """
    print("\n--- Sending articles to Gemini for analysis... ---", flush=True)
    
    # Prepare the data for the prompt, keeping it concise
    prompt_articles = []
    for article in articles:
        # Provide title and a snippet of the summary
        snippet = ' '.join(article.get('summary', '').split()[:100])
        prompt_articles.append({
            "url": article["url"],
            "title": article["title"],
            "snippet": snippet
        })

    prompt = f"""
    You are an expert news analyst specializing in the AI industry. I will provide you with a list of recent news articles.
    Your task is to analyze these articles and group them into distinct topics. A topic should be about a closely related subject, such as a specific product release, a major corporate announcement, or a significant research trend.

    Your goal is to find a good balance between creating specific, high-quality topics and ensuring good coverage of the provided articles. If an article doesn't fit into a clear group, it's better to leave it out than to create a messy, unfocused topic.

    For each topic you identify, you must provide the following information in a structured format:
    1. `name`: A short, catchy, descriptive headline for the topic, under 8 words.
    2. `summary`: A 2-3 sentence neutral, journalistic summary synthesizing the key information from all articles in the group.
    3. `description`: A single, compelling sentence that encapsulates the core of the topic.
    4. `article_urls`: A list of all the URLs of the articles belonging to this topic.
    5. `keywords`: A list of 3-5 relevant keywords or technical terms for this topic (e.g., ["LLM", "AGI", "RAG", "Prompt Engineering"]).
    6. `category`: Assign a single category from this list: ["Corporate", "Technology", "Research", "Ethics", "Community"].

    Your final output must be a single, valid JSON object with a key "topics", which contains a list of the topic objects you have identified.
    Do not include any text, markdown, or formatting outside of this single JSON object.

    Here are the articles:
    {json.dumps(prompt_articles, indent=2)}
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    
    try:
        print("PROGRESS:100:Analyzing with Gemini...", flush=True)
        response = model.generate_content(
            prompt,
            request_options={"timeout": 120} # 2 minute timeout (reduced from 5)
        )
        
        print("\n--- Gemini raw response text: ---", flush=True)
        print(response.text, flush=True)
        
        # Clean the response to ensure it's valid JSON
        print("PROGRESS:100:Parsing Gemini response...", flush=True)
        cleaned_response_text = response.text.strip().replace('```json', '').replace('```', '')
        
        gemini_result = json.loads(cleaned_response_text)
        gemini_topics = gemini_result.get("topics", [])
        
        print(f"--- Found {len(gemini_topics)} topics in Gemini's response. ---", flush=True)

        # Create the final topic objects by linking back to the original articles
        final_topics = []
        for i, gemini_topic in enumerate(gemini_topics):
            topic_articles = [
                article for article in articles 
                if article["url"] in gemini_topic.get("article_urls", [])
            ]
            
            if not topic_articles:
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

            topic = {
                "id": f"topic_{i}",
                "name": gemini_topic.get("name", "Unnamed Topic"),
                "summary": gemini_topic.get("summary", ""),
                "description": gemini_topic.get("description", ""),
                "articles": topic_articles,
                "sources": sorted(list(set(article['source'] for article in topic_articles))),
                "image": topic_articles[0].get('image') if topic_articles else None,
                "keywords": gemini_topic.get("keywords", []),
                "category": gemini_topic.get("category", "General"),
                "date_range": date_range_str,
            }
            final_topics.append(topic)
            
        return final_topics

    except Exception as e:
        # Per user feedback: Send a specific error to the frontend
        print(f"\nERROR:Gemini API Error: {e}", flush=True)
        print("--- Gemini raw response was: ---", flush=True)
        print(response.text if 'response' in locals() else "No response received.", flush=True)
        return []

def main():
    source_categories = get_source_categories()

    tasks = []
    for category_name, sources in source_categories.items():
        for source_info in sources:
            tasks.append({'source_info': source_info, 'category_name': category_name})

    total_sources = len(tasks)
    processed_sources = 0
    all_articles = []
    all_articles_lock = Lock()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_task = {executor.submit(process_source, task['source_info'], task['category_name'], all_articles_lock, all_articles): task for task in tasks}
        
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

    print("\n--- All articles fetched. Running simple duplicate detection for debugging... ---", flush=True)
    unique_articles = []
    seen_titles = set()
    for article in all_articles:
        if article['title'] not in seen_titles:
            unique_articles.append(article)
            seen_titles.add(article['title'])

    print(f"\nFound {len(unique_articles)} unique articles in total.")

    # Generate topics using Gemini
    topics = generate_topics_with_gemini(unique_articles)
    print(f"\nFound {len(topics)} topics from {len(unique_articles)} articles using Gemini.")

    # Determine the output path relative to the script's location
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
    
    print(f"\nSuccessfully created {output_path}")

if __name__ == "__main__":
    main() 