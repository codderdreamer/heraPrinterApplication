from PIL import Image, ImageDraw, ImageFont
from barcode import Code128, EAN13, Code39
from barcode.writer import ImageWriter
from io import BytesIO


'''
img = Image.new("1", (200, 100), 1)  # 1 = siyah-beyaz mod, 1=white
draw = ImageDraw.Draw(img)
draw.rectangle([10, 10, 190, 90], outline=0, width=2)  # 0=black
draw.text((20, 40), "TSC", fill=0)
img.save("logo_bw.bmp", format="BMP")
'''

# --- Yazıcı sabitleri (TSC TE310) ---
DOTS_PER_MM = 12           # 12 dots/mm (≈300 DPI)
MAX_WIDTH_MM = 105.7
MAX_LENGTH_MM = 11430

class CreateBitmap:
    def __init__(self, message, width_mm = 100, height_mm = 29, dpi=300, filename="logo.bmp"):
        self.message = message
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.dpi = dpi
        self.filename = filename
        self.draw = None
        self.img = None


    def _mm_to_px(self, mm: float, dpi: float = None) -> int:
        if dpi is None:
            dpi = self.dpi  # Sınıfın kendi dpi değerini kullan
        dpmm = dpi / 25.4  # convert DPI to dots per mm
        return int(mm * dpmm)  # convert mm to pixels based on DPI
    
    def _px_to_mm(self, px: int, dpi: float = None) -> float:
        if dpi is None:
            dpi = self.dpi  # Sınıfın kendi dpi değerini kullan
        dpmm = dpi / 25.4  # convert DPI to dots per mm
        return px / dpmm  # convert pixels to mm based on DPI

    def _load_font(self, font_path="arial.ttf", font_size_px=30):
        try:
            return ImageFont.truetype(font_path, font_size_px)
        except OSError:
            try:
                return ImageFont.truetype("DejaVuSans.ttf", font_size_px)
            except OSError:
                return ImageFont.load_default()

    def set_label_scale(self):
        """
        Etiket boyutlarını mm'den pixel'e çevirir.
        Returns: (width_px, height_px, dpmm)
        """
        dpmm = self.dpi / 25.4  # dots per mm
        width_px = int(round(self.width_mm * dpmm))
        height_px = int(round(self.height_mm * dpmm))
        return width_px, height_px, dpmm

    def set_text(self, text, x, y, font_size_px, font_path="arial.ttf"):
        """
        Belirtilen koordinatlara metin yazar ve textbbox bilgisini döndürür.
        Args:
            text (str): Yazılacak metin
            x (int): X koordinatı (pixel)
            y (int): Y koordinatı (pixel)
            font_size_px (int): Font boyutu pixel cinsinden
            font_path (str): Font dosya yolu (varsayılan: arial.ttf)
        Returns:
            tuple: Metnin bounding box koordinatları (left, top, right, bottom)
        """
        font = self._load_font(font_path, font_size_px)
        self.draw.text((x, y), text, font=font, fill=0)
        bbox = self.draw.textbbox((x, y), text, font=font)
        print(f"Text '{text}' bbox: {bbox}")
        return bbox

    def set_barcode(self, data, x, y, barcode_type="code128", width_px=None, height_px=None):
        """
        Belirtilen koordinatlara barkod ekler.
        Args:
            data (str): Barkod verisi
            x (int): X koordinatı (pixel)
            y (int): Y koordinatı (pixel)
            barcode_type (str): Barkod tipi (code128, ean13, code39)
            width_px (int): Barkod genişliği pixel cinsinden
            height_px (int): Barkod yüksekliği pixel cinsinden
        Returns:
            tuple: Barkodun bounding box koordinatları (left, top, right, bottom)
        """
        # Barkod tipini seç
        barcode_classes = {
            "code128": Code128,
            "ean13": EAN13,
            "code39": Code39
        }
        
        if barcode_type.lower() not in barcode_classes:
            raise ValueError(f"Desteklenmeyen barkod tipi: {barcode_type}")
        
        # Barkod oluştur
        barcode_class = barcode_classes[barcode_type.lower()]
        
        # ImageWriter ile barkod oluştur
        writer = ImageWriter()
        
        # Boyut ayarları - pixel'den mm'ye çevir
        if height_px:
            # Barkod yüksekliği için module_height ayarla (pixel'i mm'ye çevir)
            writer.module_height = self._px_to_mm(height_px)
        if width_px:
            # Barkod genişliği için module_width ayarla (daha ince çizgiler)
            writer.module_width = 0.2  # mm cinsinden daha ince modül genişliği
        
        # Barkod oluştur
        barcode = barcode_class(data, writer=writer)
        
        # BytesIO'ya kaydet
        buffer = BytesIO()
        barcode.write(buffer)
        buffer.seek(0)
        
        # PIL Image olarak yükle
        barcode_img = Image.open(buffer)
        
        # Siyah-beyaz (1-bit) moduna çevir
        barcode_img = barcode_img.convert("1")
        
        # Kullanıcının istediği boyutlara yeniden boyutlandır
        if width_px or height_px:
            current_width, current_height = barcode_img.size
            new_width = width_px if width_px else current_width
            new_height = height_px if height_px else current_height
            barcode_img = barcode_img.resize((new_width, new_height))
        
        # Ana görüntüye yapıştır
        self.img.paste(barcode_img, (x, y))
        
        # Bounding box hesapla
        bbox = (x, y, x + barcode_img.width, y + barcode_img.height)
        print(f"Barcode '{data}' ({barcode_type}) bbox: {bbox}")
        
        return bbox
    def set_image(self, image_path, x, y, width_px=None, height_px=None):
        """
        Etikete resim ekler
        
        Args:
            image_path (str): Resim dosyasının yolu
            x (int): X koordinatı (pixel)
            y (int): Y koordinatı (pixel)
            width_px (int, optional): Hedef genişlik (pixel)
            height_px (int, optional): Hedef yükseklik (pixel)
        
        Returns:
            tuple: Resmin bounding box'ı (x, y, x+width, y+height)
        """
        try:
            # Resmi yükle
            img = Image.open(image_path)
            
            # Siyah-beyaz (1-bit) moduna çevir
            img = img.convert("1")
            
            # Boyutlandırma
            if width_px or height_px:
                current_width, current_height = img.size
                
                if width_px and height_px:
                    # Her iki boyut da verilmişse direkt yeniden boyutlandır
                    img = img.resize((width_px, height_px))
                elif width_px:
                    # Sadece genişlik verilmişse orantılı yeniden boyutlandır
                    ratio = width_px / current_width
                    new_height = int(current_height * ratio)
                    img = img.resize((width_px, new_height))
                elif height_px:
                    # Sadece yükseklik verilmişse orantılı yeniden boyutlandır
                    ratio = height_px / current_height
                    new_width = int(current_width * ratio)
                    img = img.resize((new_width, height_px))
            
            # Ana görüntüye yapıştır
            self.img.paste(img, (x, y))
            
            # Bounding box hesapla
            bbox = (x, y, x + img.width, y + img.height)
            print(f"Image '{image_path}' bbox: {bbox}")
            
            return bbox
            
        except Exception as e:
            print(f"Resim yüklenirken hata oluştu: {e}")
            return (x, y, x, y)  # Boş bbox döndür

    def bitmap_init(self):
        # Etiket boyutlarını hesapla
        W, H, dpmm = self.set_label_scale()
        
        # Image ve Draw nesnelerini oluştur
        self.img = Image.new("1", (W, H), 1)  # 1=mode (1-bit), 1=white
        self.draw = ImageDraw.Draw(self.img)

    def bitmap_finish(self):
        # Kaydet
        self.img.save(self.filename, format="BMP")

    def create(self):
        self.bitmap_init()
        for item in self.message:
            if item["type"] == "text":
                self.set_text(
                    item["data"]["text"], 
                    item["data"]["x"], 
                    item["data"]["y"], 
                    item["data"]["font_size"], 
                    item["data"]["font_path"]
                )
            elif item["type"] == "barcode":
                self.set_barcode(
                    item["data"]["data"], 
                    item["data"]["x"], 
                    item["data"]["y"], 
                    item["data"].get("barcode_type", "code128"),
                    item["data"].get("width_px", None),
                    item["data"].get("height_px", None)
                )
            elif item["type"] == "image":
                self.set_image(
                    item["data"]["image_path"], 
                    item["data"]["x"], 
                    item["data"]["y"], 
                    item["data"].get("width_px", None),
                    item["data"].get("height_px", None)
                )
        self.bitmap_finish()
        
        
message = [ 
        # Logo (üst-sol) - Fotoğraf olarak
        {
            "type" : "image",
            "data" : {
                        "image_path":r"C:\Users\syucedag\OneDrive - Dias Bilişim ve Teknoloji Hizmetleri A.Ş\Desktop\ibrahim\foto\logo.png",
                        "x":20,
                        "y":10,
                        "width_px":216,
                        "height_px":90
                    }
        },
        
        # Sol sütun - Ürün bilgileri
        {
            "type" : "text",
            "data" : {
                        "text":"Product Code",
                        "x":10,
                        "y":102,
                        "font_size":27,
                        "font_path":"arialbd.ttf"
                    }
        },
        {
            "type" : "text",
            "data" : {
                        "text":":",
                        "x":195,
                        "y":102,
                        "font_size":27,
                        "font_path":"arialbd.ttf"
                    }
        },
        {
            "type" : "text",
            "data" : {
                        "text":"HC022301312",
                        "x":205,
                        "y":104,
                        "font_size":25,
                        "font_path":"arialbd.ttf"
                    }
        },
        
        # Model
        {
            "type" : "text",
            "data" : {
                        "text":"Model",
                        "x":10,
                        "y":134,
                        "font_size":27,
                        "font_path":"arialbd.ttf"
                    }
        },
        {
            "type" : "text",
            "data" : {
                        "text":":",
                        "x":195,
                        "y":134,
                        "font_size":27,
                        "font_path":"arialbd.ttf"
                    }
        },
        {
            "type" : "text",
            "data" : {
                        "text":"ChargePack® BS33A Smart+ Type2 Socket",
                        "x":205,
                        "y":136,
                        "font_size":25,
                        "font_path":"arialbd.ttf"
                    }
        },
        
        # System
        {
            "type" : "text",
            "data" : {
                        "text":"System",
                        "x":10,
                        "y":166,
                        "font_size":27,
                        "font_path":"arialbd.ttf"
                    }
        },
        {
            "type" : "text",
            "data" : {
                        "text":":",
                        "x":195,
                        "y":166,
                        "font_size":27,
                        "font_path":"arialbd.ttf"
                    }
        },
        {
            "type" : "text",
            "data" : {
                        "text":"RFID, Wifi, Ethernet, Bluetooth, 4G whit MID METER",
                        "x":205,
                        "y":168,
                        "font_size":25,
                        "font_path":"arialbd.ttf"
                    }
        },
        
        # Rated Voltage
        {
            "type" : "text",
            "data" : {
                        "text":"Rated Voltage",
                        "x":10,
                        "y":198,
                        "font_size":27,
                        "font_path":"arialbd.ttf"
                    }
        },
        {
            "type" : "text",
            "data" : {
                        "text":":",
                        "x":195,
                        "y":198,
                        "font_size":27,
                        "font_path":"arialbd.ttf"
                    }
        },
        {
            "type" : "text",
            "data" : {
                        "text":"Three Phase 340-460 VAC 50-60 Hz",
                        "x":205,
                        "y":200,
                        "font_size":25,
                        "font_path":"arialbd.ttf"
                    }
        },
        
        # Rated Power
        {
            "type" : "text",
            "data" : {
                        "text":"Rated Power",
                        "x":10,
                        "y":230,
                        "font_size":27,
                        "font_path":"arialbd.ttf"
                    }
        },
        {
            "type" : "text",
            "data" : {
                        "text":":",
                        "x":195,
                        "y":230,
                        "font_size":27,
                        "font_path":"arialbd.ttf"
                    }
        },
        {
            "type" : "text",
            "data" : {
                        "text":"Max 32A - 22kW",
                        "x":205,
                        "y":232,
                        "font_size":25,
                        "font_path":"arialbd.ttf"
                    }
        },
        
        # Alt-sol - Firma bilgileri
        {
            "type" : "text",
            "data" : {
                        "text":"Hera Charge Elektronik A.Ş.",
                        "x":10,
                        "y":265,
                        "font_size":27,
                        "font_path":"arialbd.ttf"
                    }
        },
        {
            "type" : "text",
            "data" : {
                        "text":"www.heracharge.com",
                        "x":10,
                        "y":295,
                        "font_size":27,
                        "font_path":"arialbd.ttf"
                    }
        },
        
        # Sağ üst - MAC/IMEI bilgileri
        {
            "type" : "text",
            "data" : {
                        "text":"BT Mac : E8:51:9E:FD:5E:80",
                        "x":755,
                        "y":20,
                        "font_size":26,
                        "font_path":"arialbd.ttf"
                    }
        },
        {
            "type" : "text",
            "data" : {
                        "text":"Lan Mac: 1E:23:D4:54:F3:78",
                        "x":755,
                        "y":55,
                        "font_size":26,
                        "font_path":"arialbd.ttf"
                    }
        },
        {
            "type" : "text",
            "data" : {
                        "text":"IMEI   : 867395071672212",
                        "x":755,
                        "y":90,
                        "font_size":26,
                        "font_path":"arialbd.ttf"
                    }
        },
        
        # Sağ üst köşe - Tarih
        {
            "type" : "text",
            "data" : {
                        "text":"Date: 18/03/2025",
                        "x":920,
                        "y":190,
                        "font_size":25,
                        "font_path":"arialbd.ttf"
                    }
        },
        
        # Alt orta - İkonlar (M24, CE, vb.) - aşağı ve sağa kaydırıldı
        {
            "type" : "image",
            "data" : {
                        "image_path":r"C:\Users\syucedag\OneDrive - Dias Bilişim ve Teknoloji Hizmetleri A.Ş\Desktop\ibrahim\foto\m24_icon.png",
                        "x":400,
                        "y":260,
                        "width_px":84,
                        "height_px":70
                    }
        },
        {
            "type" : "image",
            "data" : {
                        "image_path":r"C:\Users\syucedag\OneDrive - Dias Bilişim ve Teknoloji Hizmetleri A.Ş\Desktop\ibrahim\foto\square_icon.png",
                        "x":490,
                        "y":260,
                        "width_px":56,
                        "height_px":56
                    }
        },
        {
            "type" : "image",
            "data" : {
                        "image_path":r"C:\Users\syucedag\OneDrive - Dias Bilişim ve Teknoloji Hizmetleri A.Ş\Desktop\ibrahim\foto\ce_icon.png",
                        "x":555,
                        "y":260,
                        "width_px":70,
                        "height_px":56
                    }
        },
        {
            "type" : "image",
            "data" : {
                        "image_path":r"C:\Users\syucedag\OneDrive - Dias Bilişim ve Teknoloji Hizmetleri A.Ş\Desktop\ibrahim\foto\recycle_icon.png",
                        "x":630,
                        "y":260,
                        "width_px":56,
                        "height_px":56
                    }
        },

        # Sağ alt - Barkod
        {
            "type" : "barcode",
            "data" : {
                        "data":"10114847068",
                        "x":760,
                        "y":220,
                        "barcode_type":"code128",
                        "width_px":360,
                        "height_px":100
                    }
        },
        
        # Sağ alt köşe - Made in Türkiye
        {
            "type" : "text",
            "data" : {
                        "text":"Made in Türkiye",
                        "x":970,
                        "y":320,
                        "font_size":14,
                        "font_path":"arialbd.ttf"
                    }
        }

]

# --- Test: 100x30 mm---
create_label = CreateBitmap(message)
create_label.create()