import os
import json
from backend.bitmapGenerator import BitmapGenerator
from backend.tscPrinterModule import printer_manager


class Utils:
    def __init__(self, application):
        self.application = application

    def save_device_data(self, serial_number, data):
        try:
            devices_data_dir = os.path.join(os.getcwd(), "devices_data")
            if not os.path.exists(devices_data_dir):
                os.makedirs(devices_data_dir)
                print(f"devices_data klasörü oluşturuldu: {devices_data_dir}")

            # JSON'ı serino.json olarak kaydet
            filename = f"{serial_number}.json"
            filepath = os.path.join(devices_data_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"save_device_data error: {e}")

    def get_device_data(self, serial_number):
        try:
            print(f"serial_number: {os.getcwd()}")
            devices_data_dir = os.path.join(os.getcwd(), "devices_data")
            if not os.path.exists(devices_data_dir):
                os.makedirs(devices_data_dir)
                print(f"devices_data klasörü oluşturuldu: {devices_data_dir}")

            filename = f"{serial_number}.json"
            filepath = os.path.join(devices_data_dir, filename)

            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"get_device_data error: {e}")
            return None

    def print_paket(self, data):
        try:
            serial_number = data.get('SERIAL_NUMBER')
            if not serial_number:
                return False

            device_data = self.application.utils.get_device_data(serial_number)
            if not device_data:
                return False

            printer_name = "PAKET"
            ip = self.application.printers.get_printer_ip_by_name(printer_name)
            settings_data = self.application.printers.get_printer_data_by_ip(ip)
            print(f"Settings data: {settings_data}")
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
                if value_data["valueId"] == "PRODUCT_CODE":
                    value_data["content"] = device_data["PRODUCT_CODE"]
                elif value_data["valueId"] == "MODEL_NUMBER":
                    value_data["content"] = device_data["MODEL_NUMBER"]
                elif value_data["valueId"] == "SYSTEM_ID":
                    value_data["content"] = device_data["SYSTEM"]
                elif value_data["valueId"] == "RATED_VOLTAGE":
                    value_data["content"] = device_data["RATED_VOLTAGE"]
                elif value_data["valueId"] == "BODY_COLOR":
                    value_data["content"] = device_data["BODY_COLOR"]
                elif value_data["valueId"] == "SERIAL_NUMBER":
                    value_data["content"] = device_data["SERIAL_NUMBER"]
                elif value_data["valueId"] == "EAN_NUMBER":
                    value_data["content"] = device_data["EAN_NUMBER"]
                elif value_data["valueId"] == "MANUFACTURER":
                    value_data["content"] = device_data["MANUFACTURER"]
                elif value_data["valueId"] == "SITE_ID":
                    value_data["content"] = device_data["SITE_ID"]

            for barcode_item in barcode_items:
                if barcode_item["sira"] == 1:
                    barcode_item["data"] = device_data["SERIAL_NUMBER"]
                elif barcode_item["sira"] == 2:
                    barcode_item["data"] = device_data["EAN_NUMBER"]

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
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            print(f"print_paket error: {e}")

    def print_qr(self, data):
        try:
            serial_number = data.get('SERIAL_NUMBER')
            if not serial_number:
                return False

            device_data = self.application.utils.get_device_data(serial_number)
            if not device_data:
                return False

            printer_name = "QR KOD"
            ip = self.application.printers.get_printer_ip_by_name(printer_name)
            settings_data = self.application.printers.get_printer_data_by_ip(ip)
            print(f"Settings data: {settings_data}")
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
                value_id = value_data.get("valueId")
                if value_id == "PRODUCT_CODE":
                    value_data["content"] = device_data.get("PRODUCT_CODE", "")
                elif value_id == "SERIAL_NUMBER":
                    value_data["content"] = device_data.get("SERIAL_NUMBER", serial_number)
                elif value_id == "BT_NAME":
                    value_data["content"] = device_data.get("BT_NAME", "")
                elif value_id == "PIN_CODE":
                    value_data["content"] = device_data.get("PIN_CODE", "")

            pin_code = device_data.get("PIN_CODE", "")
            for barcode_item in barcode_items:
                barcode_item["data"] = pin_code

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
                    return True
                else:
                    return False
            else:
                return False
                


        except Exception as e:
            print(f"print_qr error: {e}")
