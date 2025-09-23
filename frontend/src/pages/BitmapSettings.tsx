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
  const [printStatus, setPrintStatus] = useState<string>('');
  const [settingsName, setSettingsName] = useState<string>('default');
  const [showSaveDialog, setShowSaveDialog] = useState<boolean>(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState<boolean>(false);

  // Logo'yu almak için fonksiyon (sadece component mount olduğunda)
  const fetchLogo = useCallback(async () => {
    try {
      // Sadece mevcut logo.bmp dosyasını al
      const blob = await apiService.getLogo();
      const url = URL.createObjectURL(blob);
      setLogoUrl(url);
    } catch (error) {
      console.error('Error fetching logo:', error);
    }
  }, []);

  // Otomatik kaydetme kaldırıldı - sadece manuel kaydetme kullanılacak

  // Print fonksiyonu
  const handlePrint = async () => {
    try {
      setPrintStatus('Yazdırılıyor...');
      
      // Mevcut ayarları kaydet ve bitmap oluştur
      const settings = {
        textItems,
        iconItems,
        barcodeItems
      };
      
      // Ayarları kaydet ve bitmap dosyasını oluştur
      await apiService.saveBitmapSettings(printer.ip, settingsName, settings);
      
      // Oluşturulan bitmap dosyasını yazdır
      const bmp_filename = `bitmap_${printer.ip}_${settingsName}.bmp`;
      await apiService.printToPrinter(printer.ip, {
        type: 'bmp',
        bmp_path: bmp_filename
      });
      
      setPrintStatus('Yazdırıldı!');
      setHasUnsavedChanges(false); // Artık kaydedildi
      setTimeout(() => setPrintStatus(''), 3000);
    } catch (error) {
      console.error('Print error:', error);
      setPrintStatus('Hata!');
      setTimeout(() => setPrintStatus(''), 3000);
    }
  };

  // Save settings fonksiyonu
  const handleSaveSettings = async () => {
    try {
      setSaveStatus('Kaydediliyor...');
      
      const settings = {
        textItems,
        iconItems,
        barcodeItems
      };
      
      console.log(`Saving settings for printer ${printer.ip} with name: ${settingsName}`);
      console.log('Settings to save:', settings);
      
      await apiService.saveBitmapSettings(printer.ip, settingsName, settings);
      
      console.log('Settings saved successfully');
      setSaveStatus('Kaydedildi!');
      setShowSaveDialog(false);
      setHasUnsavedChanges(false); // Artık kaydedildi
      setTimeout(() => setSaveStatus(''), 3000);
    } catch (error) {
      console.error('Save error:', error);
      setSaveStatus('Hata!');
      setTimeout(() => setSaveStatus(''), 3000);
    }
  };

  // Load settings fonksiyonu
  const handleLoadSettings = async (name: string = 'default') => {
    try {
      console.log(`Loading settings for printer ${printer.ip} with name: ${name}`);
      const response = await apiService.getBitmapSettings(printer.ip, name);
      console.log('Load settings response:', response);
      
      if (response.found && response.settings) {
        const settings = response.settings;
        console.log('Loaded settings:', settings);
        
        // Load text items
        if (settings.textItems && Array.isArray(settings.textItems)) {
          console.log('Loading text items:', settings.textItems);
          setTextItems(settings.textItems);
          setNextTextId(settings.textItems.length > 0 ? Math.max(...settings.textItems.map((item: any) => item.id)) + 1 : 1);
        } else {
          console.log('No text items found or not array');
          setTextItems([]);
          setNextTextId(1);
        }
        
        // Load icon items
        if (settings.iconItems && Array.isArray(settings.iconItems)) {
          console.log('Loading icon items:', settings.iconItems);
          setIconItems(settings.iconItems);
          setNextIconId(settings.iconItems.length > 0 ? Math.max(...settings.iconItems.map((item: any) => item.id)) + 1 : 1);
        } else {
          console.log('No icon items found or not array');
          setIconItems([]);
          setNextIconId(1);
        }
        
        // Load barcode items
        if (settings.barcodeItems && Array.isArray(settings.barcodeItems)) {
          console.log('Loading barcode items:', settings.barcodeItems);
          setBarcodeItems(settings.barcodeItems);
          setNextBarcodeId(settings.barcodeItems.length > 0 ? Math.max(...settings.barcodeItems.map((item: any) => item.id)) + 1 : 1);
        } else {
          console.log('No barcode items found or not array');
          setBarcodeItems([]);
          setNextBarcodeId(1);
        }
        
        setSaveStatus('Ayarlar yüklendi!');
        setHasUnsavedChanges(false); // Yeni ayarlar yüklendi
        setTimeout(() => setSaveStatus(''), 3000);
      } else {
        console.log('No settings found');
        setSaveStatus('Kayıtlı ayar bulunamadı');
        setTimeout(() => setSaveStatus(''), 3000);
      }
    } catch (error) {
      console.error('Load error:', error);
      setSaveStatus('Yükleme hatası!');
      setTimeout(() => setSaveStatus(''), 3000);
    }
  };

  // Component mount olduğunda logo'yu al ve ayarları yükle
  useEffect(() => {
    fetchLogo();
    // Sayfa açıldığında default ayarları yükle
    handleLoadSettings('default');
  }, []); // Sadece component mount olduğunda çalışsın

  const addNewText = () => {
    const newText: TextItem = {
      id: nextTextId,
      content: '',
      x: 0,
      y: 0,
      fontSize: 12,
      fontFamily: 'Arial'
    };
    console.log('Adding new text:', newText);
    setTextItems(prev => {
      const newItems = [...prev, newText];
      console.log('Updated textItems:', newItems);
      return newItems;
    });
    setNextTextId(prev => prev + 1);
  };

  const updateTextItem = (id: number, field: string, value: string | number) => {
    console.log(`Updating text item ${id}, field: ${field}, value: ${value}`);
    setTextItems(prev => {
      const updated = prev.map(item => 
        item.id === id ? { ...item, [field]: value } : item
      );
      console.log('Updated textItems after update:', updated);
      return updated;
    });
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
        <div className="header-status">
          {saveStatus && (
            <span className="save-status" style={{ 
              color: saveStatus === 'Kaydedildi' ? '#4CAF50' : '#f44336',
              marginRight: '1rem',
              fontSize: '0.9rem'
            }}>
              {saveStatus}
            </span>
          )}
          {printStatus && (
            <span className="print-status" style={{ 
              color: printStatus === 'Yazdırıldı!' ? '#4CAF50' : printStatus === 'Hata!' ? '#f44336' : '#2196F3',
              marginRight: '1rem',
              fontSize: '0.9rem'
            }}>
              {printStatus}
            </span>
          )}
          <button 
            onClick={handlePrint} 
            className="btn btn-primary print-btn"
            disabled={printStatus === 'Yazdırılıyor...'}
          >
            {printStatus === 'Yazdırılıyor...' ? '⏳ Yazdırılıyor...' : '🖨️ Yazdır'}
          </button>
          <button 
            onClick={() => setShowSaveDialog(true)} 
            className="btn btn-secondary save-btn"
            disabled={saveStatus === 'Kaydediliyor...'}
          >
            {saveStatus === 'Kaydediliyor...' ? '⏳ Kaydediliyor...' : '💾 Kaydet'}
          </button>
        </div>
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

      {/* Save Dialog */}
      {showSaveDialog && (
        <div className="save-dialog-overlay">
          <div className="save-dialog">
            <h3>Bitmap Ayarlarını Kaydet</h3>
            <div className="form-group">
              <label>Ayar Adı:</label>
              <input
                type="text"
                value={settingsName}
                onChange={(e) => setSettingsName(e.target.value)}
                placeholder="Örn: varsayılan, ürün etiketi"
              />
            </div>
            <div className="dialog-buttons">
              <button 
                onClick={handleSaveSettings}
                className="btn btn-primary"
                disabled={saveStatus === 'Kaydediliyor...' || !settingsName.trim()}
              >
                {saveStatus === 'Kaydediliyor...' ? 'Kaydediliyor...' : 'Kaydet'}
              </button>
              <button 
                onClick={() => setShowSaveDialog(false)}
                className="btn btn-secondary"
              >
                İptal
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BitmapSettings;
