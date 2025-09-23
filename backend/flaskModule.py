from flask import Flask, Response, render_template, request, jsonify, session, send_file
from flask_cors import CORS
from threading import Thread
import os

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
        
        @self.app.route("/printer-settings")
        def printer_settings():
            return render_template("index.html")
        
        @self.app.route("/api/health")
        def health():
            return jsonify({"status": "healthy", "message": "API is running"})
        
        @self.app.route("/api/printers", methods=['GET'])
        def get_printers():
            try:
                printers = self.application.printers.get_all_printers_with_status()
                return jsonify(printers)
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
        
        @self.app.route("/api/printers/<string:ip>", methods=['GET'])
        def get_printer(ip):
            try:
                printer = self.application.printers.get_printer_status(ip)
                if "error" in printer:
                    return jsonify(printer), 404
                else:
                    return jsonify(printer)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/api/printers/<string:ip>", methods=['PUT'])
        def update_printer(ip):
            try:
                data = request.get_json()
                new_ip = data.get('ip')
                name = data.get('name')
                dpi = data.get('dpi')
                width = data.get('width')
                height = data.get('height')
                
                if not all([new_ip, name, dpi, width, height]):
                    return jsonify({"error": "Missing required fields"}), 400
                
                # Önce mevcut printer'ı bul
                existing_printer = self.application.printers.get_printer_by_ip(ip)
                if not existing_printer:
                    return jsonify({"error": "Printer not found"}), 404
                
                printer_id = existing_printer[0]['id']
                success = self.application.printers.update_printer(
                    printer_id, new_ip, name, dpi, width, height
                )
                
                if success:
                    return jsonify({"message": "Printer updated successfully"})
                else:
                    return jsonify({"error": "Failed to update printer"}), 500
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/api/printers/<string:ip>", methods=['DELETE'])
        def delete_printer(ip):
            try:
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
        
        @self.app.route("/api/bitmap-settings", methods=['POST'])
        def save_bitmap_settings():
            try:
                data = request.get_json()
                ip = data.get('ip')
                
                if not ip:
                    return jsonify({"error": "IP is required"}), 400
                
                # Önce mevcut printer'ı bul
                existing_printer = self.application.printers.get_printer_by_ip(ip)
                if not existing_printer:
                    return jsonify({"error": "Printer not found"}), 404
                
                # Bitmap ayarlarını kaydet (şimdilik sadece log)
                print(f"Bitmap settings for printer {ip}:")
                print(f"Text items: {data.get('textItems', [])}")
                print(f"Icon items: {data.get('iconItems', [])}")
                print(f"Barcode items: {data.get('barcodeItems', [])}")
                
                # Logo.bmp dosyasını döndür
                current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                logo_path = os.path.join(current_dir, "logo.bmp")
                if os.path.exists(logo_path):
                    return send_file(logo_path, mimetype='image/bmp')
                else:
                    return jsonify({"error": "Logo file not found"}), 404
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
    def run(self):
        try:
            print("Flask server starting on http://127.0.0.1:8080")
            print("Frontend: http://127.0.0.1:8080")
            print("API endpoints:")
            print("  GET  /api/printers - List all printers")
            print("  POST /api/printers - Add new printer")
            print("  GET  /api/printers/<ip> - Get printer by IP")
            print("  PUT  /api/printers/<ip> - Update printer by IP")
            print("  DELETE /api/printers/<ip> - Delete printer by IP")
            print("  GET  /api/health - Health check")
            print("  POST /api/bitmap-settings - Save bitmap settings")
            self.app.run(use_reloader=False, host="127.0.0.1", port=8080, threaded=False)
        except Exception as e:
            print("FlaskServer.py run Exception:", e)
