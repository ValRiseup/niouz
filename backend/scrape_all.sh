#!/bin/bash

# Script pour récupérer TOUS les articles avec l'IA Gemini
# Utile pour le développement et les tests

echo "🚀 Lancement du scraping complet avec génération IA de sujets..."
echo "📋 Mode: TOUS LES ARTICLES (ignorer timestamp)"
echo ""

# Activer l'environnement virtuel
source venv/bin/activate

# Lancer le scraper avec l'option --all
python scraper.py --all

echo ""
echo "✅ Scraping terminé ! Vérifiez le fichier ../src/data.js"
echo "🌐 Lancez 'npm run dev' dans le répertoire racine pour voir les résultats" 