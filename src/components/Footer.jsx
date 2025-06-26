import React from 'react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <p>Curated by an AI Assistant for a developer in Paris.</p>
        <p>&copy; {new Date().getFullYear()} AI News Feed. All Rights Reserved.</p>
      </div>
    </footer>
  );
};

export default Footer; 