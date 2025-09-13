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
  return (
    <div className="printer-card">
      <h3>{printer.name}</h3>
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
