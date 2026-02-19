from flask import Flask, Response, render_template, request, jsonify, session, send_file
from flask_cors import CORS
from threading import Thread
import os
import json
import sys
import base64
from datetime import datetime

# Import with PyInstaller compatibility
try:
    from backend.tscPrinterModule import printer_manager
    from backend.bitmapGenerator import BitmapGenerator
except ImportError:
    try:
        # Fallback for PyInstaller
        from tscPrinterModule import printer_manager
        from bitmapGenerator import BitmapGenerator
    except ImportError:
        # Second fallback - try without backend prefix
        import sys
        import os
        backend_path = os.path.join(os.path.dirname(__file__))
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        from tscPrinterModule import printer_manager
        from bitmapGenerator import BitmapGenerator

class FlaskModule:
    def __init__(self, application) -> None:
        self.application = application
        # Mutlak path kullan
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        build_path = os.path.join(current_dir, "frontend", "build")
        
        self.app = Flask(__name__, 
                        static_url_path='',
                        static_folder=build_path,
                        template_folder=build_path)
        
        # CORS'u etkinleştir
        CORS(self.app)
        
        self.setup_routes()
        Thread(target=self.run, daemon=True).start()
              
    def setup_routes(self):
        @self.app.route("/")
        def main():
            return render_template("index.html")

        @self.app.route("/bitmap-settings")
        def bitmap_settings():
            return render_template("index.html")

        @self.app.route("/printer-settings")
        def printer_settings():
            return render_template("index.html")
        
        
        @self.app.route("/api/health")
        def health():
            return jsonify({"status": "healthy", "message": "API is running"})
        
        @self.app.route("/api/printers", methods=['GET'])
        def get_printers():
            try:
                printers = self.application.printers.get_all_printers()
                result = []
                
                for printer in printers:
                    # Check printer connection status using printer_manager
                    status_info = printer_manager.get_printer_status(printer["ip"])
                    printer_with_status = {
                        **printer,
                        "is_online": status_info["is_online"],
                        "status": status_info["status"]
                    }
                    result.append(printer_with_status)
                
                return jsonify(result)
            except Exception as e:
                print(f"Error in get_printers: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/api/printers", methods=['POST'])
        def add_printer():
            try:
                data = request.get_json()
                ip = data.get('ip')
                name = data.get('name')
                dpi = data.get('dpi')
                width = data.get('width')
                height = data.get('height')
                
                if not all([ip, name, dpi, width, height]):
                    return jsonify({"error": "Missing required fields"}), 400
                
                success = self.application.printers.insert_printer(
                    ip, name, dpi, width, height
                )
                
                if success:
                    return jsonify({"message": "Printer added successfully"}), 201
                else:
                    return jsonify({"error": "Failed to add printer"}), 500
                    
            except Exception as e:
                print(f"Error in add_printer: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/api/printer", methods=['POST'])
        def get_printer():
            try:
                data = request.get_json()
                ip = data.get('ip')
                name = data.get('name')  # Printer name de destekleniyor
                
                if not ip and not name:
                    return jsonify({"error": "IP or name is required"}), 400
                
                # Önce name'e göre ara, yoksa IP'ye göre ara
                if name:
                    printer_data = self.application.printers.get_printer_by_name(name)
                    if not printer_data:
                        return jsonify({"error": "Printer not found"}), 404
                    printer = printer_data[0]
                    ip = printer["ip"]  # IP'yi printer'dan al
                else:
                    printer_data = self.application.printers.get_printer_by_ip(ip)
                    if not printer_data:
                        return jsonify({"error": "Printer not found"}), 404
                    printer = printer_data[0]
                
                # Check printer connection status using printer_manager
                status_info = printer_manager.get_printer_status(ip)
                
                result = {
                    **printer,
                    "is_online": status_info["is_online"],
                    "status": status_info["status"]
                }
                
                return jsonify(result)
            except Exception as e:
                print(f"Error in get_printer: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/api/printer/update", methods=['POST'])
        def update_printer():
            try:
                data = request.get_json()
                ip = data.get('ip')
                name = data.get('name')
                dpi = data.get('dpi')
                width = data.get('width')
                height = data.get('height')
                
                if not all([ip, name, dpi, width, height]):
                    return jsonify({"error": "Missing required fields"}), 400
                
                # Önce mevcut printer'ı bul
                existing_printer = self.application.printers.get_printer_by_ip(ip)
                if not existing_printer:
                    return jsonify({"error": "Printer not found"}), 404
                
                printer_id = existing_printer[0]['id']
                success = self.application.printers.update_printer(
                    printer_id, ip, name, dpi, width, height
                )
                
                if success:
                    return jsonify({"message": "Printer updated successfully"})
                else:
                    return jsonify({"error": "Failed to update printer"}), 500
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/api/printer/delete", methods=['POST'])
        def delete_printer():
            try:
                data = request.get_json()
                ip = data.get('ip')
                
                if not ip:
                    return jsonify({"error": "IP is required"}), 400
                
                # Önce mevcut printer'ı bul
                existing_printer = self.application.printers.get_printer_by_ip(ip)
                if not existing_printer:
                    return jsonify({"error": "Printer not found"}), 404
                
                printer_id = existing_printer[0]['id']
                success = self.application.printers.delete_printer(printer_id)
                if success:
                    return jsonify({"message": "Printer deleted successfully"})
                else:
                    return jsonify({"error": "Failed to delete printer"}), 500
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/printers/count", methods=['GET'])
        def get_printer_count():
            try:
                count = self.application.printers.get_printer_count()
                return jsonify({"count": count})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/printer/print", methods=['POST'])
        def print_to_printer():
            try:
                data = request.get_json()
                ip = data.get('ip')
                print_type = data.get('type', 'bmp')  # 'bmp' or 'text'
                
                if not ip:
                    return jsonify({"error": "IP is required"}), 400
                
                # Get printer info from database
                printer_data = self.application.printers.get_printer_by_ip(ip)
                if not printer_data:
                    return jsonify({"error": "Printer not found"}), 404
                
                printer_info = printer_data[0]
                width_mm = printer_info["width"]
                height_mm = printer_info["height"]
                
                if print_type == 'bmp':
                    bmp_path = data.get('bmp_path', 'logo.bmp')
                    # Bitmap dosyasının varlığını kontrol et
                    if not os.path.exists(bmp_path):
                        return jsonify({"error": f"Bitmap file not found: {bmp_path}"}), 404
                    success = printer_manager.print_bmp(ip, bmp_path, width_mm, height_mm)
                elif print_type == 'text':
                    text = data.get('text', 'Test Print')
                    x = data.get('x', 10)
                    y = data.get('y', 10)
                    success = printer_manager.print_text(ip, text, x, y, width_mm, height_mm)
                else:
                    return jsonify({"error": "Invalid print type. Use 'bmp' or 'text'"}), 400
                
                if success:
                    return jsonify({"message": f"Successfully printed to {ip}"})
                else:
                    return jsonify({"error": f"Failed to print to {ip}"}), 500
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/api/printer/logo", methods=['POST'])
        def get_printer_logo():
            """Get the bitmap file for a specific printer"""
            try:
                data = request.get_json()
                printer_ip = data.get('ip')
                printer_name = data.get('printerName')  # Frontend'ten gelen printer name
                settings_name = data.get('name', 'default')
                
                if not printer_ip:
                    return jsonify({"error": "IP is required"}), 400
                
                # Eğer printerName gönderilmişse onu kullan, yoksa IP'ye göre bul
                if printer_name:
                    # Printer name'e göre kontrol et
                    existing_printer = self.application.printers.get_printer_by_name(printer_name)
                    if not existing_printer:
                        return jsonify({"error": "Printer not found"}), 404
                    # IP'yi de kontrol et (güvenlik için)
                    if existing_printer[0]["ip"] != printer_ip:
                        return jsonify({"error": "Printer IP mismatch"}), 400
                else:
                    # Geriye dönük uyumluluk: IP'ye göre bul
                    existing_printer = self.application.printers.get_printer_by_ip(printer_ip)
                    if not existing_printer:
                        return jsonify({"error": "Printer not found"}), 404
                    printer_name = existing_printer[0]["name"]
                
                # Get bitmap settings from database
                bitmap_settings = self.application.printers.get_bitmap_settings(printer_ip, printer_name, settings_name)
                if not bitmap_settings:
                    # If no specific settings found, try to find any settings for this printer
                    all_settings = self.application.printers.get_bitmap_settings(printer_ip, printer_name)
                    if all_settings:
                        # Use the first available settings
                        bitmap_settings = [all_settings[0]]
                        settings_name = all_settings[0]['name']
                    else:
                        return jsonify({"error": "No bitmap settings found for this printer"}), 404
                
                # Check if the corresponding bitmap file exists
                bitmap_filename = f"bitmap_{printer_ip}_{settings_name}.bmp"
                
                # Get the correct path for bitmap files when running as exe
                if getattr(sys, 'frozen', False):
                    # Running as compiled exe - bitmap files are in the same directory as exe
                    base_path = os.path.dirname(sys.executable)
                    bitmap_path = os.path.join(base_path, bitmap_filename)
                else:
                    # Running as script - bitmap files are in project root
                    bitmap_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), bitmap_filename)
                
                if os.path.exists(bitmap_path):
                    return send_file(bitmap_path, mimetype='image/bmp')
                else:
                    # If bitmap file doesn't exist, generate it from settings
                    settings_data = json.loads(bitmap_settings[0]['settings_data'])
                    printer_info = existing_printer[0]
                    
                    # Generate bitmap
                    from backend.bitmapGenerator import BitmapGenerator
                    generator = BitmapGenerator(
                        printer_info["width"], 
                        printer_info["height"], 
                        printer_info["dpi"],
                        bitmap_path
                    )
                    generator.create_from_frontend_data(
                        settings_data.get('textItems', []), 
                        settings_data.get('valueItems', []),
                        settings_data.get('iconItems', []), 
                        settings_data.get('barcodeItems', [])
                    )
                    
                    # Return the generated bitmap
                    if os.path.exists(bitmap_path):
                        return send_file(bitmap_path, mimetype='image/bmp')
                    else:
                        return jsonify({"error": "Failed to generate bitmap"}), 500
                        
            except Exception as e:
                print(f"Logo endpoint error: {e}")
                return jsonify({"error": str(e)}), 500

    def print_yan_etiket_normal(self, is_arcelik, payload, sap_data):
        try:
            if is_arcelik:
                sap_data["LOGO_NAME"] = "hera_logo"

            printer_name = "ARKA MASA"

            serial_number = payload.get("SERIAL_NUMBER") or ""
            if not serial_number:
                return jsonify({"error": "Serial number is required"}), 400
            
            test_device = payload.get("TEST_DEVICE") or ""
            if not test_device:
                return jsonify({"error": "Test device is required"}), 400

            if test_device == 2:
                printer_name = "ARKA MASA"
            elif test_device == 1:
                printer_name = "ÖN MASA"
            else:
                return jsonify({"error": "Invalid test device"}), 400

            data = {
                "PRODUCT_CODE": sap_data.get("PRODUCT_CODE") or "",
                "MODEL_NUMBER": sap_data.get("MODEL_NUMBER") or "",
                "SYSTEM": sap_data.get("SYSTEM") or "",
                "RATED_VOLTAGE": sap_data.get("RATED_VOLTAGE") or "",
                "RATED_POWER": sap_data.get("RATED_POWER") or "",
                "OPERATING_TEMP": sap_data.get("OPERATING_TEMP") or "",
                "MANUFACTURER": sap_data.get("MANUFACTURER") or "",
                "BT_MAC": sap_data.get("BT_MAC") or "",
                "LAN_MAC": sap_data.get("LAN_MAC") or "",
                "IMEI_NUMBER": sap_data.get("IMEI_NUMBER") or "",
                "SITE_ID": sap_data.get("SITE_ID") or "",
                "DATE_NUMBER": datetime.now().strftime("%d/%m/%Y"),
                "SERIAL_NUMBER": serial_number,
                "BODY_COLOR": sap_data.get("BODY_COLOR") or "",
                "EAN_NUMBER": sap_data.get("EAN_NUMBER") or "",
                "mid": sap_data.get("mid") or False,
                "mid_year": sap_data.get("mid_year") or "",
                "mid_lab": sap_data.get("mid_lab") or "",
                "ip": sap_data.get("IP") or "",
                "BT_NAME": sap_data.get("BT_NAME") or "",
                "PIN_CODE": sap_data.get("PIN_CODE") or "",
                "LOGO_NAME": sap_data.get("LOGO_NAME") or "",
                "OEM_COMPANY_NAME": sap_data.get("OEM_COMPANY_NAME") or "",
                "OemProductCode": sap_data.get("OemProductCode") or "",
                "OemProductCode2": sap_data.get("OemProductCode2") or "",
                "OemProductCodeDefinition": sap_data.get("OemProductCodeDefinition") or "",
            }

            ip = self.application.printers.get_printer_ip_by_name(printer_name)
            # Printer name'e göre bitmap ayarlarını al
            settings_data = self.application.printers.get_printer_data_by_name(printer_name, "default")
            if not settings_data:
                # Eğer default yoksa, IP'ye göre ilk bulunan ayarı al (geriye dönük uyumluluk)
                settings_data = self.application.printers.get_printer_data_by_ip(ip)
            if not settings_data:
                return jsonify({"error": "Bitmap settings not found"}), 404
            settings_data_json = json.loads(settings_data)
            text_items = settings_data_json.get('textItems', [])
            value_items = settings_data_json.get('valueItems', [])
            icon_items = settings_data_json.get('iconItems', [])
            barcode_items = settings_data_json.get('barcodeItems', [])
            
            settings_data = {
                "textItems": text_items,
                "valueItems": value_items,
                "iconItems": icon_items,
                "barcodeItems": barcode_items
            }

            for value_data in value_items:
                if value_data["valueId"] == "SERIAL_NUMBER":
                    value_data["content"] = data.get("SERIAL_NUMBER", "")
                elif value_data["valueId"] == "DATE_NUMBER":
                    value_data["content"] = data.get("DATE_NUMBER", "")
                elif value_data["valueId"] == "SITE_ID":
                    value_data["content"] = data.get("SITE_ID", "")
                elif value_data["valueId"] == "IMEI_NUMBER":
                    value_data["content"] = data.get("IMEI_NUMBER", "")
                elif value_data["valueId"] == "LAN_MAC":
                    value_data["content"] = (data.get("LAN_MAC", "") or "").upper()
                elif value_data["valueId"] == "BT_MAC":
                    value_data["content"] = (data.get("BT_MAC", "") or "").upper()
                elif value_data["valueId"] == "PRODUCT_CODE":
                    value_data["content"] = data.get("PRODUCT_CODE", "")
                elif value_data["valueId"] == "MODEL_NUMBER":
                    value_data["content"] = data.get("MODEL_NUMBER", "")
                elif value_data["valueId"] == "SYSTEM":
                    value_data["content"] = data.get("SYSTEM", "")
                elif value_data["valueId"] == "RATED_VOLTAGE":
                    value_data["content"] = data.get("RATED_VOLTAGE", "")
                elif value_data["valueId"] == "RATED_POWER":
                    value_data["content"] = data.get("RATED_POWER", "")
                elif value_data["valueId"] == "OPERATING_TEMP":
                    value_data["content"] = data.get("OPERATING_TEMP", "")
                elif value_data["valueId"] == "MANUFACTURER":
                    value_data["content"] = data.get("MANUFACTURER", "")
                elif value_data["valueId"] == "BT_NAME":
                    value_data["content"] = data.get("BT_NAME", "")
                elif value_data["valueId"] == "PIN_CODE":
                    value_data["content"] = data.get("PIN_CODE", "")
                elif value_data["valueId"] == "LOGO_NAME":
                    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    images_dir = os.path.join(project_root, "database", "images")
                    image_path = os.path.join(images_dir, f"{data.get('LOGO_NAME', '')}.png")
                    print(f"Image path: {image_path}")
                    if os.path.exists(image_path):
                        with open(image_path, "rb") as img_file:
                            encoded = base64.b64encode(img_file.read()).decode("ascii")
                        value_data["type"] = "image"
                        value_data["content"] = ""
                        value_data["imageFile"] = encoded
                    else:
                        print(f"Image not found: {image_path}")
                elif value_data["valueId"] == "mid_lab":
                    value_data["content"] = data.get("mid_lab", "")
                elif value_data["valueId"] == "IP":
                    # IP normalde image olacak: IP55 -> IP55.png, IP54 -> IP54.png
                    ip_value = data.get("ip", "")
                    if ip_value:
                        try:
                            # Proje kökü: backend klasörünün bir üstü
                            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                            images_dir = os.path.join(project_root, "database", "images")
                            image_path = os.path.join(images_dir, f"{ip_value}.png")

                            if os.path.exists(image_path):
                                with open(image_path, "rb") as img_file:
                                    encoded = base64.b64encode(img_file.read()).decode("ascii")

                                # Bu value item'i image tipine çevir
                                value_data["type"] = "image"
                                value_data["content"] = ""  # text kullanılmayacak
                                value_data["imageFile"] = encoded
                                # imageWidth / imageHeight ayarlıysa tasarımdaki değerler kullanılacak
                            else:
                                # Dosya yoksa fallback olarak text yaz
                                value_data["content"] = ip_value
                        except Exception as e:
                            print(f"IP image load error: {e}")
                            # Fallback: IP değerini text olarak göster
                            value_data["content"] = data.get("ip", "")
                elif value_data["valueId"] == "MID":
                    # MID varsa: MID M{mid_year}.png göster
                    try:
                        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                        images_dir = os.path.join(project_root, "database", "images")
                        
                        has_mid = data.get("mid", False)
                        mid_year = data.get("mid_year", "")
                        
                        if has_mid and mid_year:
                            image_filename = f"MID M{mid_year}.png"
                            image_path = os.path.join(images_dir, image_filename)
                            
                            if os.path.exists(image_path):
                                with open(image_path, "rb") as img_file:
                                    encoded = base64.b64encode(img_file.read()).decode("ascii")
                                
                                value_data["type"] = "image"
                                value_data["content"] = ""
                                value_data["imageFile"] = encoded
                            else:
                                # MID dosyası yoksa fallback olarak text yaz
                                value_data["type"] = "text"
                                value_data["imageFile"] = ""
                                value_data["content"] = f"MID M{mid_year}"
                        else:
                            # MID yoksa bu value item'ı boş bırak ve image'i temizle
                            value_data["type"] = "text"
                            value_data["imageFile"] = ""
                            value_data["content"] = ""
                    except Exception as e:
                        print(f"MID image load error: {e}")
                        value_data["type"] = "text"
                        value_data["imageFile"] = ""
                        value_data["content"] = ""
                elif value_data["valueId"] == "OEM_COMPANY_NAME":
                    value_data["content"] = data.get("OEM_COMPANY_NAME", "")
                elif value_data["valueId"] == "OemProductCode":
                    value_data["content"] = data.get("OemProductCode", "")
                elif value_data["valueId"] == "OemProductCodeDefinition":
                    value_data["content"] = data.get("OemProductCodeDefinition", "")

            # Barkod alanlarını seri numarası ile doldur
            for barcode_item in barcode_items:
                barcode_item["data"] = data.get("SERIAL_NUMBER", "")

            # Imei 18, 21
            # Lan mac 19, 22
            # bt mac 20, 23

            # BT_MAC, LAN_MAC, IMEI_NUMBER yoksa ilgili textItems'ları filtrele
            bt_mac_exists = bool(data.get("BT_MAC") and data.get("BT_MAC", "").strip())
            lan_mac_exists = bool(data.get("LAN_MAC") and data.get("LAN_MAC", "").strip())
            imei_exists = bool(data.get("IMEI_NUMBER") and data.get("IMEI_NUMBER", "").strip())
            
            # Filtrelenecek text item id'lerini belirle
            text_ids_to_filter = []
            
            # IMEI_NUMBER yoksa 18 ve 21'i filtrele
            if not imei_exists:
                text_ids_to_filter.extend([18, 21])
            
            # LAN_MAC yoksa 19 ve 22'yi filtrele
            if not lan_mac_exists:
                text_ids_to_filter.extend([19, 22])
            
            # BT_MAC yoksa 20 ve 23'ü filtrele
            if not bt_mac_exists:
                text_ids_to_filter.extend([20, 23])
            
            # Filtreleme işlemini yap
            if text_ids_to_filter:
                text_items = [item for item in text_items if item.get("id") not in text_ids_to_filter]

            printers = self.application.printers.search_printers_by_name(printer_name)
            width = printers[0]["width"]
            height = printers[0]["height"]
            dpi = printers[0]["dpi"]
            name = "test"

            generator = BitmapGenerator(
                width, 
                height, 
                dpi,
                f"bitmap_{ip}_{name}.bmp"
            )
            generator.create_from_frontend_data(text_items, value_items, icon_items, barcode_items)
            bitmap_path = os.path.join(os.getcwd(), f"bitmap_{ip}_{name}.bmp")
            if os.path.exists(bitmap_path):
                success = printer_manager.print_bmp(ip, bitmap_path, width, height)
                if success:
                    return jsonify({"message": "Bitmap printed successfully"})
                else:
                    return jsonify({"error": "Failed to print bitmap"}), 500
            else:
                return jsonify({"error": "Failed to generate bitmap"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def print_yan_etiket_arcelik(self, payload, sap_data):
        try:
            sap_data["LOGO_NAME"] = "arcelikbywat_logo"

            printer_name = "ARÇELİK ARKA MASA"

            serial_number = payload.get("SERIAL_NUMBER") or ""
            if not serial_number:
                return jsonify({"error": "Serial number is required"}), 400
            
            test_device = payload.get("TEST_DEVICE") or ""
            if not test_device:
                return jsonify({"error": "Test device is required"}), 400

            if test_device == 2:
                printer_name = "ARÇELİK ARKA MASA"
            elif test_device == 1:
                printer_name = "ARÇELİK ÖN MASA"
            else:
                return jsonify({"error": "Invalid test device"}), 400

            data = {
                "PRODUCT_CODE": sap_data.get("PRODUCT_CODE") or "",
                "MODEL_NUMBER": sap_data.get("MODEL_NUMBER") or "",
                "SYSTEM": sap_data.get("SYSTEM") or "",
                "RATED_VOLTAGE": sap_data.get("RATED_VOLTAGE") or "",
                "RATED_POWER": sap_data.get("RATED_POWER") or "",
                "OPERATING_TEMP": sap_data.get("OPERATING_TEMP") or "",
                "MANUFACTURER": sap_data.get("MANUFACTURER") or "",
                "BT_MAC": sap_data.get("BT_MAC") or "",
                "LAN_MAC": sap_data.get("LAN_MAC") or "",
                "IMEI_NUMBER": sap_data.get("IMEI_NUMBER") or "",
                "SITE_ID": sap_data.get("SITE_ID") or "",
                "DATE_NUMBER": datetime.now().strftime("%d/%m/%Y"),
                "SERIAL_NUMBER": serial_number,
                "BODY_COLOR": sap_data.get("BODY_COLOR") or "",
                "EAN_NUMBER": sap_data.get("EAN_NUMBER") or "",
                "mid": sap_data.get("mid") or False,
                "mid_year": sap_data.get("mid_year") or "",
                "mid_lab": sap_data.get("mid_lab") or "",
                "ip": sap_data.get("IP") or "",
                "BT_NAME": sap_data.get("BT_NAME") or "",
                "PIN_CODE": sap_data.get("PIN_CODE") or "",
                "LOGO_NAME": sap_data.get("LOGO_NAME") or "",
                "OEM_COMPANY_NAME": sap_data.get("OEM_COMPANY_NAME") or "",
                "OemProductCode": sap_data.get("OemProductCode") or "",
                "OemProductCode2": sap_data.get("OemProductCode2") or "",
                "OemProductCodeDefinition": sap_data.get("OemProductCodeDefinition") or "",
            }

            ip = self.application.printers.get_printer_ip_by_name(printer_name)
            # Printer name'e göre bitmap ayarlarını al
            settings_data = self.application.printers.get_printer_data_by_name(printer_name, "default")
            if not settings_data:
                # Eğer default yoksa, IP'ye göre ilk bulunan ayarı al (geriye dönük uyumluluk)
                settings_data = self.application.printers.get_printer_data_by_ip(ip)
            if not settings_data:
                return jsonify({"error": "Bitmap settings not found"}), 404
            settings_data_json = json.loads(settings_data)
            text_items = settings_data_json.get('textItems', [])
            value_items = settings_data_json.get('valueItems', [])
            icon_items = settings_data_json.get('iconItems', [])
            barcode_items = settings_data_json.get('barcodeItems', [])
            
            settings_data = {
                "textItems": text_items,
                "valueItems": value_items,
                "iconItems": icon_items,
                "barcodeItems": barcode_items
            }

            for value_data in value_items:
                if value_data["valueId"] == "SERIAL_NUMBER":
                    value_data["content"] = self.application.utils.create_arcelik_serial_number(data.get("OemProductCode2"), data.get("SERIAL_NUMBER"))
                elif value_data["valueId"] == "DATE_NUMBER":
                    value_data["content"] = data.get("DATE_NUMBER", "")
                elif value_data["valueId"] == "SITE_ID":
                    value_data["content"] = data.get("SITE_ID", "")
                elif value_data["valueId"] == "IMEI_NUMBER":
                    value_data["content"] = data.get("IMEI_NUMBER", "")
                elif value_data["valueId"] == "LAN_MAC":
                    value_data["content"] = (data.get("LAN_MAC", "") or "").upper()
                elif value_data["valueId"] == "BT_MAC":
                    value_data["content"] = (data.get("BT_MAC", "") or "").upper()
                elif value_data["valueId"] == "PRODUCT_CODE":
                    value_data["content"] = data.get("PRODUCT_CODE", "")
                elif value_data["valueId"] == "MODEL_NUMBER":
                    value_data["content"] = data.get("MODEL_NUMBER", "")
                elif value_data["valueId"] == "SYSTEM":
                    value_data["content"] = data.get("SYSTEM", "")
                elif value_data["valueId"] == "RATED_VOLTAGE":
                    value_data["content"] = data.get("RATED_VOLTAGE", "")
                elif value_data["valueId"] == "RATED_POWER":
                    value_data["content"] = data.get("RATED_POWER", "")
                elif value_data["valueId"] == "OPERATING_TEMP":
                    value_data["content"] = data.get("OPERATING_TEMP", "")
                elif value_data["valueId"] == "MANUFACTURER":
                    value_data["content"] = data.get("MANUFACTURER", "")
                elif value_data["valueId"] == "BT_NAME":
                    value_data["content"] = data.get("BT_NAME", "")
                elif value_data["valueId"] == "PIN_CODE":
                    value_data["content"] = data.get("PIN_CODE", "")
                elif value_data["valueId"] == "LOGO_NAME":
                    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    images_dir = os.path.join(project_root, "database", "images")
                    image_path = os.path.join(images_dir, f"{data.get('LOGO_NAME', '')}.png")
                    print(f"Image path: {image_path}")
                    if os.path.exists(image_path):
                        with open(image_path, "rb") as img_file:
                            encoded = base64.b64encode(img_file.read()).decode("ascii")
                        value_data["type"] = "image"
                        value_data["content"] = ""
                        value_data["imageFile"] = encoded
                    else:
                        print(f"Image not found: {image_path}")
                elif value_data["valueId"] == "mid_lab":
                    value_data["content"] = data.get("mid_lab", "")
                elif value_data["valueId"] == "IP":
                    # IP normalde image olacak: IP55 -> IP55.png, IP54 -> IP54.png
                    ip_value = data.get("ip", "")
                    if ip_value:
                        try:
                            # Proje kökü: backend klasörünün bir üstü
                            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                            images_dir = os.path.join(project_root, "database", "images")
                            image_path = os.path.join(images_dir, f"{ip_value}.png")

                            if os.path.exists(image_path):
                                with open(image_path, "rb") as img_file:
                                    encoded = base64.b64encode(img_file.read()).decode("ascii")

                                # Bu value item'i image tipine çevir
                                value_data["type"] = "image"
                                value_data["content"] = ""  # text kullanılmayacak
                                value_data["imageFile"] = encoded
                                # imageWidth / imageHeight ayarlıysa tasarımdaki değerler kullanılacak
                            else:
                                # Dosya yoksa fallback olarak text yaz
                                value_data["content"] = ip_value
                        except Exception as e:
                            print(f"IP image load error: {e}")
                            # Fallback: IP değerini text olarak göster
                            value_data["content"] = data.get("ip", "")
                elif value_data["valueId"] == "MID":
                    # MID varsa: MID M{mid_year}.png göster
                    try:
                        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                        images_dir = os.path.join(project_root, "database", "images")
                        
                        has_mid = data.get("mid", False)
                        mid_year = data.get("mid_year", "")
                        
                        if has_mid and mid_year:
                            image_filename = f"MID M{mid_year}.png"
                            image_path = os.path.join(images_dir, image_filename)
                            
                            if os.path.exists(image_path):
                                with open(image_path, "rb") as img_file:
                                    encoded = base64.b64encode(img_file.read()).decode("ascii")
                                
                                value_data["type"] = "image"
                                value_data["content"] = ""
                                value_data["imageFile"] = encoded
                            else:
                                # MID dosyası yoksa fallback olarak text yaz
                                value_data["type"] = "text"
                                value_data["imageFile"] = ""
                                value_data["content"] = f"MID M{mid_year}"
                        else:
                            # MID yoksa bu value item'ı boş bırak ve image'i temizle
                            value_data["type"] = "text"
                            value_data["imageFile"] = ""
                            value_data["content"] = ""
                    except Exception as e:
                        print(f"MID image load error: {e}")
                        value_data["type"] = "text"
                        value_data["imageFile"] = ""
                        value_data["content"] = ""
                elif value_data["valueId"] == "OEM_COMPANY_NAME":
                    value_data["content"] = data.get("OEM_COMPANY_NAME", "")
                elif value_data["valueId"] == "OemProductCode":
                    value_data["content"] = data.get("OemProductCode", "")
                elif value_data["valueId"] == "OemProductCodeDefinition":
                    value_data["content"] = data.get("OemProductCodeDefinition", "")

            # Barkod alanlarını seri numarası ile doldur
            for barcode_item in barcode_items:
                barcode_item["data"] = data.get("SERIAL_NUMBER", "")

            # Imei 18, 21
            # Lan mac 19, 22
            # bt mac 20, 23

            # BT_MAC, LAN_MAC, IMEI_NUMBER yoksa ilgili textItems'ları filtrele
            bt_mac_exists = bool(data.get("BT_MAC") and data.get("BT_MAC", "").strip())
            lan_mac_exists = bool(data.get("LAN_MAC") and data.get("LAN_MAC", "").strip())
            imei_exists = bool(data.get("IMEI_NUMBER") and data.get("IMEI_NUMBER", "").strip())
            
            # Filtrelenecek text item id'lerini belirle
            text_ids_to_filter = []
            
            # IMEI_NUMBER yoksa 18 ve 21'i filtrele
            if not imei_exists:
                text_ids_to_filter.extend([18, 21])
            
            # LAN_MAC yoksa 19 ve 22'yi filtrele
            if not lan_mac_exists:
                text_ids_to_filter.extend([19, 22])
            
            # BT_MAC yoksa 20 ve 23'ü filtrele
            if not bt_mac_exists:
                text_ids_to_filter.extend([20, 23])
            
            # Filtreleme işlemini yap
            if text_ids_to_filter:
                text_items = [item for item in text_items if item.get("id") not in text_ids_to_filter]

            printers = self.application.printers.search_printers_by_name(printer_name)
            width = printers[0]["width"]
            height = printers[0]["height"]
            dpi = printers[0]["dpi"]
            name = "test"

            generator = BitmapGenerator(
                width, 
                height, 
                dpi,
                f"bitmap_{ip}_{name}.bmp"
            )
            generator.create_from_frontend_data(text_items, value_items, icon_items, barcode_items)
            bitmap_path = os.path.join(os.getcwd(), f"bitmap_{ip}_{name}.bmp")
            if os.path.exists(bitmap_path):
                success = printer_manager.print_bmp(ip, bitmap_path, width, height)
                if success:
                    return jsonify({"message": "Bitmap printed successfully"})
                else:
                    return jsonify({"error": "Failed to print bitmap"}), 500
            else:
                return jsonify({"error": "Failed to generate bitmap"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500


        @self.app.route("/api/testApplication/print", methods=['POST'])
        def test_application_print():
            try:
                payload = request.get_json(silent=True) or {}

                serial_number = payload.get("SERIAL_NUMBER") or ""
                if not serial_number:
                    return jsonify({"error": "Serial number is required"}), 400

                sap_data = self.application.utils.get_sap_device_knowledge(serial_number)
                if not sap_data:
                    return jsonify({"error": "SAP data not found"}), 404

                is_arcelik = sap_data.get("LOGO_NAME") == "arcelikbywat_logo"

                # Normal etiketi yazdır
                result_normal = self.print_yan_etiket_normal(is_arcelik, payload, sap_data)
                # Helper fonksiyon tuple döndürüyorsa (response, status_code) kontrol et
                if isinstance(result_normal, tuple):
                    response, status_code = result_normal
                    if status_code != 200:
                        # Hata durumu - hata mesajını döndür
                        return result_normal
                
                # Eğer arçelik ise arçelik etiketini de yazdır
                if is_arcelik:
                    result_arcelik = self.print_yan_etiket_arcelik(payload, sap_data)
                    if isinstance(result_arcelik, tuple):
                        response, status_code = result_arcelik
                        if status_code != 200:
                            # Hata durumu
                            return result_arcelik
                    return jsonify({"message": "Both labels printed successfully (normal + arcelik)"})
                else:
                    return jsonify({"message": "Label printed successfully"})
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500



        @self.app.route("/api/barcodeScanner/print", methods=['POST'])
        def barcode_scanner_print():
            try:
                data = request.get_json()
                serial_number = data.get('SERIAL_NUMBER', "")
                print(f"/api/barcodeScanner/print Serial number: {serial_number}")
                if not serial_number:
                    return jsonify({"error": "Serial number not found"}), 404
                    return False

                sap_data = self.application.utils.get_sap_device_knowledge(serial_number)
                if not sap_data:
                    return jsonify({"error": "SAP data not found"}), 404
                print(f"SAP data: {sap_data}")
                self.application.utils.print_paket(serial_number, sap_data)
                pin_code = sap_data.get("PIN_CODE", "")
                if pin_code:
                    self.application.utils.print_qr(serial_number, sap_data)

                return jsonify({"message": "Barcode printed successfully"})
            except Exception as e:
                print(f"barcode_scanner_print error: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/bitmap-settings", methods=['POST'])
        def save_bitmap_settings():
            try:
                data = request.get_json()
                ip = data.get('ip')
                printer_name = data.get('printerName')  # Frontend'ten gelen printer name
                name = data.get('name', 'default')  # Default name if not provided
                
                if not ip:
                    return jsonify({"error": "IP is required"}), 400
                
                # Eğer printerName gönderilmişse onu kullan, yoksa IP'ye göre bul
                if printer_name:
                    # Printer name'e göre kontrol et
                    existing_printer = self.application.printers.get_printer_by_name(printer_name)
                    if not existing_printer:
                        return jsonify({"error": "Printer not found"}), 404
                    # IP'yi de kontrol et (güvenlik için)
                    if existing_printer[0]["ip"] != ip:
                        return jsonify({"error": "Printer IP mismatch"}), 400
                else:
                    # Geriye dönük uyumluluk: IP'ye göre bul
                    existing_printer = self.application.printers.get_printer_by_ip(ip)
                    if not existing_printer:
                        return jsonify({"error": "Printer not found"}), 404
                    printer_name = existing_printer[0]["name"]
                
                # Get bitmap settings data
                text_items = data.get('textItems', [])
                value_items = data.get('valueItems', [])
                icon_items = data.get('iconItems', [])
                barcode_items = data.get('barcodeItems', [])
                
                # Debug logging
                print(f"Saving bitmap settings for {ip} (printer: {printer_name}) with settings name: {name}")
                print(f"Text items count: {len(text_items)}")
                print(f"Value items count: {len(value_items)}")
                print(f"Icon items count: {len(icon_items)}")
                print(f"Barcode items count: {len(barcode_items)}")
                
                # Log icon items details
                for i, icon_item in enumerate(icon_items):
                    icon_file_size = len(icon_item.get('iconFile', '')) if icon_item.get('iconFile') else 0
                    print(f"Icon item {i}: x={icon_item.get('x', 0)}, y={icon_item.get('y', 0)}, "
                          f"width={icon_item.get('width', 0)}, height={icon_item.get('height', 0)}, "
                          f"iconFile size={icon_file_size} chars")
                
                # Log barcode items details
                for i, barcode_item in enumerate(barcode_items):
                    print(f"Barcode item {i}: x={barcode_item.get('x', 0)}, y={barcode_item.get('y', 0)}, "
                          f"data='{barcode_item.get('data', '')}', format={barcode_item.get('format', '')}")
                
                # Create settings data structure
                settings_data = {
                    "textItems": text_items,
                    "valueItems": value_items,
                    "iconItems": icon_items,
                    "barcodeItems": barcode_items
                }
                success = self.application.printers.save_bitmap_settings(
                    ip, printer_name, name, json.dumps(settings_data)
                )
                print(f"Save result: {success}")
                
                if success:
                    # Generate bitmap file
                    try:
                        printer_info = existing_printer[0]
                        generator = BitmapGenerator(
                            printer_info["width"], 
                            printer_info["height"], 
                            printer_info["dpi"],
                            f"bitmap_{ip}_{name}.bmp"
                        )
                        generator.create_from_frontend_data(text_items, value_items, icon_items, barcode_items)
                        
                        # Return the generated bitmap file
                        bitmap_path = os.path.join(os.getcwd(), f"bitmap_{ip}_{name}.bmp")
                        if os.path.exists(bitmap_path):
                            return send_file(bitmap_path, mimetype='image/bmp')
                        else:
                            return jsonify({"message": "Settings saved successfully"})
                    except Exception as e:
                        print(f"Bitmap generation error: {e}")
                        return jsonify({"message": "Settings saved, but bitmap generation failed"})
                else:
                    return jsonify({"error": "Failed to save settings"}), 500
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/bitmap-settings/get", methods=['POST'])
        def get_bitmap_settings():
            try:
                data = request.get_json()
                ip = data.get('ip')
                printer_name = data.get('printerName')  # Frontend'ten gelen printer name
                name = data.get('name', None)
                
                if not ip:
                    return jsonify({"error": "IP is required"}), 400
                
                # Eğer printerName gönderilmişse onu kullan, yoksa IP'ye göre bul
                if printer_name:
                    # Printer name'e göre kontrol et
                    existing_printer = self.application.printers.get_printer_by_name(printer_name)
                    if not existing_printer:
                        return jsonify({"error": "Printer not found"}), 404
                    # IP'yi de kontrol et (güvenlik için)
                    if existing_printer[0]["ip"] != ip:
                        return jsonify({"error": "Printer IP mismatch"}), 400
                else:
                    # Geriye dönük uyumluluk: IP'ye göre bul
                    existing_printer = self.application.printers.get_printer_by_ip(ip)
                    if not existing_printer:
                        return jsonify({"error": "Printer not found"}), 404
                    printer_name = existing_printer[0]["name"]
                
                print(f"Getting bitmap settings for {ip} (printer: {printer_name}) with settings name: {name}")
                
                if name:
                    settings = self.application.printers.get_bitmap_settings(ip, printer_name, name)
                else:
                    settings = self.application.printers.get_bitmap_settings(ip, printer_name)
                
                print(f"Found settings: {settings}")
                
                if settings:
                    if name and len(settings) > 0:
                        # Return specific settings
                        settings_data = json.loads(settings[0]["settings_data"])
                        return jsonify({
                            "found": True,
                            "settings": settings_data,
                            "name": settings[0]["name"],
                            "created_at": settings[0]["created_at"],
                            "updated_at": settings[0]["updated_at"]
                        })
                    else:
                        # Return all settings for this printer
                        result = []
                        for setting in settings:
                            result.append({
                                "id": setting["id"],
                                "name": setting["name"],
                                "settings": json.loads(setting["settings_data"]),
                                "created_at": setting["created_at"],
                                "updated_at": setting["updated_at"]
                            })
                        return jsonify({
                            "found": True,
                            "settings_list": result
                        })
                else:
                    return jsonify({"found": False, "message": "No settings found"})
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/bitmap-settings/delete", methods=['POST'])
        def delete_bitmap_settings():
            try:
                data = request.get_json()
                ip = data.get('ip')
                name = data.get('name')
                
                if not ip or not name:
                    return jsonify({"error": "IP and name are required"}), 400
                
                # Get printer name from IP
                existing_printer = self.application.printers.get_printer_by_ip(ip)
                if not existing_printer:
                    return jsonify({"error": "Printer not found"}), 404
                
                printer_name = existing_printer[0]["name"]
                
                success = self.application.printers.delete_bitmap_settings(ip, printer_name, name)
                
                if success:
                    return jsonify({"message": "Settings deleted successfully"})
                else:
                    return jsonify({"error": "Failed to delete settings"}), 500
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        # Catch-all route for React Router (SPA support) - MUST BE LAST
        @self.app.route('/<path:path>')
        def catch_all(path):
            # API routes should not be caught
            if path.startswith('api/'):
                return jsonify({"error": "API endpoint not found"}), 404
            # Serve React app for all other routes
            return render_template("index.html")
        
    def run(self):
        try:
            print("Flask server starting on http://127.0.0.1:8088")
            print("Frontend: http://127.0.0.1:8088")
            print("API endpoints:")
            print("  GET  /api/printers - List all printers")
            print("  POST /api/printers - Add new printer")
            print("  GET  /api/printers/<ip> - Get printer by IP")
            print("  PUT  /api/printers/<ip> - Update printer by IP")
            print("  DELETE /api/printers/<ip> - Delete printer by IP")
            print("  GET  /api/health - Health check")
            print("  POST /api/bitmap-settings - Save bitmap settings")
            self.app.run(use_reloader=False, host="0.0.0.0", port=8088, threaded=False)
        except Exception as e:
            print("FlaskServer.py run Exception:", e)
