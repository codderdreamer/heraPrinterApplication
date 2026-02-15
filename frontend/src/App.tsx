import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useParams, useNavigate } from 'react-router-dom';
import './App.css';
import Navigation from './components/Navigation';
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
            <Route path="/" element={<PrinterSettings />} />
            <Route path="/printer-settings" element={<PrinterSettings />} />
            <Route path="/bitmap-settings" element={<BitmapSettingsWrapper />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

// BitmapSettings wrapper component to handle routing
function BitmapSettingsWrapper() {
  const navigate = useNavigate();
  const [printer, setPrinter] = useState<Printer | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchPrinter = async () => {
      try {
        // localStorage'dan printer name'i al (öncelikli)
        const printerName = localStorage.getItem('selectedPrinterName');
        const printerIp = localStorage.getItem('selectedPrinterIp'); // Geriye dönük uyumluluk
        
        if (!printerName && !printerIp) {
          navigate('/printer-settings');
          return;
        }
        
        // Önce name'e göre ara, yoksa IP'ye göre ara
        const data = await apiService.getPrinter(printerIp || undefined, printerName || undefined);
        setPrinter(data);
      } catch (error) {
        console.error('Error fetching printer:', error);
        navigate('/printer-settings');
      } finally {
        setLoading(false);
      }
    };
    
    fetchPrinter();
  }, [navigate]);
  
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
