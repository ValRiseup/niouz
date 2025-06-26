#!/usr/bin/env python3

"""
Script de test rapide pour le développement
Ne scrape que quelques sources sélectionnées pour tester rapidement
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import (
    get_source_categories, process_source, generate_topics_with_gemini,
    get_requests_session
)
from threading import Lock
import json
from datetime import datetime, timezone

def main():
    print("🧪 [TEST] ===== TEST RAPIDE DU SCRAPER =====")
    
    # Sources de test (limitées pour rapidité)
    test_sources = [
        {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "lang": "en"},
        {"name": "ActuIA", "url": "https://www.actuia.com/feed/", "lang": "fr"},
        {"name": "The Decoder", "url": "https://the-decoder.com/feed/", "lang": "en"},
    ]
    
    all_articles = []
    all_articles_lock = Lock()
    
    print(f"🧪 [TEST] Scraping {len(test_sources)} sources de test...")
    
    # Scraper les sources de test (sans filtrage timestamp)
    for source_info in test_sources:
        print(f"🧪 [TEST] Processing {source_info['name']}...")
        try:
            process_source(source_info, "Test", all_articles_lock, all_articles, None, ignore_timestamp=True)
        except Exception as e:
            print(f"🧪 [TEST] ❌ Error with {source_info['name']}: {e}")
    
    print(f"🧪 [TEST] Collected {len(all_articles)} articles total")
    
    if len(all_articles) < 2:
        print("🧪 [TEST] ⚠️ Not enough articles for topic generation (minimum 2)")
        return
    
    # Limiter à 20 articles max pour test rapide
    test_articles = all_articles[:20]
    print(f"🧪 [TEST] Using {len(test_articles)} articles for topic generation")
    
    # Générer des sujets avec Gemini
    print("🧪 [TEST] Generating topics with Gemini...")
    topics = generate_topics_with_gemini(test_articles)
    
    print(f"🧪 [TEST] Generated {len(topics)} topics")
    for i, topic in enumerate(topics):
        print(f"🧪 [TEST] Topic {i+1}: '{topic['name']}' ({len(topic['articles'])} articles)")
    
    # Sauvegarder les résultats de test
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, '../src/data.js')
    
    output_data = {
        "articles": test_articles,
        "topics": topics
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("export const newsData = ")
        json.dump(output_data, f, indent=4, ensure_ascii=False)
        f.write(";")
    
    print(f"🧪 [TEST] ✅ Test results saved to {output_path}")
    print(f"🧪 [TEST] 🎉 Test complete! Run 'npm run dev' to see results")

if __name__ == "__main__":
    main() 