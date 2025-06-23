import React from 'react';
import RefreshButton from './RefreshButton';
import './Header.css';

const Header = () => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <img src="/logo.svg" alt="Logo AI News" />
          <h1>Les Actualités de l'IA</h1>
        </div>
        <RefreshButton />
      </div>
      <p>Restez à la pointe avec les dernières avancées, découvertes et actualités de l'industrie de l'intelligence artificielle.</p>
    </header>
  );
};

export default Header; 