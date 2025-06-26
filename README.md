# Les Actualités de l'IA

Une plateforme d'actualités IA avec génération intelligente de sujets orchestrée par l'intelligence artificielle.

## 🚀 Fonctionnalités Principales

### 📰 Agrégation Multi-Sources
- Scraping automatisé de **70+ sources** spécialisées en IA
- Sources en français et anglais (médias, blogs, recherche, entreprises)
- Filtrage intelligent par source et langue

### 🧠 Génération Intelligente de Sujets avec Gemini
- **Architecture orchestrée par IA** : Utilise Google Gemini pour analyser et regrouper les articles
- **Regroupement automatique** : Les articles traitant du même événement/sujet sont intelligemment groupés
- **Synthèse journalistique** : Chaque sujet génère un résumé consolidé de tous les articles connexes
- **Catégorisation automatique** : Corporate, Technology, Research, Ethics, Community
- **Extraction de mots-clés** : Identification automatique des termes techniques pertinents

### 🎯 Interface Utilisateur Avancée
- **Double vue** : Articles individuels ou sujets regroupés
- **Cartes de sujets expansibles** : Voir tous les articles d'un même sujet
- **Filtrage et recherche** avancés
- **Design responsive** avec layout Masonry
- **Scroll infini** pour une navigation fluide

## 🛠️ Architecture Technique

### Frontend (React + Vite)
```bash
npm install
npm run dev
```

### Backend (Python + IA)
Le backend utilise une architecture hybride combinant :
- **Scraping multi-threadé** pour l'agrégation de contenu
- **API Google Gemini** pour l'analyse et le regroupement intelligent
- **Pipeline de traitement** automatisé

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

3. **Lancement du scraper**
   ```bash
   python scraper.py
   ```

#### Fonctionnement du Pipeline IA

1. **Scraping** : Collecte des articles depuis 70+ sources RSS
2. **Préprocessing** : Nettoyage et extraction des métadonnées
3. **Analyse Gemini** : Envoi à l'IA pour analyse sémantique
4. **Regroupement** : Création de sujets cohérents avec articles connexes
5. **Génération** : Production de résumés et métadonnées enrichies

## 🔧 Configuration

### Sources d'Actualités
Les sources sont configurées dans `src/config.json` avec :
- **Qualité** : Score de fiabilité (1-5)
- **Langue** : Français/Anglais
- **Catégorie** : Business, Research, Technical, etc.

### Paramètres Gemini
- **Modèle** : `gemini-1.5-flash`
- **Timeout** : 2 minutes
- **Analyse** : Max 100 articles par batch
- **Critères** : Événements, entreprises, technologies, recherche

## 📊 Exemple de Génération de Sujets

**Input** : 50 articles sur l'IA
**Output Gemini** :
```json
{
  "topics": [
    {
      "name": "OpenAI GPT-4 Vision Launch",
      "summary": "OpenAI announces GPT-4 Vision with multimodal capabilities...",
      "articles": [/* 5 articles from different sources */],
      "sources": ["TechCrunch", "Wired", "The Verge"],
      "keywords": ["GPT-4", "Vision", "Multimodal", "OpenAI"],
      "category": "Corporate"
    }
  ]
}
```

## 🚦 Statut du Projet

✅ **Fonctionnel** : Scraping multi-sources  
✅ **Fonctionnel** : Génération IA de sujets avec Gemini  
✅ **Fonctionnel** : Interface utilisateur complète  
✅ **Fonctionnel** : Regroupement intelligent d'articles  
🔄 **En cours** : Optimisation des performances

## 🎯 Objectifs de l'Architecture IA

L'objectif est de créer une **expérience de lecture optimisée** où :
- L'utilisateur voit les **sujets d'actualité** plutôt que des articles dispersés
- Chaque sujet regroupe **tous les médias** qui en parlent
- La **synthèse IA** évite la redondance d'information
- Le **regroupement automatique** révèle les tendances importantes

Cette approche transforme la veille technologique en une expérience curatoriale intelligente.
