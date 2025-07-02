# 🏛️ Les Actualités Politiques

> Plateforme d'actualités politiques avec analyse intelligente par IA

Une plateforme moderne d'agrégation et d'analyse d'actualités politiques, alimentée par l'intelligence artificielle Google Gemini pour regrouper automatiquement les sujets politiques français et internationaux.

## 🚀 Fonctionnalités Principales

### 📰 Agrégation Multi-Sources Politiques
- Scraping automatisé de **40+ sources** spécialisées en politique
- Sources françaises et internationales (médias, institutions, analyses)
- Filtrage intelligent par source, langue et catégorie politique

### 🧠 Analyse Politique Intelligente avec Gemini
- **Architecture orchestrée par IA** : Utilise Google Gemini pour analyser et regrouper les articles politiques
- **Regroupement politique automatique** : Les articles traitant du même événement/personnalité/scandale sont intelligemment groupés
- **Synthèse journalistique politique** : Chaque sujet génère un résumé consolidé de tous les articles connexes
- **Catégorisation politique** : National, International, Elections, Politique, Scandale, Parlement
- **Extraction de mots-clés politiques** : Identification automatique des personnalités, partis et enjeux

### 🎯 Interface Utilisateur Spécialisée
- **Double vue** : Articles individuels ou sujets politiques regroupés
- **Cartes de sujets politiques expansibles** : Voir tous les articles d'un même sujet
- **Filtrage et recherche** avancés adaptés à la politique
- **Design responsive** avec layout optimisé pour le contenu politique
- **Navigation intuitive** entre les différentes catégories politiques

## 🛠️ Architecture Technique

### Frontend (React + Vite)
```bash
npm install
npm run dev
```

### Backend (Python + IA)
Le backend utilise une architecture hybride combinant :
- **Scraping multi-threadé** pour l'agrégation de contenu politique
- **API Google Gemini** pour l'analyse et le regroupement intelligent des sujets politiques
- **Pipeline de traitement** automatisé spécialisé pour la politique

#### Configuration Requise

1. **Clé API Gemini** (obligatoire)
   ```bash
   export GEMINI_API_KEY="votre_clé_api_gemini"
   ```

2. **Environnement Python**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # ou .\\venv\\Scripts\\activate  # Windows
   pip install -r requirements.txt
   ```

3. **Lancement du scraper politique**
   ```bash
   python scraper_politics.py
   ```

#### Fonctionnement du Pipeline IA Politique

1. **Scraping** : Collecte des articles depuis 40+ sources RSS politiques
2. **Préprocessing** : Nettoyage et extraction des métadonnées politiques
3. **Analyse Gemini** : Envoi à l'IA pour analyse sémantique politique
4. **Regroupement** : Création de sujets politiques cohérents avec articles connexes
5. **Génération** : Production de résumés et métadonnées enrichies politiques

## 🔧 Configuration

### Sources d'Actualités Politiques
Les sources sont configurées dans `src/config.json` avec :
- **Qualité** : Score de fiabilité (1-5)
- **Langue** : Français/Anglais
- **Catégorie** : Politique France, International, Europe & UE, Analyses & Opinion, Sondages & Data

### Paramètres Gemini Politiques
- **Modèle** : `gemini-1.5-flash`
- **Timeout** : 2 minutes
- **Analyse** : Max 100 articles politiques par batch
- **Critères** : Événements politiques, personnalités, partis, scandales, élections

## 📊 Exemple de Génération de Sujets Politiques

**Input** : 50 articles politiques
**Output Gemini** :
```json
{
  "topics": [
    {
      "name": "Réforme des Retraites Macron",
      "summary": "Le gouvernement français propose une nouvelle réforme des retraites...",
      "articles": [/* 5 articles from different sources */],
      "sources": ["Le Figaro", "Le Monde", "Libération"],
      "keywords": ["Macron", "retraites", "réforme", "syndicats"],
      "category": "National"
    }
  ]
}
```

## 🏛️ Sources Politiques Couvertes

### 🇫🇷 Politique France
- Le Figaro Politique, Le Monde Politique, Libération
- Mediapart, France 24, BFM Politique, LCI
- L'Express, Marianne, L'Opinion, Challenges

### 🌍 Politique Internationale
- BBC Politics, Reuters Politics, CNN Politics
- The Guardian Politics, Financial Times, Washington Post
- New York Times Politics, Politico

### 🇪🇺 Europe & UE
- Euronews Politique, Politico Europe
- European Parliament News, Deutsche Welle

### 💭 Analyses & Opinion
- Atlantico, Causeur, Contrepoints, Slate France
- Foreign Affairs, Project Syndicate, The Atlantic

## 🚦 Statut du Projet

✅ **Fonctionnel** : Scraping multi-sources politiques  
✅ **Fonctionnel** : Génération IA de sujets politiques avec Gemini  
✅ **Fonctionnel** : Interface utilisateur politique complète  
✅ **Fonctionnel** : Regroupement intelligent d'articles politiques  
🔄 **En cours** : Optimisation des performances et ajout de sources

## 🎯 Objectifs de l'Architecture IA Politique

L'objectif est de créer une **expérience de veille politique optimisée** où :
- L'utilisateur voit les **sujets politiques d'actualité** plutôt que des articles dispersés
- Chaque sujet regroupe **tous les médias** qui couvrent l'événement politique
- La **synthèse IA** évite la redondance d'information politique
- Le **regroupement automatique** révèle les tendances politiques importantes

Cette approche transforme la veille politique en une expérience curatoriale intelligente, permettant de suivre efficacement l'actualité politique française et internationale.

## 📋 Installation et Démarrage

### 1. Installation Frontend
```bash
npm install
npm run dev
```
L'application sera disponible sur `http://localhost:5178`

### 2. Installation Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurer la clé API Gemini
export GEMINI_API_KEY="votre_clé_api"

# Lancer le scraper
python scraper_politics.py --all
```

### 3. Structure du Projet
```
AI-NEWS-POLITICS/
├── src/                    # Frontend React
│   ├── components/         # Composants UI
│   ├── config.json        # Sources politiques
│   └── topics.js          # Sujets politiques
├── backend/               # Backend Python
│   ├── scraper_politics.py # Scraper principal
│   ├── database.py        # Gestion base de données
│   └── requirements.txt   # Dépendances Python
└── README.md             # Documentation
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Ajouter de nouvelles sources politiques
- Améliorer l'analyse IA des sujets politiques
- Optimiser l'interface utilisateur
- Signaler des bugs ou proposer des améliorations

---

**🏛️ Les Actualités Politiques** - Transformez votre veille politique grâce à l'intelligence artificielle 