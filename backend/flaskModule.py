from flask import Flask, Response, render_template, request, jsonify, session, send_file
from flask_cors import CORS
from threading import Thread
import os
import json
import sys

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
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/api/printer", methods=['POST'])
        def get_printer():
            try:
                data = request.get_json()
                ip = data.get('ip')
                
                if not ip:
                    return jsonify({"error": "IP is required"}), 400
                
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
                settings_name = data.get('name', 'default')
                
                if not printer_ip:
                    return jsonify({"error": "IP is required"}), 400
                
                # Check if printer exists
                existing_printer = self.application.printers.get_printer_by_ip(printer_ip)
                if not existing_printer:
                    return jsonify({"error": "Printer not found"}), 404
                
                # Get bitmap settings from database
                bitmap_settings = self.application.printers.get_bitmap_settings(printer_ip, settings_name)
                if not bitmap_settings:
                    # If no specific settings found, try to find any settings for this printer
                    all_settings = self.application.printers.get_bitmap_settings(printer_ip)
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

        @self.app.route("/api/bitmap-settings", methods=['POST'])
        def save_bitmap_settings():
            try:
                data = request.get_json()
                ip = data.get('ip')
                name = data.get('name', 'default')  # Default name if not provided
                
                if not ip:
                    return jsonify({"error": "IP is required"}), 400
                
                # Check if printer exists
                existing_printer = self.application.printers.get_printer_by_ip(ip)
                if not existing_printer:
                    return jsonify({"error": "Printer not found"}), 404
                
                # Get bitmap settings data
                text_items = data.get('textItems', [])
                value_items = data.get('valueItems', [])
                icon_items = data.get('iconItems', [])
                barcode_items = data.get('barcodeItems', [])
                
                # Debug logging
                print(f"Saving bitmap settings for {ip} with name: {name}")
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
                    ip, name, json.dumps(settings_data)
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
                name = data.get('name', None)
                
                if not ip:
                    return jsonify({"error": "IP is required"}), 400
                
                print(f"Getting bitmap settings for {ip} with name: {name}")
                
                if name:
                    settings = self.application.printers.get_bitmap_settings(ip, name)
                else:
                    settings = self.application.printers.get_bitmap_settings(ip)
                
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
                
                success = self.application.printers.delete_bitmap_settings(ip, name)
                
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
