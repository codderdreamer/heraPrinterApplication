import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useParams, useNavigate } from 'react-router-dom';
import './App.css';
import Navigation from './components/Navigation';
import HomePage from './pages/HomePage';
import PrinterSettings from './pages/PrinterSettings';
import BitmapSettings from './pages/BitmapSettings';
import { Printer, apiService } from './services/api';

function App() {
  return (
    <Router>
      <div className="App">
        <Navigation />
        
        <main className="App-main">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/printer-settings" element={<PrinterSettings />} />
            <Route path="/bitmap-settings/:ip" element={<BitmapSettingsWrapper />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

// BitmapSettings wrapper component to handle routing
function BitmapSettingsWrapper() {
  const { ip } = useParams<{ ip: string }>();
  const navigate = useNavigate();
  
  const [printer, setPrinter] = useState<Printer | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchPrinter = async () => {
      try {
        const data = await apiService.getPrinter(ip!);
        setPrinter(data);
      } catch (error) {
        console.error('Error fetching printer:', error);
        navigate('/printer-settings');
      } finally {
        setLoading(false);
      }
    };
    
    if (ip) {
      fetchPrinter();
    }
  }, [ip, navigate]);
  
  const handleBack = () => {
    navigate('/printer-settings');
  };
  
  if (loading) {
    return <div className="container">Loading...</div>;
  }
  
  if (!printer) {
    return <div className="container">Printer not found</div>;
  }
  
  return <BitmapSettings printer={printer} onBack={handleBack} />;
}

export default App;
