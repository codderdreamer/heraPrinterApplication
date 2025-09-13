import React, { useState, useEffect } from 'react';
import './App.css';

interface Printer {
  id: number;
  ip: string;
  name: string;
  dots_per_mm: number;
  width: number;
  height: number;
  created_at: string;
  updated_at: string;
}

function App() {
  const [printers, setPrinters] = useState<Printer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPrinters();
  }, []);

  const fetchPrinters = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/printers');
      const data = await response.json();
      setPrinters(data);
    } catch (error) {
      console.error('Error fetching printers:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Hera Printer Application</h1>
        <p>Printer Management System</p>
      </header>
      
      <main className="App-main">
        <div className="printers-section">
          <h2>Registered Printers</h2>
          {loading ? (
            <p>Loading printers...</p>
          ) : (
            <div className="printers-grid">
              {printers.length === 0 ? (
                <p>No printers found. Add a printer to get started.</p>
              ) : (
                printers.map((printer) => (
                  <div key={printer.id} className="printer-card">
                    <h3>{printer.name}</h3>
                    <p><strong>IP:</strong> {printer.ip}</p>
                    <p><strong>Resolution:</strong> {printer.dots_per_mm} DPI</p>
                    <p><strong>Size:</strong> {printer.width} x {printer.height} mm</p>
                    <p><strong>Added:</strong> {new Date(printer.created_at).toLocaleDateString()}</p>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
