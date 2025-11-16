from PIL import Image, ImageDraw, ImageFont
from barcode import Code128, EAN13, EAN8, Code39
from barcode.writer import ImageWriter
import qrcode
from io import BytesIO
import json
import os
import platform
import base64
from pathlib import Path
from typing import List, Dict, Any

class BitmapGenerator:
    """Bitmap generation class based on test.py example"""
    
    def __init__(self, width_mm: int = 100, height_mm: int = 29, dpi: int = 300, filename: str = "generated_bitmap.bmp"):
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.dpi = dpi
        self.filename = filename
        self.draw = None
        self.img = None
        self.text_layer = None
        self.text_draw = None

    def _get_system_font_paths(self):
        """Get common system font paths based on operating system"""
        try:
            system = platform.system().lower()
            font_paths = {}
            
            if system == "windows":
                windows_fonts = os.environ.get('WINDIR', 'C:\\Windows') + '\\Fonts\\'
                font_paths = {
                    'arial': os.path.join(windows_fonts, 'arial.ttf'),
                    'arial bold': os.path.join(windows_fonts, 'arialbd.ttf'),
                    'arial narrow': os.path.join(windows_fonts, 'ARIALN.TTF'),
                    'times': os.path.join(windows_fonts, 'times.ttf'),
                    'times new roman': os.path.join(windows_fonts, 'times.ttf'),
                    'courier': os.path.join(windows_fonts, 'cour.ttf'),
                    'courier new': os.path.join(windows_fonts, 'cour.ttf'),
                    'calibri': os.path.join(windows_fonts, 'calibri.ttf'),
                    'tahoma': os.path.join(windows_fonts, 'tahoma.ttf'),
                    'verdana': os.path.join(windows_fonts, 'verdana.ttf'),
                    'georgia': os.path.join(windows_fonts, 'georgia.ttf'),
                    'trebuchet ms': os.path.join(windows_fonts, 'trebuc.ttf')
                }
            elif system == "darwin":  # macOS
                font_paths = {
                    'arial': '/System/Library/Fonts/Arial.ttf',
                    'times': '/System/Library/Fonts/Times.ttc',
                    'times new roman': '/System/Library/Fonts/Times.ttc',
                    'courier': '/System/Library/Fonts/Courier New.ttf',
                    'courier new': '/System/Library/Fonts/Courier New.ttf',
                    'helvetica': '/System/Library/Fonts/Helvetica.ttc'
                }
            else:  # Linux and others
                font_paths = {
                    'arial': '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
                    'times': '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',
                    'times new roman': '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',
                    'courier': '/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf',
                    'courier new': '/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf',
                    'dejavu sans': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
                }
            
            return font_paths
        except Exception as e:
            print(f"Error getting system font paths: {e}")
            return {}

    def _resolve_font_path(self, font_family: str) -> str:
        """Resolve font family name to actual font file path"""
        try:
            # If it's already a full path, use it
            if os.path.isfile(font_family):
                return font_family
            
            # If it's a .ttf file in current directory, use it
            if font_family.endswith('.ttf') and os.path.isfile(font_family):
                return font_family
            
            # Get system font paths
            font_paths = self._get_system_font_paths()
            
            # Normalize font family name for lookup
            normalized_name = font_family.lower().strip()
            
            # Try direct lookup
            if normalized_name in font_paths:
                font_path = font_paths[normalized_name]
                if os.path.isfile(font_path):
                    return font_path
            
            # Try common variations
            variations = [
                normalized_name,
                normalized_name.replace(' ', ''),
                normalized_name + '.ttf',
                normalized_name.replace(' ', '') + '.ttf'
            ]
            
            for variation in variations:
                if variation in font_paths:
                    font_path = font_paths[variation]
                    if os.path.isfile(font_path):
                        return font_path
            
            # If not found, return None to use fallback
            return None
        except Exception as e:
            print(f"Error resolving font path: {e}")
            return None

    def _mm_to_px(self, mm: float) -> int:
        """Convert mm to pixels based on DPI"""
        try:
            dpmm = self.dpi / 25.4  # dots per mm
            return int(mm * dpmm)
        except Exception as e:
            print(f"Error converting mm to px: {e}")
            return 0

    def _px_to_mm(self, px: int) -> float:
        """Convert pixels to mm based on DPI"""
        dpmm = self.dpi / 25.4  # dots per mm
        return px / dpmm

    def _load_font(self, font_family: str = "Arial", font_size_px: int = 30):
        """Load font with improved resolution and fallbacks"""
        try:
            # First try to resolve the font family to a system font path
            font_path = self._resolve_font_path(font_family)
            
            if font_path:
                try:
                    print(f"Loading font: {font_path}")
                    return ImageFont.truetype(font_path, font_size_px)
                except (OSError, UnicodeDecodeError) as e:
                    print(f"Error loading font {font_path}: {e}")
            
            # Fallback to common system fonts
            fallback_fonts = []
            system = platform.system().lower()
            
            if system == "windows":
                fallback_fonts = [
                    os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'arial.ttf'),
                    os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'calibri.ttf'),
                    os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', 'tahoma.ttf')
                ]
            elif system == "darwin":
                fallback_fonts = [
                    '/System/Library/Fonts/Arial.ttf',
                    '/System/Library/Fonts/Helvetica.ttc'
                ]
            else:
                fallback_fonts = [
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                    '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
                ]
            
            # Try fallback fonts
            for fallback_path in fallback_fonts:
                try:
                    if os.path.isfile(fallback_path):
                        print(f"Using fallback font: {fallback_path}")
                        return ImageFont.truetype(fallback_path, font_size_px)
                except (OSError, UnicodeDecodeError) as e:
                    print(f"Error loading fallback font {fallback_path}: {e}")
                    continue
            
            # Last resort - use default font
            print("Using default PIL font")
            return ImageFont.load_default()
        except Exception as e:
            print(f"Error loading font: {e}")
            return None

    def set_label_scale(self):
        """Convert label dimensions from mm to pixels"""
        try:
            dpmm = self.dpi / 25.4  # dots per mm
            width_px = int(round(self.width_mm * dpmm))
            # Yükseklik için int() kullanarak 342.519... gibi değerlerin 342 olmasını sağlıyoruz
            height_px = int(self.height_mm * dpmm)
            return width_px, height_px, dpmm
        except Exception as e:
            print(f"Error setting label scale: {e}")
            return (0, 0, 0)

    def set_text(self, text: str, x: int, y: int, font_size_px: int, font_family: str = "Arial", rotation: int = 0):
        """Add text to bitmap at specified coordinates with rotation"""
        try:
            font = self._load_font(font_family, font_size_px)

            if self.img is None:
                raise ValueError("Bitmap not initialized. Call bitmap_init() before adding text.")

            if self.text_layer is None or self.text_draw is None:
                self.text_layer = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
                self.text_draw = ImageDraw.Draw(self.text_layer)
            
            if rotation == 0:
                # Normal text (no rotation)
                self.text_draw.text((x, y), text, font=font, fill=(0, 0, 0, 255))  # Black text with transparency
                bbox = self.text_draw.textbbox((x, y), text, font=font)
            else:
                # Get text bounding box to calculate center
                bbox = self.text_draw.textbbox((x, y), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Create a temporary image just for the text
                # Extra padding is added to avoid clipping when rotated (especially at 90/270 degrees)
                padding = 40
                temp_img = Image.new(
                    "RGBA",
                    (text_width + padding, text_height + padding),
                    (0, 0, 0, 0)
                )  # Transparent background
                temp_draw = ImageDraw.Draw(temp_img)
                
                # Draw text on temporary image (centered)
                temp_x = (temp_img.width - text_width) // 2
                temp_y = (temp_img.height - text_height) // 2
                temp_draw.text((temp_x, temp_y), text, font=font, fill=(0, 0, 0, 255))  # Black text with transparency
                
                # Rotate the temporary image around its center
                # expand=True => canvas genişler, metnin köşeleri kesilmez
                rotated_img = temp_img.rotate(rotation, expand=True, fillcolor=(0, 0, 0, 0))
                
                # Calculate the position to paste the rotated text
                # So that the center of the rotated text is at (x, y)
                paste_x = x - rotated_img.width // 2
                paste_y = y - rotated_img.height // 2
                
                # Paste the rotated text onto the main image
                self.text_layer.paste(rotated_img, (paste_x, paste_y), rotated_img)
                
                # Update bounding box for rotated text
                bbox = (paste_x, paste_y, paste_x + rotated_img.width, paste_y + rotated_img.height)
            
            print(f"Text '{text}' with rotation {rotation}° at ({x}, {y}) bbox: {bbox}")
            return bbox
        except Exception as e:
            print(f"Error setting text: {e}")
            return (x, y, x, y)

    def set_barcode(self, data: str, x: int, y: int, barcode_type: str = "code128", width_px: int = None, height_px: int = None):
        """Add barcode to bitmap at specified coordinates"""
        try:
            btype = barcode_type.lower()
            
            # QR kod desteği
            if btype == "qr":
                # QR kod oluştur
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(data)
                qr.make(fit=True)
                
                # QR kod görselini oluştur
                barcode_img = qr.make_image(fill_color="black", back_color="white")
                
                # 1-bit dönüştürme
                barcode_img = barcode_img.convert("1")
                
                # İstenirse yeniden boyutlandır
                if width_px or height_px:
                    cw, ch = barcode_img.size
                    nw = width_px if width_px else cw
                    nh = height_px if height_px else ch
                    barcode_img = barcode_img.resize((nw, nh), Image.Resampling.LANCZOS)
                
                # Ana görsele yapıştır
                self.img.paste(barcode_img, (x, y))
                bbox = (x, y, x + barcode_img.width, y + barcode_img.height)
                print(f"QR Code '{data}' bbox: {bbox}")
                return bbox
            
            # Diğer barkod tipleri (code128, ean13, ean8, code39)
            barcode_classes = {
                "code128": Code128,
                "ean13": EAN13,
                "ean8": EAN8,
                "code39": Code39
            }
            
            if btype not in barcode_classes:
                raise ValueError(f"Unsupported barcode type: {barcode_type}")

            # 2) (Önemli) EAN13 veri doğrulama: 12 rakam olmalı (checksum'ı kütüphane ekler)
            if btype == "ean13":
                digits = "".join(ch for ch in data if ch.isdigit())
                if len(digits) < 12:
                    raise ValueError(f"EAN13 needs 12 digits (got {len(digits)}). Data: '{data}'")
                data = digits[:12]
            
            # EAN8 veri doğrulama: 7 rakam olmalı (checksum'ı kütüphane ekler)
            if btype == "ean8":
                digits = "".join(ch for ch in data if ch.isdigit())
                if len(digits) < 7:
                    raise ValueError(f"EAN8 needs 7 digits (got {len(digits)}). Data: '{data}'")
                data = digits[:7]

            # 3) Writer oluştur (fonta dokunmuyoruz)
            writer = ImageWriter()
            writer.write_text = False           # yazıyı kapat (ama font_path AYARLAMA)
            # writer.font_path = ...  # hiç set ETME

            # mm ayarları
            writer.module_width = 0.2
            writer.module_height = 10.0
            if height_px:
                writer.module_height = self._px_to_mm(height_px)
            if width_px:
                writer.module_width = max(0.1, self._px_to_mm(width_px) / 50)

            # 4) Barcode objesi ve doğrudan PIL Image üretimi
            # Code39 için checksum'ı kapatıyoruz (sona eklenen kontrol karakterini önlemek için)
            if btype == "code39":
                barcode_obj = barcode_classes[btype](data, writer=writer, add_checksum=False)
            else:
                barcode_obj = barcode_classes[btype](data, writer=writer)

            # KRİTİK: write() + BytesIO yerine render() kullan.
            # render() ile direkt PIL.Image döner ve options ile yazıyı kapatırız.
            barcode_img = barcode_obj.render(writer_options={"write_text": False})

            # 5) 1-bit dönüştürme
            barcode_img = barcode_img.convert("1")

            # 6) İstenirse yeniden boyutlandır
            if width_px or height_px:
                cw, ch = barcode_img.size
                nw = width_px if width_px else cw
                nh = height_px if height_px else ch
                barcode_img = barcode_img.resize((nw, nh))
            

            # 7) Ana görsele yapıştır
            self.img.paste(barcode_img, (x, y))
            bbox = (x, y, x + barcode_img.width, y + barcode_img.height)
            print(f"Barcode '{data}' ({barcode_type}) bbox: {bbox}")
            return bbox

        except Exception as e:
            print(f"Error creating barcode: {e}")
            return (x, y, x, y)

    def set_image(self, image_path: str, x: int, y: int, width_px: int = None, height_px: int = None):
        """Add image to bitmap at specified coordinates"""
        try:
            # Load image
            img = Image.open(image_path)

            # ÖNCE yüksek çözünürlüklü olarak resize et, SONRA 1-bit'e çevir
            if width_px or height_px:
                current_width, current_height = img.size
                
                if width_px and height_px:
                    # Both dimensions given - direct resize
                    img = img.resize((width_px, height_px))
                elif width_px:
                    # Only width given - proportional resize
                    ratio = width_px / current_width
                    new_height = int(current_height * ratio)
                    img = img.resize((width_px, new_height))
                elif height_px:
                    # Only height given - proportional resize
                    ratio = height_px / current_height
                    new_width = int(current_width * ratio)
                    img = img.resize((new_width, height_px))

            # En son, net ve keskin kenarlar için 1-bit'e çevir
            #img = img.convert("1")
            
            # Paste to main image
            self.img.paste(img, (x, y))
            
            # Calculate bounding box
            bbox = (x, y, x + img.width, y + img.height)
            print(f"Image '{image_path}' bbox: {bbox}")
            
            return bbox
            
        except Exception as e:
            print(f"Error loading image: {e}")
            return (x, y, x, y)  # Return empty bbox

    def set_icon_from_base64(self, base64_data: str, x: int, y: int, width_px: int = None, height_px: int = None):
        """Add icon from base64 data to bitmap at specified coordinates"""
        try:
            # Remove data URL prefix if present (e.g., "data:image/png;base64,")
            if base64_data.startswith('data:'):
                base64_data = base64_data.split(',')[1]
            
            # Decode base64 data
            image_data = base64.b64decode(base64_data)
            
            # Create image from bytes
            img = Image.open(BytesIO(image_data))

            # Resize only if valid dimensions are provided (önce resize, sonra 1-bit)
            if (width_px and width_px > 0) or (height_px and height_px > 0):
                current_width, current_height = img.size
                
                if width_px and height_px and width_px > 0 and height_px > 0:
                    # Both dimensions given - direct resize
                    img = img.resize((width_px, height_px), Image.Resampling.LANCZOS)
                elif width_px and width_px > 0:
                    # Only width given - proportional resize
                    ratio = width_px / current_width
                    new_height = int(current_height * ratio)
                    img = img.resize((width_px, new_height), Image.Resampling.LANCZOS)
                elif height_px and height_px > 0:
                    # Only height given - proportional resize
                    ratio = height_px / current_height
                    new_width = int(current_width * ratio)
                    img = img.resize((new_width, height_px), Image.Resampling.LANCZOS)

            # En son, 1-bit'e çevir (siyah/beyaz, daha keskin)
            #img = img.convert("1")
            
            # Paste to main image
            self.img.paste(img, (x, y))
            
            # Calculate bounding box
            bbox = (x, y, x + img.width, y + img.height)
            print(f"Icon from base64 bbox: {bbox}")
            
            return bbox
            
        except Exception as e:
            print(f"Error loading icon from base64: {e}")
            return (x, y, x, y)  # Return empty bbox

    def bitmap_init(self):
        """Initialize bitmap with label dimensions"""
        try:
            # Calculate label dimensions
            W, H, dpmm = self.set_label_scale()
            
            # Create Image and Draw objects - RGB format for better text visibility
            self.img = Image.new("RGB", (W, H), (255, 255, 255))  # RGB, white background
            self.draw = ImageDraw.Draw(self.img)
            self.text_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            self.text_draw = ImageDraw.Draw(self.text_layer)
        except Exception as e:
            print(f"Error initializing bitmap: {e}")

    def bitmap_finish(self):
        """Save bitmap to file"""
        try:
            if self.text_layer is not None:
                base_rgba = self.img.convert("RGBA")
                combined = Image.alpha_composite(base_rgba, self.text_layer)
                self.img = combined.convert("RGB")
                self.text_layer = None
                self.text_draw = None

            # Convert to high-quality 1-bit (monochrome) for printer compatibility
            # 1) Her şeyi gri tona çevir (0-255)
            
            gray_img = self.img.convert("L")

            # 2) Kontrollü threshold ile (dithersiz) 1-bit'e çevir
            #    Daha yüksek eşik (örn. 200) ince çizgileri korur, halo'yu azaltır.
            threshold = 200
            self.img = gray_img.point(lambda x: 0 if x < threshold else 255, "1")
            
            self.img.save(self.filename, format="BMP")
            print(f"Bitmap saved as {self.filename}")
        except Exception as e:
            print(f"Error saving bitmap: {e}")

    def create_from_settings(self, settings_data: List[Dict[str, Any]]):
        """Create bitmap from settings data (similar to test.py message format)"""
        try:
            self.bitmap_init()
            
            for item in settings_data:
                if item["type"] == "text":
                    self.set_text(
                        item["data"]["text"], 
                        item["data"]["x"], 
                        item["data"]["y"], 
                        item["data"]["font_size"], 
                        item["data"].get("font_family", "Arial")
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
        except Exception as e:
            print(f"Error creating bitmap from settings: {e}")

    def create_from_frontend_data(self, text_items: List[Dict], value_items: List[Dict], icon_items: List[Dict], barcode_items: List[Dict]):
        """Create bitmap from frontend data format"""
        try:
            self.bitmap_init()
            
            # Process text items
            for text_item in text_items:
                if text_item.get("content"):
                    self.set_text(
                        text_item["content"],
                        text_item.get("x", 0),
                        text_item.get("y", 0),
                        text_item.get("fontSize", 12),
                        text_item.get("fontFamily", "Arial"),
                        text_item.get("rotation", 0)
                    )
            
            # Process value items
            for value_item in value_items:
                value_type = value_item.get("type", "text")
                
                if value_type == "text" and value_item.get("content"):
                    self.set_text(
                        value_item["content"],
                        value_item.get("x", 0),
                        value_item.get("y", 0),
                        value_item.get("fontSize", 12),
                        value_item.get("fontFamily", "Arial"),
                        value_item.get("rotation", 0)
                    )
                elif value_type == "image" and value_item.get("imageFile"):
                    print(f"Processing value image item: x={value_item.get('x', 0)}, y={value_item.get('y', 0)}, "
                          f"width={value_item.get('imageWidth', 0)}, height={value_item.get('imageHeight', 0)}")
                    
                    self.set_icon_from_base64(
                        value_item["imageFile"],
                        value_item.get("x", 0),
                        value_item.get("y", 0),
                        value_item.get("imageWidth", 0),
                        value_item.get("imageHeight", 0)
                    )
            
            # Process icon items
            for icon_item in icon_items:
                if icon_item.get("iconFile"):
                    print(f"Processing icon item: x={icon_item.get('x', 0)}, y={icon_item.get('y', 0)}, "
                        f"width={icon_item.get('width', 0)}, height={icon_item.get('height', 0)}")
                    # If no width/height specified, keep original dimensions
                    width = icon_item.get("width")
                    height = icon_item.get("height")
                    
                    self.set_icon_from_base64(
                        icon_item["iconFile"],
                        icon_item.get("x", 0),
                        icon_item.get("y", 0),
                        width,
                        height
                    )
                else:
                    print("Icon item has no iconFile data")
            
            # Process barcode items
            for barcode_item in barcode_items:
                if barcode_item.get("data"):
                    print(f"Processing barcode item: data='{barcode_item.get('data', '')}', "
                        f"format={barcode_item.get('format', 'code128')}, "
                        f"x={barcode_item.get('x', 0)}, y={barcode_item.get('y', 0)}")
                    self.set_barcode(
                        barcode_item["data"],
                        barcode_item.get("x", 0),
                        barcode_item.get("y", 0),
                        barcode_item.get("format", "code128"),
                        barcode_item.get("width", None),
                        barcode_item.get("height", None)
                    )
                else:
                    print("Barcode item has no data")
            
            self.bitmap_finish()
        except Exception as e:
            print(f"Error creating bitmap from frontend data: {e}")

