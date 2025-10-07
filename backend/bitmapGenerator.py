from PIL import Image, ImageDraw, ImageFont
from barcode import Code128, EAN13, Code39
from barcode.writer import ImageWriter
from io import BytesIO
import json
import os
import platform
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

    def _get_system_font_paths(self):
        """Get common system font paths based on operating system"""
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

    def _resolve_font_path(self, font_family: str) -> str:
        """Resolve font family name to actual font file path"""
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

    def _mm_to_px(self, mm: float) -> int:
        """Convert mm to pixels based on DPI"""
        dpmm = self.dpi / 25.4  # dots per mm
        return int(mm * dpmm)

    def _px_to_mm(self, px: int) -> float:
        """Convert pixels to mm based on DPI"""
        dpmm = self.dpi / 25.4  # dots per mm
        return px / dpmm

    def _load_font(self, font_family: str = "Arial", font_size_px: int = 30):
        """Load font with improved resolution and fallbacks"""
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

    def set_label_scale(self):
        """Convert label dimensions from mm to pixels"""
        dpmm = self.dpi / 25.4  # dots per mm
        width_px = int(round(self.width_mm * dpmm))
        height_px = int(round(self.height_mm * dpmm))
        return width_px, height_px, dpmm

    def set_text(self, text: str, x: int, y: int, font_size_px: int, font_family: str = "Arial"):
        """Add text to bitmap at specified coordinates"""
        font = self._load_font(font_family, font_size_px)
        self.draw.text((x, y), text, font=font, fill=0)
        bbox = self.draw.textbbox((x, y), text, font=font)
        print(f"Text '{text}' bbox: {bbox}")
        return bbox

    def set_barcode(self, data: str, x: int, y: int, barcode_type: str = "code128", width_px: int = None, height_px: int = None):
        """Add barcode to bitmap at specified coordinates"""
        # Barcode type selection
        barcode_classes = {
            "code128": Code128,
            "ean13": EAN13,
            "code39": Code39
        }
        
        if barcode_type.lower() not in barcode_classes:
            raise ValueError(f"Unsupported barcode type: {barcode_type}")
        
        # Create barcode
        barcode_class = barcode_classes[barcode_type.lower()]
        
        # ImageWriter for barcode creation
        writer = ImageWriter()
        
        # Size settings - convert pixels to mm
        if height_px:
            writer.module_height = self._px_to_mm(height_px)
        if width_px:
            writer.module_width = 0.2  # mm for thinner module width
        
        # Create barcode
        barcode = barcode_class(data, writer=writer)
        
        # Save to BytesIO
        buffer = BytesIO()
        barcode.write(buffer)
        buffer.seek(0)
        
        # Load as PIL Image
        barcode_img = Image.open(buffer)
        
        # Convert to black-white (1-bit) mode
        barcode_img = barcode_img.convert("1")
        
        # Resize to desired dimensions
        if width_px or height_px:
            current_width, current_height = barcode_img.size
            new_width = width_px if width_px else current_width
            new_height = height_px if height_px else current_height
            barcode_img = barcode_img.resize((new_width, new_height))
        
        # Paste to main image
        self.img.paste(barcode_img, (x, y))
        
        # Calculate bounding box
        bbox = (x, y, x + barcode_img.width, y + barcode_img.height)
        print(f"Barcode '{data}' ({barcode_type}) bbox: {bbox}")
        
        return bbox

    def set_image(self, image_path: str, x: int, y: int, width_px: int = None, height_px: int = None):
        """Add image to bitmap at specified coordinates"""
        try:
            # Load image
            img = Image.open(image_path)
            
            # Convert to black-white (1-bit) mode
            img = img.convert("1")
            
            # Resize
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
            
            # Paste to main image
            self.img.paste(img, (x, y))
            
            # Calculate bounding box
            bbox = (x, y, x + img.width, y + img.height)
            print(f"Image '{image_path}' bbox: {bbox}")
            
            return bbox
            
        except Exception as e:
            print(f"Error loading image: {e}")
            return (x, y, x, y)  # Return empty bbox

    def bitmap_init(self):
        """Initialize bitmap with label dimensions"""
        # Calculate label dimensions
        W, H, dpmm = self.set_label_scale()
        
        # Create Image and Draw objects
        self.img = Image.new("1", (W, H), 1)  # 1=mode (1-bit), 1=white
        self.draw = ImageDraw.Draw(self.img)

    def bitmap_finish(self):
        """Save bitmap to file"""
        self.img.save(self.filename, format="BMP")

    def create_from_settings(self, settings_data: List[Dict[str, Any]]):
        """Create bitmap from settings data (similar to test.py message format)"""
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

    def create_from_frontend_data(self, text_items: List[Dict], value_items: List[Dict], icon_items: List[Dict], barcode_items: List[Dict]):
        """Create bitmap from frontend data format"""
        self.bitmap_init()
        
        # Process text items
        for text_item in text_items:
            if text_item.get("content"):
                self.set_text(
                    text_item["content"],
                    text_item.get("x", 0),
                    text_item.get("y", 0),
                    text_item.get("fontSize", 12),
                    text_item.get("fontFamily", "Arial")
                )
        
        # Process value items (same as text items)
        for value_item in value_items:
            if value_item.get("content"):
                self.set_text(
                    value_item["content"],
                    value_item.get("x", 0),
                    value_item.get("y", 0),
                    value_item.get("fontSize", 12),
                    value_item.get("fontFamily", "Arial")
                )
        
        # Process icon items
        for icon_item in icon_items:
            if icon_item.get("iconFile"):
                # For base64 data, we need to handle it differently
                # For now, skip icon items as they need special handling
                pass
        
        # Process barcode items
        for barcode_item in barcode_items:
            if barcode_item.get("data"):
                self.set_barcode(
                    barcode_item["data"],
                    barcode_item.get("x", 0),
                    barcode_item.get("y", 0),
                    barcode_item.get("format", "code128"),
                    barcode_item.get("width", None),
                    barcode_item.get("height", None)
                )
        
        self.bitmap_finish()

