# Hera Printer Application - Kullanım Kılavuzu

## Kurulum

Bu uygulama Python kurulumu gerektirmez. Tek bir executable dosya olarak çalışır.

### Gereksinimler
- Windows 10/11
- Ağ bağlantısı (yazıcılar için)
- Port 8088 erişimi (web arayüzü için)

### Kurulum Adımları

1. `HeraPrinterApp.exe` dosyasını istediğiniz klasöre kopyalayın
2. Dosyaya çift tıklayarak uygulamayı başlatın
3. Uygulama başladığında otomatik olarak web tarayıcınızda açılacaktır
4. Eğer otomatik açılmazsa, tarayıcınızda `http://127.0.0.1:8088` adresine gidin

## Kullanım

### Ana Özellikler
- **Yazıcı Yönetimi**: TSC yazıcıları ekleme, düzenleme ve silme
- **Bitmap Ayarları**: Etiket tasarımı oluşturma ve düzenleme
- **Yazdırma**: Bitmap ve metin yazdırma

### Yazıcı Ekleme
1. Ana sayfada "Yazıcı Ekle" butonuna tıklayın
2. Yazıcının IP adresini, adını ve özelliklerini girin
3. "Kaydet" butonuna tıklayın

### Bitmap Tasarımı
1. "Bitmap Ayarları" sayfasına gidin
2. Metin, değer, ikon ve barkod öğeleri ekleyin
3. Tasarımınızı kaydedin

### Yazdırma
1. Ana sayfada yazıcı kartında "Yazdır" butonuna tıklayın
2. Yazdırma türünü seçin (bitmap veya metin)
3. "Yazdır" butonuna tıklayın

## Sorun Giderme

### Uygulama Başlamıyor
- Windows Defender veya antivirüs yazılımının dosyayı engellemediğinden emin olun
- Yönetici olarak çalıştırmayı deneyin

### Web Arayüzü Açılmıyor
- Port 8088'in başka bir uygulama tarafından kullanılmadığından emin olun
- Windows Firewall ayarlarını kontrol edin

### Yazıcı Bağlantı Sorunu
- Yazıcının ağa bağlı olduğundan emin olun
- IP adresinin doğru olduğunu kontrol edin
- Yazıcının TSC protokolünü desteklediğinden emin olun

## Teknik Destek

Herhangi bir sorun yaşadığınızda, lütfen aşağıdaki bilgileri toplayın:
- Windows sürümü
- Hata mesajları
- Yazıcı modeli ve IP adresi

## Sürüm Bilgisi
- Sürüm: 1.0
- Tarih: Ekim 2025
- Geliştirici: Hera Printer Application Team
