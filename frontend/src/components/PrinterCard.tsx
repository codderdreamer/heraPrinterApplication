import React from 'react';
import { Printer } from '../services/api';
import '../styles/components/PrinterCard.css';

interface PrinterCardProps {
  printer: Printer;
  onDelete: (ip: string) => void;
  onConfigureBitmap: (ip: string) => void;
}

const PrinterCard: React.FC<PrinterCardProps> = ({ 
  printer, 
  onDelete, 
  onConfigureBitmap 
}) => {
  const getStatusColor = (isOnline?: boolean) => {
    return isOnline ? '#4CAF50' : '#f44336';
  };

  const getStatusText = (isOnline?: boolean) => {
    return isOnline ? 'Online' : 'Offline';
  };

  return (
    <div className="printer-card">
      <div className="printer-header">
        <h3>{printer.name}</h3>
        <div 
          className="status-indicator"
          style={{ 
            backgroundColor: getStatusColor(printer.is_online),
            color: 'white',
            padding: '4px 8px',
            borderRadius: '12px',
            fontSize: '12px',
            fontWeight: 'bold'
          }}
        >
          {getStatusText(printer.is_online)}
        </div>
      </div>
      <p><strong>IP:</strong> {printer.ip}</p>
      <p><strong>DPI:</strong> {printer.dpi}</p>
      <p><strong>Size:</strong> {printer.width} x {printer.height} mm</p>
      
      <div className="printer-actions">
        <button 
          className="btn btn-secondary"
          onClick={() => onConfigureBitmap(printer.ip)}
        >
          Bitmap Ayarla
        </button>
        <button 
          className="btn btn-danger"
          onClick={() => onDelete(printer.ip)}
        >
          Delete
        </button>
      </div>
    </div>
  );
};

export default PrinterCard;
