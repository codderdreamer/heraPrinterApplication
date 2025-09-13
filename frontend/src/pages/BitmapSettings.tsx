import React, { useState } from 'react';
import { Printer } from '../services/api';
import '../styles/pages/BitmapSettings.css';

interface BitmapSettingsProps {
  printer: Printer;
  onBack: () => void;
}

const BitmapSettings: React.FC<BitmapSettingsProps> = ({ printer, onBack }) => {
  const [textInfo, setTextInfo] = useState({
    content: '',
    x: 0,
    y: 0,
    fontSize: 12,
    fontFamily: 'Arial'
  });

  const [iconInfo, setIconInfo] = useState({
    iconType: 'none',
    size: 24,
    color: '#000000'
  });

  const [barcodeInfo, setBarcodeInfo] = useState({
    content: '',
    type: 'code128',
    height: 50,
    width: 2
  });

  const [showTextFields, setShowTextFields] = useState(false);

  const handleTextChange = (field: string, value: string | number) => {
    setTextInfo(prev => ({ ...prev, [field]: value }));
  };

  const handleIconChange = (field: string, value: string | number) => {
    setIconInfo(prev => ({ ...prev, [field]: value }));
  };

  const handleBarcodeChange = (field: string, value: string | number) => {
    setBarcodeInfo(prev => ({ ...prev, [field]: value }));
  };

  const toggleTextFields = () => {
    setShowTextFields(!showTextFields);
  };

  // Bitmap boyutlarını hesapla (mm'den pixel'e)
  const dpi = printer.dpi;
  const widthPx = Math.round((printer.width * dpi) / 25.4);
  const heightPx = Math.round((printer.height * dpi) / 25.4);

  return (
    <div className="bitmap-settings">
      <div className="settings-header">
        <button onClick={onBack} className="btn-back">← Geri</button>
        <h2>Bitmap Ayarları - {printer.name}</h2>
      </div>

      <div className="settings-content">
        <div className="settings-panel">
          <div className="settings-section">
            <div className="section-header">
              <h3>Text Bilgileri</h3>
              <button 
                className="toggle-btn"
                onClick={toggleTextFields}
              >
                {showTextFields ? '−' : '+'}
              </button>
            </div>
            
            {showTextFields && (
              <div className="form-fields">
                <div className="form-group">
                  <label>Text:</label>
                  <input
                    type="text"
                    value={textInfo.content}
                    onChange={(e) => handleTextChange('content', e.target.value)}
                    placeholder="Yazılacak metin..."
                  />
                </div>
                <div className="form-group">
                  <label>X Koordinatı:</label>
                  <input
                    type="number"
                    value={textInfo.x}
                    onChange={(e) => handleTextChange('x', parseInt(e.target.value) || 0)}
                    min="0"
                  />
                </div>
                <div className="form-group">
                  <label>Y Koordinatı:</label>
                  <input
                    type="number"
                    value={textInfo.y}
                    onChange={(e) => handleTextChange('y', parseInt(e.target.value) || 0)}
                    min="0"
                  />
                </div>
                <div className="form-group">
                  <label>Font Boyutu:</label>
                  <input
                    type="number"
                    value={textInfo.fontSize}
                    onChange={(e) => handleTextChange('fontSize', parseInt(e.target.value))}
                    min="8"
                    max="72"
                  />
                </div>
                <div className="form-group">
                  <label>Font Ailesi:</label>
                  <select
                    value={textInfo.fontFamily}
                    onChange={(e) => handleTextChange('fontFamily', e.target.value)}
                  >
                    <option value="Arial">Arial</option>
                    <option value="Times New Roman">Times New Roman</option>
                    <option value="Courier New">Courier New</option>
                    <option value="Helvetica">Helvetica</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          <div className="settings-section">
            <h3>İkon Bilgileri</h3>
            <div className="form-group">
              <label>İkon Tipi:</label>
              <select
                value={iconInfo.iconType}
                onChange={(e) => handleIconChange('iconType', e.target.value)}
              >
                <option value="none">İkon Yok</option>
                <option value="logo">Logo</option>
                <option value="warning">Uyarı</option>
                <option value="info">Bilgi</option>
              </select>
            </div>
            <div className="form-group">
              <label>Boyut:</label>
              <input
                type="number"
                value={iconInfo.size}
                onChange={(e) => handleIconChange('size', parseInt(e.target.value))}
                min="16"
                max="64"
              />
            </div>
            <div className="form-group">
              <label>Renk:</label>
              <input
                type="color"
                value={iconInfo.color}
                onChange={(e) => handleIconChange('color', e.target.value)}
              />
            </div>
          </div>

          <div className="settings-section">
            <h3>Barkod Bilgileri</h3>
            <div className="form-group">
              <label>İçerik:</label>
              <input
                type="text"
                value={barcodeInfo.content}
                onChange={(e) => handleBarcodeChange('content', e.target.value)}
                placeholder="Barkod içeriği..."
              />
            </div>
            <div className="form-group">
              <label>Tip:</label>
              <select
                value={barcodeInfo.type}
                onChange={(e) => handleBarcodeChange('type', e.target.value)}
              >
                <option value="code128">Code 128</option>
                <option value="code39">Code 39</option>
                <option value="ean13">EAN-13</option>
                <option value="qr">QR Code</option>
              </select>
            </div>
            <div className="form-group">
              <label>Yükseklik:</label>
              <input
                type="number"
                value={barcodeInfo.height}
                onChange={(e) => handleBarcodeChange('height', parseInt(e.target.value))}
                min="20"
                max="100"
              />
            </div>
            <div className="form-group">
              <label>Genişlik:</label>
              <input
                type="number"
                value={barcodeInfo.width}
                onChange={(e) => handleBarcodeChange('width', parseInt(e.target.value))}
                min="1"
                max="10"
              />
            </div>
          </div>
        </div>

        <div className="preview-panel">
          <h3>Bitmap Önizlemesi</h3>
          <div className="preview-container">
            <div 
              className="bitmap-preview"
              style={{
                aspectRatio: `${widthPx} / ${heightPx}`
              }}
            >
              {/* Text Preview */}
              {textInfo.content && (
                <div 
                  className="preview-text"
                  style={{
                    position: 'absolute',
                    left: `${textInfo.x}px`,
                    top: `${textInfo.y}px`,
                    fontSize: `${textInfo.fontSize}px`,
                    fontFamily: textInfo.fontFamily,
                    color: '#000000'
                  }}
                >
                  {textInfo.content}
                </div>
              )}

              {/* Icon Preview */}
              {iconInfo.iconType !== 'none' && (
                <div 
                  className="preview-icon"
                  style={{
                    width: `${iconInfo.size}px`,
                    height: `${iconInfo.size}px`,
                    backgroundColor: iconInfo.color,
                    borderRadius: '4px'
                  }}
                >
                  {iconInfo.iconType}
                </div>
              )}

              {/* Barcode Preview */}
              {barcodeInfo.content && (
                <div 
                  className="preview-barcode"
                  style={{
                    height: `${barcodeInfo.height}px`,
                    width: `${barcodeInfo.content.length * 8}px`,
                    backgroundColor: '#000000',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#ffffff',
                    fontSize: '10px'
                  }}
                >
                  {barcodeInfo.content}
                </div>
              )}
            </div>
            <div className="preview-info">
              <p>Boyut: {widthPx} x {heightPx} px</p>
              <p>Çözünürlük: {printer.dpi} DPI</p>
              <p>Oran: {printer.width}:{printer.height}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BitmapSettings;
