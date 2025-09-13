import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Printer, apiService } from '../services/api';
import PrinterCard from '../components/PrinterCard';
import '../styles/pages/PrinterSettings.css';

const PrinterSettings: React.FC = () => {
  const [printers, setPrinters] = useState<Printer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    ip: '',
    name: '',
    dpi: 300,
    width: 100,
    height: 30
  });
  const navigate = useNavigate();

  useEffect(() => {
    fetchPrinters();
  }, []);

  const fetchPrinters = async () => {
    try {
      setLoading(true);
      const data = await apiService.getPrinters();
      setPrinters(data);
    } catch (err) {
      setError('Printer listesi yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'dpi' || name === 'width' || name === 'height' 
        ? parseInt(value) || 0 
        : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.ip || !formData.name) {
      setError('IP ve Name alanları zorunludur');
      return;
    }

    if (formData.dpi < 72 || formData.dpi > 4800) {
      setError('DPI 72-4800 arasında olmalıdır');
      return;
    }

    if (formData.width < 1 || formData.width > 2000) {
      setError('Width 1-2000 arasında olmalıdır');
      return;
    }

    if (formData.height < 1 || formData.height > 2000) {
      setError('Height 1-2000 arasında olmalıdır');
      return;
    }

    try {
      await apiService.createPrinter(formData);
      setFormData({ ip: '', name: '', dpi: 300, width: 100, height: 30 });
      setError(null);
      fetchPrinters();
    } catch (err) {
      setError('Printer eklenirken hata oluştu');
    }
  };

  const handleDeletePrinter = async (ip: string) => {
    if (window.confirm('Bu printer\'ı silmek istediğinizden emin misiniz?')) {
      try {
        await apiService.deletePrinter(ip);
        fetchPrinters();
      } catch (err) {
        setError('Printer silinirken hata oluştu');
      }
    }
  };

  const handleConfigureBitmap = (ip: string) => {
    navigate(`/bitmap-settings/${ip}`);
  };

  if (loading) {
    return <div className="container">Yükleniyor...</div>;
  }

  return (
    <div className="printer-settings">
      <h1>Printer Ayarları</h1>
      
      <form onSubmit={handleSubmit} className="add-printer-form">
        <h2>Yeni Printer Ekle</h2>
        
        {error && (
          <div style={{ color: '#ff6b6b', marginBottom: '1rem' }}>
            {error}
          </div>
        )}
        
        <div className="form-row">
          <div className="form-group">
            <label>IP Adresi:</label>
            <input
              type="text"
              name="ip"
              value={formData.ip}
              onChange={handleInputChange}
              placeholder="192.168.1.100"
              required
            />
          </div>
          
          <div className="form-group">
            <label>Printer Adı:</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="TSC Printer"
              required
            />
          </div>
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <label>DPI:</label>
            <input
              type="number"
              name="dpi"
              value={formData.dpi}
              onChange={handleInputChange}
              min="72"
              max="4800"
              required
            />
          </div>
          
          <div className="form-group">
            <label>Genişlik (mm):</label>
            <input
              type="number"
              name="width"
              value={formData.width}
              onChange={handleInputChange}
              min="1"
              max="2000"
              required
            />
          </div>
          
          <div className="form-group">
            <label>Yükseklik (mm):</label>
            <input
              type="number"
              name="height"
              value={formData.height}
              onChange={handleInputChange}
              min="1"
              max="2000"
              required
            />
          </div>
        </div>
        
        <button type="submit" className="btn">
          Printer Ekle
        </button>
      </form>
      
      <div>
        <h2>Kayıtlı Printerlar ({printers.length})</h2>
        <div className="printer-grid">
          {printers.map((printer) => (
            <PrinterCard
              key={printer.ip}
              printer={printer}
              onDelete={handleDeletePrinter}
              onConfigureBitmap={handleConfigureBitmap}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default PrinterSettings;
