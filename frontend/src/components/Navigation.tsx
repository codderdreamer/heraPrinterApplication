import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import '../styles/components/Navigation.css';

const Navigation: React.FC = () => {
  const location = useLocation();

  return (
    <nav className="navigation">
      <div className="nav-brand">
        <h2>Hera Printer</h2>
      </div>
      <div className="nav-menu">
        <Link 
          to="/" 
          className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
        >
          Printer Ayarları
        </Link>
      </div>
    </nav>
  );
};

export default Navigation;
