// Political topics configuration for French and international politics
export const topicCategories = [
  {
    id: 'national',
    name: 'National',
    icon: '🇫🇷',
    description: 'Politique française, gouvernement, parlement',
    color: '#1e40af'
  },
  {
    id: 'international',
    name: 'International',
    icon: '🌍',
    description: 'Diplomatie, relations internationales',
    color: '#059669'
  },
  {
    id: 'elections',
    name: 'Élections',
    icon: '🗳️',
    description: 'Campagnes, sondages, résultats électoraux',
    color: '#dc2626'
  },
  {
    id: 'economie',
    name: 'Économie',
    icon: '💼',
    description: 'Politique économique, budget, finances',
    color: '#7c3aed'
  },
  {
    id: 'social',
    name: 'Social',
    icon: '👥',
    description: 'Politique sociale, réformes, société',
    color: '#ea580c'
  },
  {
    id: 'justice',
    name: 'Justice',
    icon: '⚖️',
    description: 'Affaires judiciaires, scandales, enquêtes',
    color: '#be185d'
  },
  {
    id: 'europe',
    name: 'Europe',
    icon: '🇪🇺',
    description: 'Union européenne, parlement européen',
    color: '#0284c7'
  },
  {
    id: 'institutions',
    name: 'Institutions',
    icon: '🏛️',
    description: 'Assemblée, Sénat, Conseil constitutionnel',
    color: '#4338ca'
  },
  {
    id: 'parties',
    name: 'Partis',
    icon: '🎯',
    description: 'Partis politiques, stratégies, alliances',
    color: '#16a34a'
  },
  {
    id: 'regions',
    name: 'Régions',
    icon: '🏘️',
    description: 'Politique locale, collectivités territoriales',
    color: '#0891b2'
  }
];

// Enhanced political keywords for better categorization
export const politicalKeywords = {
  national: [
    'macron', 'président', 'gouvernement', 'premier ministre', 'conseil ministres',
    'élysée', 'matignon', 'france', 'français', 'république', 'état'
  ],
  international: [
    'diplomatie', 'international', 'étranger', 'ambassade', 'traité',
    'otan', 'onu', 'g7', 'g20', 'sommet', 'relations', 'guerre', 'paix'
  ],
  elections: [
    'élection', 'vote', 'scrutin', 'campagne', 'candidat', 'sondage',
    'présidentielle', 'législatives', 'municipales', 'européennes', 'ballot'
  ],
  economie: [
    'budget', 'économie', 'finance', 'fiscal', 'taxe', 'impôt',
    'bercy', 'croissance', 'inflation', 'chômage', 'emploi', 'retraite'
  ],
  social: [
    'social', 'santé', 'éducation', 'logement', 'famille', 'jeunesse',
    'solidarité', 'protection sociale', 'sécurité sociale', 'cmu'
  ],
  justice: [
    'justice', 'procès', 'enquête', 'tribunal', 'juge', 'avocat',
    'scandale', 'corruption', 'affaire', 'police', 'gendarmerie'
  ],
  europe: [
    'europe', 'européen', 'ue', 'bruxelles', 'parlement européen',
    'commission européenne', 'conseil européen', 'euro', 'brexit'
  ],
  institutions: [
    'assemblée', 'sénat', 'parlement', 'député', 'sénateur',
    'conseil constitutionnel', 'conseil état', 'palais bourbon'
  ],
  parties: [
    'parti', 'renaissance', 'républicains', 'socialiste', 'insoumise',
    'rassemblement national', 'écologie', 'politique', 'alliance'
  ],
  regions: [
    'région', 'département', 'commune', 'maire', 'préfet',
    'collectivité', 'territorial', 'local', 'métropole'
  ]
};

// Enhanced source categories for political news
export const sourceCategories = {
  'Politique France': {
    description: 'Actualité politique française',
    priority: 1,
    icon: '🇫🇷'
  },
  'Assemblée & Sénat': {
    description: 'Institutions parlementaires',
    priority: 2,
    icon: '🏛️'
  },
  'Partis Politiques': {
    description: 'Communication des partis',
    priority: 3,
    icon: '🎯'
  },
  'Régions & Collectivités': {
    description: 'Politique territoriale',
    priority: 4,
    icon: '🏘️'
  },
  'Politique Internationale': {
    description: 'Actualité politique mondiale',
    priority: 5,
    icon: '🌍'
  },
  'Europe & UE': {
    description: 'Politique européenne',
    priority: 6,
    icon: '🇪🇺'
  },
  'Analyses & Opinion': {
    description: 'Analyses et éditoriaux',
    priority: 7,
    icon: '📝'
  },
  'Sondages & Data': {
    description: 'Enquêtes d\'opinion',
    priority: 8,
    icon: '📊'
  },
  'Fact-Checking': {
    description: 'Vérification des faits',
    priority: 9,
    icon: '✅'
  }
}; 