#!/usr/bin/env python3
"""
Script d'exemple pour tester la plateforme politique sans clé API Gemini
Génère des données d'exemple pour démonstration
"""

import json
import os
from datetime import datetime

def generate_sample_data():
    """Génère des données d'exemple pour la plateforme politique"""
    
    # Articles d'exemple
    sample_articles = [
        {
            "title": "Réforme des retraites : manifestations dans toute la France",
            "url": "https://example.com/reforme-retraites-manifestations",
            "source": "Le Figaro Politique",
            "source_category": "Politique France",
            "image": "https://picsum.photos/400/200?random=10",
            "date": "2024-01-20T09:30:00.000Z",
            "reading_time": 5,
            "language": "fr",
            "summary": "Des millions de Français descendent dans la rue pour protester contre la réforme des retraites proposée par le gouvernement. Les syndicats appellent à une grève générale.",
            "links": []
        },
        {
            "title": "Macron défend sa politique européenne à Bruxelles",
            "url": "https://example.com/macron-europe-bruxelles",
            "source": "Le Monde Politique",
            "source_category": "Europe & UE",
            "image": "https://picsum.photos/400/200?random=11",
            "date": "2024-01-20T11:15:00.000Z",
            "reading_time": 4,
            "language": "fr",
            "summary": "Le président français présente sa vision de l'Europe lors d'un discours devant le Parlement européen, insistant sur la souveraineté stratégique.",
            "links": []
        },
        {
            "title": "Trump leads in Republican primary polls",
            "url": "https://example.com/trump-republican-polls",
            "source": "CNN Politics",
            "source_category": "Politique Internationale",
            "image": "https://picsum.photos/400/200?random=12",
            "date": "2024-01-20T13:45:00.000Z",
            "reading_time": 3,
            "language": "en",
            "summary": "Former President Donald Trump maintains his lead in Republican primary polls ahead of the 2024 presidential election, despite ongoing legal challenges.",
            "links": []
        },
        {
            "title": "Budget 2024 : tensions au sein de la majorité",
            "url": "https://example.com/budget-2024-tensions",
            "source": "Libération Politique",
            "source_category": "Politique France",
            "image": "https://picsum.photos/400/200?random=13",
            "date": "2024-01-20T15:20:00.000Z",
            "reading_time": 6,
            "language": "fr",
            "summary": "Les débats autour du budget 2024 révèlent des fractures au sein de la majorité présidentielle, notamment sur les questions fiscales.",
            "links": []
        },
        {
            "title": "Sondage IFOP : intentions de vote pour les européennes",
            "url": "https://example.com/sondage-ifop-europeennes",
            "source": "IFOP",
            "source_category": "Sondages & Data",
            "image": "https://picsum.photos/400/200?random=14",
            "date": "2024-01-20T17:00:00.000Z",
            "reading_time": 4,
            "language": "fr",
            "summary": "Le dernier sondage IFOP révèle une progression de la liste Renaissance pour les élections européennes, mais le RN reste en tête des intentions de vote.",
            "links": []
        }
    ]
    
    # Sujets d'exemple (topics générés par IA simulée)
    sample_topics = [
        {
            "id": "politics_topic_0",
            "name": "Réforme des Retraites : Mobilisation Nationale",
            "summary": "Le gouvernement français fait face à une forte mobilisation sociale contre sa réforme des retraites. Les syndicats organisent des manifestations nationales et appellent à la grève générale pour s'opposer au recul de l'âge légal de départ à la retraite.",
            "description": "Crise sociale majeure autour de la réforme du système de retraites",
            "articles": [sample_articles[0], sample_articles[3]],
            "sources": ["Le Figaro Politique", "Libération Politique", "BFM Politique"],
            "image": "https://picsum.photos/400/200?random=10",
            "keywords": ["retraites", "réforme", "manifestations", "syndicats", "grève"],
            "category": "National",
            "date_range": "20 jan 2024"
        },
        {
            "id": "politics_topic_1",
            "name": "Europe : Vision Française de Macron",
            "summary": "Emmanuel Macron présente sa stratégie européenne lors d'un déplacement à Bruxelles, mettant l'accent sur l'autonomie stratégique et la souveraineté européenne face aux défis géopolitiques mondiaux.",
            "description": "Diplomatie européenne et positionnement français sur la scène continentale",
            "articles": [sample_articles[1]],
            "sources": ["Le Monde Politique", "Euronews Politique"],
            "image": "https://picsum.photos/400/200?random=11",
            "keywords": ["Macron", "Europe", "souveraineté", "Bruxelles", "diplomatie"],
            "category": "International",
            "date_range": "20 jan 2024"
        },
        {
            "id": "politics_topic_2",
            "name": "Élections Européennes : Dynamiques Politiques",
            "summary": "À quelques mois des élections européennes, les derniers sondages révèlent les dynamiques politiques françaises. Le RN maintient sa position de tête while Renaissance progresse dans les intentions de vote.",
            "description": "Course électorale pour les européennes 2024 en France",
            "articles": [sample_articles[4]],
            "sources": ["IFOP", "OpinionWay"],
            "image": "https://picsum.photos/400/200?random=14",
            "keywords": ["élections", "européennes", "sondages", "RN", "Renaissance"],
            "category": "Elections",
            "date_range": "20 jan 2024"
        }
    ]
    
    return sample_articles, sample_topics

def main():
    """Fonction principale pour générer et sauvegarder les données d'exemple"""
    print("🏛️ [DEMO] Génération de données d'exemple pour la plateforme politique")
    
    articles, topics = generate_sample_data()
    
    # Générer le fichier data.js pour le frontend
    data_js_content = f"""// Données d'exemple générées automatiquement - {datetime.now().isoformat()}
export const newsData = {json.dumps(articles, indent=2, ensure_ascii=False)};

export const topicsData = {json.dumps(topics, indent=2, ensure_ascii=False)};

export const lastUpdated = "{datetime.now().isoformat()}";
"""
    
    # Sauvegarder dans le répertoire src
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../src/data.js')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(data_js_content)
    
    print(f"✅ [DEMO] Données sauvegardées : {len(articles)} articles, {len(topics)} sujets")
    print(f"📄 [DEMO] Fichier généré : {output_path}")
    print(f"🚀 [DEMO] Vous pouvez maintenant lancer 'npm run dev' pour voir la démo")
    
    # Afficher un résumé
    print(f"\n📊 [RÉSUMÉ] Plateforme Politique - Données de Démonstration")
    print(f"📰 Articles par source :")
    sources = {}
    for article in articles:
        source = article['source']
        sources[source] = sources.get(source, 0) + 1
    
    for source, count in sources.items():
        print(f"  • {source}: {count} articles")
    
    print(f"\n🏷️ Sujets par catégorie :")
    categories = {}
    for topic in topics:
        cat = topic['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in categories.items():
        print(f"  • {cat}: {count} sujets")

if __name__ == "__main__":
    main() 