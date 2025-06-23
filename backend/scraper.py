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

def get_source_categories():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '../src/config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_image_from_url(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']
            
        article_body = soup.find('article') or soup.find('main') or soup.body
        if article_body:
            images = article_body.find_all('img')
            for img in images:
                if img.get('src'):
                    try:
                        width = int(img.get('width', '0'))
                        height = int(img.get('height', '0'))
                        if width > 300 and height > 150:
                            return img['src']
                    except (ValueError, TypeError):
                        continue
        
    except requests.exceptions.RequestException as e:
        print(f"Could not fetch article URL {url}: {e}", flush=True)
    return None

def find_image(entry):
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
    
    if entry.link:
        image_from_url = get_image_from_url(entry.link)
        if image_from_url:
            return image_from_url
            
    return f"https://picsum.photos/seed/{random.randint(1, 1000)}/400/300"

def get_reading_time(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        article_body = soup.find('article') or soup.find('main') or soup.body
        if article_body:
            for element in article_body(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            text = article_body.get_text(separator=' ', strip=True)
            words = re.findall(r'\w+', text)
            word_count = len(words)
            reading_time = round(word_count / 200)
            return max(1, reading_time)

    except requests.exceptions.RequestException as e:
        print(f"Could not fetch article URL {url} for reading time: {e}", flush=True)
    
    return None

def process_source(source_info, category_name, all_articles_lock, all_articles):
    source_name = source_info['name']
    url = source_info['url']
    lang = source_info['lang']
    
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:7]:
            if source_name == 'Maddyness' and 'intelligence artificielle' not in entry.title.lower() and 'ia' not in entry.title.lower():
                continue
            
            published_date = None
            if 'published_parsed' in entry and entry.published_parsed:
                published_date = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', entry.published_parsed)
            elif 'updated_parsed' in entry and entry.updated_parsed:
                published_date = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', entry.updated_parsed)

            article = {
                'title': entry.title,
                'url': entry.link,
                'source': source_name,
                'source_category': category_name,
                'image': find_image(entry),
                'date': published_date,
                'reading_time': get_reading_time(entry.link),
                'language': lang,
                'category': random.choice(['daily', 'trending', 'global'])
            }
            with all_articles_lock:
                all_articles.append(article)
    except Exception as e:
        print(f"Could not parse feed from {source_name}: {e}", flush=True)

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
        
        for future in concurrent.futures.as_completed(future_to_task):
            task = future_to_task[future]
            source_name = task['source_info']['name']
            try:
                future.result() 
            except Exception as e:
                print(f"Error processing {source_name}: {e}", flush=True)
            
            processed_sources += 1
            progress = (processed_sources / total_sources) * 100
            print(f"PROGRESS:{progress:.2f}:{source_name}", flush=True)

    # Remove duplicates
    seen_titles = set()
    unique_articles = []
    for article in all_articles:
        if article['title'] not in seen_titles:
            unique_articles.append(article)
            seen_titles.add(article['title'])

    print(f"\nFound {len(unique_articles)} unique articles in total.")

    # Determine the output path relative to the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, '../src/data.js')


    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("export const newsData = ")
        json.dump(unique_articles, f, indent=4, ensure_ascii=False)
        f.write(";")
    
    print(f"\nSuccessfully created {output_path}")

if __name__ == "__main__":
    main() 