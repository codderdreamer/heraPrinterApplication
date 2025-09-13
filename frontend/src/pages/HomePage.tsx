import React, { useState, useEffect } from 'react';
import { Printer, apiService } from '../services/api';
import PrinterCard from '../components/PrinterCard';

const HomePage: React.FC = () => {
  const [printers, setPrinters] = useState<Printer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPrinters();
  }, []);

  const fetchPrinters = async () => {
    try {
      setLoading(true);
      const data = await apiService.getPrinters();
      setPrinters(data);
    } catch (error) {
      console.error('Error fetching printers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePrinter = async (ip: string) => {
    if (window.confirm('Are you sure you want to delete this printer?')) {
      try {
        await apiService.deletePrinter(ip);
        fetchPrinters();
      } catch (error) {
        console.error('Error deleting printer:', error);
      }
    }
  };

  const handleConfigureBitmap = (ip: string) => {
    // Navigate to bitmap settings page
    window.location.href = `/bitmap-settings/${ip}`;
  };

  if (loading) {
    return (
      <div className="container">
        <h1>Hera Printer Application</h1>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>Hera Printer Application</h1>
      <p>Printer Management System</p>
      
      <div className="glass-card">
        <h2>Hera Printer</h2>
        <p>Welcome to the Hera Printer Management System.</p>
        
        <h3>Registered Printers ({printers.length})</h3>
        {printers.length === 0 ? (
          <p>No printers found. Add a printer to get started.</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
            {printers.map((printer) => (
              <PrinterCard
                key={printer.id}
                printer={printer}
                onDelete={(ip) => handleDeletePrinter(ip)}
                onConfigureBitmap={(ip) => handleConfigureBitmap(ip)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default HomePage;
