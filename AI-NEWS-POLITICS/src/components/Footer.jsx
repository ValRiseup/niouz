import React from 'react';
import './Footer.css';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-content">
          <div className="footer-section">
            <h3 className="footer-title">
              🏛️ Les Actualités Politiques
            </h3>
            <p className="footer-description">
              Plateforme d'actualités politiques alimentée par l'intelligence artificielle. 
              Analyse automatique et regroupement intelligent des sujets politiques français et internationaux.
            </p>
          </div>

          <div className="footer-section">
            <h4 className="footer-subtitle">✨ Fonctionnalités</h4>
            <ul className="footer-list">
              <li>🧠 Analyse IA avec Google Gemini</li>
              <li>📰 Sources multiples vérifiées</li>
              <li>🔍 Regroupement intelligent</li>
              <li>🌍 Français & International</li>
            </ul>
          </div>

          <div className="footer-section">
            <h4 className="footer-subtitle">📊 Sources</h4>
            <ul className="footer-list">
              <li>📺 Médias traditionnels</li>
              <li>🏛️ Institutions politiques</li>
              <li>💭 Analyses d'experts</li>
              <li>📈 Sondages & données</li>
            </ul>
          </div>

          <div className="footer-section">
            <h4 className="footer-subtitle">🔧 Technologie</h4>
            <ul className="footer-list">
              <li>⚛️ React & Vite</li>
              <li>🐍 Python & Scraping</li>
              <li>🤖 Google Gemini AI</li>
              <li>📱 Design Responsive</li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <div className="footer-legal">
            <p>&copy; {currentYear} Les Actualités Politiques - Analyse IA</p>
            <p className="footer-note">
              Contenu agrégé automatiquement depuis des sources publiques. 
              Cliquez sur les articles pour accéder aux sources originales.
            </p>
          </div>
          
          <div className="footer-stats">
            <span className="stat-badge">
              🤖 Powered by AI
            </span>
            <span className="stat-badge">
              🌐 Open Source
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 