import React, { useState } from 'react';
import { Printer } from '../services/api';
import '../styles/pages/BitmapSettings.css';

interface BitmapSettingsProps {
  printer: Printer;
  onBack: () => void;
}

interface TextItem {
  id: number;
  content: string;
  x: number;
  y: number;
  fontSize: number;
  fontFamily: string;
}

const BitmapSettings: React.FC<BitmapSettingsProps> = ({ printer, onBack }) => {
  const [textItems, setTextItems] = useState<TextItem[]>([]);
  const [nextTextId, setNextTextId] = useState(1);

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

  const handleIconChange = (field: string, value: string | number) => {
    setIconInfo(prev => ({ ...prev, [field]: value }));
  };

  const handleBarcodeChange = (field: string, value: string | number) => {
    setBarcodeInfo(prev => ({ ...prev, [field]: value }));
  };

  const addNewText = () => {
    const newText: TextItem = {
      id: nextTextId,
      content: '',
      x: 0,
      y: 0,
      fontSize: 12,
      fontFamily: 'Arial'
    };
    setTextItems(prev => [...prev, newText]);
    setNextTextId(prev => prev + 1);
  };

  const updateTextItem = (id: number, field: string, value: string | number) => {
    setTextItems(prev => 
      prev.map(item => 
        item.id === id ? { ...item, [field]: value } : item
      )
    );
  };

  const deleteTextItem = (id: number) => {
    setTextItems(prev => prev.filter(item => item.id !== id));
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
            <h3>Text Bilgileri</h3>
            
            <button 
              className="btn btn-secondary add-text-btn"
              onClick={addNewText}
            >
              + Text Ekle
            </button>

            {textItems.map((textItem) => (
              <div key={textItem.id} className="text-item">
                <div className="text-item-header">
                  <span>Text #{textItem.id}</span>
                  <button 
                    className="btn btn-danger delete-text-btn"
                    onClick={() => deleteTextItem(textItem.id)}
                  >
                    Sil
                  </button>
                </div>
                
                <div className="form-group">
                  <label>Text:</label>
                  <input
                    type="text"
                    value={textItem.content}
                    onChange={(e) => updateTextItem(textItem.id, 'content', e.target.value)}
                    placeholder="Yazılacak metin..."
                  />
                </div>
                <div className="form-group">
                  <label>X Koordinatı:</label>
                  <input
                    type="number"
                    value={textItem.x}
                    onChange={(e) => updateTextItem(textItem.id, 'x', e.target.value === '' ? '' : parseInt(e.target.value))}
                    min="0"
                    placeholder="0"
                  />
                </div>
                <div className="form-group">
                  <label>Y Koordinatı:</label>
                  <input
                    type="number"
                    value={textItem.y}
                    onChange={(e) => updateTextItem(textItem.id, 'y', e.target.value === '' ? '' : parseInt(e.target.value))}
                    min="0"
                    placeholder="0"
                  />
                </div>
                <div className="form-group">
                  <label>Font Boyutu:</label>
                  <input
                    type="number"
                    value={textItem.fontSize}
                    onChange={(e) => updateTextItem(textItem.id, 'fontSize', parseInt(e.target.value))}
                    min="8"
                    max="72"
                  />
                </div>
                <div className="form-group">
                  <label>Font Ailesi:</label>
                  <select
                    value={textItem.fontFamily}
                    onChange={(e) => updateTextItem(textItem.id, 'fontFamily', e.target.value)}
                  >
                    <option value="Arial">Arial</option>
                    <option value="Times New Roman">Times New Roman</option>
                    <option value="Courier New">Courier New</option>
                    <option value="Helvetica">Helvetica</option>
                  </select>
                </div>
              </div>
            ))}
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
              {/* Text Preview - Multiple texts */}
              {textItems.map((textItem) => (
                textItem.content && (
                  <div 
                    key={textItem.id}
                    className="preview-text"
                    style={{
                      position: 'absolute',
                      left: `${textItem.x || 0}px`,
                      top: `${textItem.y || 0}px`,
                      fontSize: `${textItem.fontSize}px`,
                      fontFamily: textItem.fontFamily,
                      color: '#000000'
                    }}
                  >
                    {textItem.content}
                  </div>
                )
              ))}

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
              <p>Text Sayısı: {textItems.length}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BitmapSettings;
