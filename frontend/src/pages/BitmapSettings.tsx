import React, { useState, useEffect, useCallback } from 'react';
import { Printer, apiService } from '../services/api';
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

interface IconItem {
  id: number;
  x: number;
  y: number;
  width: number;
  height: number;
  iconFile: string;
}

interface BarcodeItem {
  id: number;
  sira: number;
  x: number;
  y: number;
  width: number;
  height: number;
  format: string;
  data: string;
  fontSize: number;
  fontFamily: string;
  textKonum: string;
}

const BitmapSettings: React.FC<BitmapSettingsProps> = ({ printer, onBack }) => {
  const [textItems, setTextItems] = useState<TextItem[]>([]);
  const [nextTextId, setNextTextId] = useState(1);

  const [iconItems, setIconItems] = useState<IconItem[]>([]);
  const [nextIconId, setNextIconId] = useState(1);

  const [barcodeItems, setBarcodeItems] = useState<BarcodeItem[]>([]);
  const [nextBarcodeId, setNextBarcodeId] = useState(1);

  const [saveStatus, setSaveStatus] = useState<string>('');
  const [logoUrl, setLogoUrl] = useState<string>('');

  // Logo'yu almak için fonksiyon
  const fetchLogo = useCallback(async () => {
    try {
      const settings = {
        textItems,
        iconItems,
        barcodeItems
      };
      
      const blob = await apiService.getLogo({ ...settings, ip: printer.ip });
      const url = URL.createObjectURL(blob);
      setLogoUrl(url);
    } catch (error) {
      console.error('Error fetching logo:', error);
    }
  }, [textItems, iconItems, barcodeItems, printer.ip]);

  // Otomatik kaydetme fonksiyonu
  const saveSettings = useCallback(async () => {
    try {
      const settings = {
        textItems,
        iconItems,
        barcodeItems
      };
      
      await apiService.saveBitmapSettings({ ...settings, ip: printer.ip });
      setSaveStatus('Kaydedildi');
      
      // 2 saniye sonra status'u temizle
      setTimeout(() => setSaveStatus(''), 2000);
    } catch (error) {
      console.error('Error saving bitmap settings:', error);
      setSaveStatus('Hata!');
      setTimeout(() => setSaveStatus(''), 2000);
    }
  }, [textItems, iconItems, barcodeItems, printer.ip]);

  // Form değişikliklerini otomatik kaydet
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (textItems.length > 0 || iconItems.length > 0 || barcodeItems.length > 0) {
        saveSettings();
      }
    }, 1000); // 1 saniye bekle

    return () => clearTimeout(timeoutId);
  }, [textItems, iconItems, barcodeItems, saveSettings]);

  // Component mount olduğunda logo'yu al
  useEffect(() => {
    fetchLogo();
  }, [fetchLogo]);

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

  const addNewIcon = () => {
    const newIcon: IconItem = {
      id: nextIconId,
      x: 0,
      y: 0,
      width: 24,
      height: 24,
      iconFile: ''
    };
    setIconItems(prev => [...prev, newIcon]);
    setNextIconId(prev => prev + 1);
  };

  const updateIconItem = (id: number, field: string, value: string | number) => {
    setIconItems(prev => 
      prev.map(item => 
        item.id === id ? { ...item, [field]: value } : item
      )
    );
  };

  const deleteIconItem = (id: number) => {
    setIconItems(prev => prev.filter(item => item.id !== id));
  };

  const handleIconFileChange = (id: number, event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        updateIconItem(id, 'iconFile', result);
      };
      reader.readAsDataURL(file);
    }
  };

  const addNewBarcode = () => {
    const newBarcode: BarcodeItem = {
      id: nextBarcodeId,
      sira: nextBarcodeId,
      x: 0,
      y: 0,
      width: 100,
      height: 50,
      format: 'code128',
      data: '',
      fontSize: 12,
      fontFamily: 'Arial',
      textKonum: 'alt'
    };
    setBarcodeItems(prev => [...prev, newBarcode]);
    setNextBarcodeId(prev => prev + 1);
  };

  const updateBarcodeItem = (id: number, field: string, value: string | number) => {
    setBarcodeItems(prev => 
      prev.map(item => 
        item.id === id ? { ...item, [field]: value } : item
      )
    );
  };

  const deleteBarcodeItem = (id: number) => {
    setBarcodeItems(prev => prev.filter(item => item.id !== id));
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
        {saveStatus && (
          <span className="save-status" style={{ 
            color: saveStatus === 'Kaydedildi' ? '#4CAF50' : '#f44336',
            marginLeft: '1rem',
            fontSize: '0.9rem'
          }}>
            {saveStatus}
          </span>
        )}
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
            
            <button 
              className="btn btn-secondary add-text-btn"
              onClick={addNewIcon}
            >
              + İkon Ekle
            </button>

            {iconItems.map((iconItem) => (
              <div key={iconItem.id} className="text-item">
                <div className="text-item-header">
                  <span>İkon #{iconItem.id}</span>
                  <button 
                    className="btn btn-danger delete-text-btn"
                    onClick={() => deleteIconItem(iconItem.id)}
                  >
                    Sil
                  </button>
                </div>
                
                <div className="form-group">
                  <label>İkon Dosyası:</label>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleIconFileChange(iconItem.id, e)}
                  />
                  {iconItem.iconFile && (
                    <div className="icon-preview">
                      <img src={iconItem.iconFile} alt="Icon preview" style={{ maxWidth: '50px', maxHeight: '50px' }} />
                    </div>
                  )}
                </div>
                <div className="form-group">
                  <label>X Koordinatı:</label>
                  <input
                    type="number"
                    value={iconItem.x}
                    onChange={(e) => updateIconItem(iconItem.id, 'x', e.target.value === '' ? '' : parseInt(e.target.value))}
                    min="0"
                    placeholder="0"
                  />
                </div>
                <div className="form-group">
                  <label>Y Koordinatı:</label>
                  <input
                    type="number"
                    value={iconItem.y}
                    onChange={(e) => updateIconItem(iconItem.id, 'y', e.target.value === '' ? '' : parseInt(e.target.value))}
                    min="0"
                    placeholder="0"
                  />
                </div>
                <div className="form-group">
                  <label>Genişlik:</label>
                  <input
                    type="number"
                    value={iconItem.width}
                    onChange={(e) => updateIconItem(iconItem.id, 'width', parseInt(e.target.value))}
                    min="1"
                    max="200"
                  />
                </div>
                <div className="form-group">
                  <label>Yükseklik:</label>
                  <input
                    type="number"
                    value={iconItem.height}
                    onChange={(e) => updateIconItem(iconItem.id, 'height', parseInt(e.target.value))}
                    min="1"
                    max="200"
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="settings-section">
            <h3>Barkod Bilgileri</h3>
            
            <button 
              className="btn btn-secondary add-text-btn"
              onClick={addNewBarcode}
            >
              + Barkod Ekle
            </button>

            {barcodeItems.map((barcodeItem) => (
              <div key={barcodeItem.id} className="text-item">
                <div className="text-item-header">
                  <span>Barkod #{barcodeItem.id}</span>
                  <button 
                    className="btn btn-danger delete-text-btn"
                    onClick={() => deleteBarcodeItem(barcodeItem.id)}
                  >
                    Sil
                  </button>
                </div>
                
                <div className="form-group">
                  <label>Sıra:</label>
                  <input
                    type="number"
                    value={barcodeItem.sira}
                    onChange={(e) => updateBarcodeItem(barcodeItem.id, 'sira', parseInt(e.target.value))}
                    min="1"
                  />
                </div>
                <div className="form-group">
                  <label>X Koordinatı:</label>
                  <input
                    type="number"
                    value={barcodeItem.x}
                    onChange={(e) => updateBarcodeItem(barcodeItem.id, 'x', e.target.value === '' ? '' : parseInt(e.target.value))}
                    min="0"
                    placeholder="0"
                  />
                </div>
                <div className="form-group">
                  <label>Y Koordinatı:</label>
                  <input
                    type="number"
                    value={barcodeItem.y}
                    onChange={(e) => updateBarcodeItem(barcodeItem.id, 'y', e.target.value === '' ? '' : parseInt(e.target.value))}
                    min="0"
                    placeholder="0"
                  />
                </div>
                <div className="form-group">
                  <label>Genişlik:</label>
                  <input
                    type="number"
                    value={barcodeItem.width}
                    onChange={(e) => updateBarcodeItem(barcodeItem.id, 'width', parseInt(e.target.value))}
                    min="1"
                    max="500"
                  />
                </div>
                <div className="form-group">
                  <label>Yükseklik:</label>
                  <input
                    type="number"
                    value={barcodeItem.height}
                    onChange={(e) => updateBarcodeItem(barcodeItem.id, 'height', parseInt(e.target.value))}
                    min="1"
                    max="200"
                  />
                </div>
                <div className="form-group">
                  <label>Format:</label>
                  <select
                    value={barcodeItem.format}
                    onChange={(e) => updateBarcodeItem(barcodeItem.id, 'format', e.target.value)}
                  >
                    <option value="code128">Code 128</option>
                    <option value="code39">Code 39</option>
                    <option value="qr">QR Code</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Data:</label>
                  <input
                    type="text"
                    value={barcodeItem.data}
                    onChange={(e) => updateBarcodeItem(barcodeItem.id, 'data', e.target.value)}
                    placeholder="Barkod verisi..."
                  />
                </div>
                <div className="form-group">
                  <label>Font Boyutu:</label>
                  <input
                    type="number"
                    value={barcodeItem.fontSize}
                    onChange={(e) => updateBarcodeItem(barcodeItem.id, 'fontSize', parseInt(e.target.value))}
                    min="8"
                    max="72"
                  />
                </div>
                <div className="form-group">
                  <label>Font Ailesi:</label>
                  <select
                    value={barcodeItem.fontFamily}
                    onChange={(e) => updateBarcodeItem(barcodeItem.id, 'fontFamily', e.target.value)}
                  >
                    <option value="Arial">Arial</option>
                    <option value="Times New Roman">Times New Roman</option>
                    <option value="Courier New">Courier New</option>
                    <option value="Helvetica">Helvetica</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Text Konum:</label>
                  <select
                    value={barcodeItem.textKonum}
                    onChange={(e) => updateBarcodeItem(barcodeItem.id, 'textKonum', e.target.value)}
                  >
                    <option value="alt">Alt</option>
                    <option value="ust">Üst</option>
                    <option value="sol">Sol</option>
                    <option value="sag">Sağ</option>
                    <option value="yok">Yok</option>
                  </select>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="preview-panel">
          <h3>Bitmap Önizlemesi</h3>
          <div className="preview-container">
            <div 
              className="bitmap-preview"
              style={{
                aspectRatio: `${widthPx} / ${heightPx}`,
                backgroundImage: logoUrl ? `url(${logoUrl})` : 'none',
                backgroundSize: 'contain',
                backgroundRepeat: 'no-repeat',
                backgroundPosition: 'center'
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

              {/* Icon Preview - Multiple icons */}
              {iconItems.map((iconItem) => (
                iconItem.iconFile && (
                  <img
                    key={iconItem.id}
                    src={iconItem.iconFile}
                    alt="Icon"
                    className="preview-icon"
                    style={{
                      position: 'absolute',
                      left: `${iconItem.x || 0}px`,
                      top: `${iconItem.y || 0}px`,
                      width: `${iconItem.width}px`,
                      height: `${iconItem.height}px`,
                      objectFit: 'contain'
                    }}
                  />
                )
              ))}

              {/* Barcode Preview - Multiple barcodes */}
              {barcodeItems.map((barcodeItem) => (
                barcodeItem.data && (
                  <div
                    key={barcodeItem.id}
                    className="preview-barcode"
                    style={{
                      position: 'absolute',
                      left: `${barcodeItem.x || 0}px`,
                      top: `${barcodeItem.y || 0}px`,
                      width: `${barcodeItem.width}px`,
                      height: `${barcodeItem.height}px`,
                      backgroundColor: '#000000',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#ffffff',
                      fontSize: `${barcodeItem.fontSize}px`,
                      fontFamily: barcodeItem.fontFamily,
                      border: '1px solid #333'
                    }}
                  >
                    {barcodeItem.data}
                  </div>
                )
              ))}
            </div>
            <div className="preview-info">
              <p>Boyut: {widthPx} x {heightPx} px</p>
              <p>Çözünürlük: {printer.dpi} DPI</p>
              <p>Oran: {printer.width}:{printer.height}</p>
              <p>Text Sayısı: {textItems.length}</p>
              <p>İkon Sayısı: {iconItems.length}</p>
              <p>Barkod Sayısı: {barcodeItems.length}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BitmapSettings;
