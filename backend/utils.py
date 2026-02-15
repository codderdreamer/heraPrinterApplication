import os
import json
import base64
import requests
import urllib3
import time
from datetime import datetime
from backend.bitmapGenerator import BitmapGenerator
from backend.tscPrinterModule import printer_manager

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Utils:
    def __init__(self, application):
        self.application = application
        self.sap_base_url = "https://10.254.240.20:50000/b1s/v1"
        self.company_db = "HERA"  # yusufcana sorulacak
        self.sap_username = "manager"  # yusufcana sorulacak
        self.sap_password = "1302"  # yusufcana sorulacak

    def sap_login(self):
        try:
            login_payload = {
                    "CompanyDB": self.company_db,
                    "Password": self.sap_password,
                    "UserName": self.sap_username
                }
            
            headers = {"Content-Type": "application/json"}
            
            login_response = requests.post(
                f"{self.sap_base_url}/Login",
                headers=headers,
                json=login_payload,
                verify=False
            )

            if login_response.status_code == 200:
                print(f"Login successful: {login_response.json()}")
                return login_response.json().get("SessionId")
            else:
                print(f"Login failed: {login_response.status_code} - {login_response.text}")
                return None

        except Exception as e:
            print(f"sap_login error: {e}")
            return None

    def get_sap_device_knowledge(self, serial_number):
        """
        Serial number ile SAP'den tüm cihaz bilgilerini okur.
        
        Args:
            serial_number (str): Cihaz seri numarası
            
        Returns:
            dict: Cihaz bilgileri veya None (hata durumunda)
        """
        try:
            session_id = self.sap_login()
            if not session_id:
                print("SAP login failed")
                return None

            # 2. SerialNumberDetails'i al
            headers = {
                "Content-Type": "application/json",
                "Cookie": f"B1SESSION={session_id}"
            }
            
            params = {
                "$select": "DocEntry,ItemCode,ItemDescription,MfrSerialNo,SerialNumber,U_4GImei,U_BluetoothMAC,U_EthernetMAC,U_CPID,U_MRFID,U_KRFID,U_KRFID1,U_AESKey,U_AESIV,U_BLE_A_P",
                "$filter": f"SerialNumber eq '{serial_number}'"
            }

            print(f"SerialNumberDetails params: {params}")
            
            serial_response = requests.get(
                f"{self.sap_base_url}/SerialNumberDetails",
                headers=headers,
                params=params,
                verify=False
            )

            print(f"SerialNumberDetails response: {serial_response.text}")
            
            if serial_response.status_code != 200:
                print(f"SerialNumberDetails request failed: {serial_response.status_code} - {serial_response.text}")
                return None
            
            serial_data = serial_response.json()
            if "value" not in serial_data or len(serial_data["value"]) == 0:
                print(f"No data found for serial number: {serial_number}")
                return None
            
            serial_info = serial_data["value"][0]
            item_code = serial_info.get("ItemCode")
            doc_entry = serial_info.get("DocEntry")
            
            if not item_code:
                print("ItemCode bulunamadı")
                return None
            
            print(f"Found ItemCode: {item_code}, DocEntry: {doc_entry}")
            
            # 3. Items bilgilerini al
            params = {
                "$select": "ItemCode,BarCode,ItemName,ForeignName,U_Model,U_RaletedVoltage,U_LogoName,U_OemCompanyName,U_RaletedPower,U_BodyColor,U_operating_temp,U_manufacturer,U_baglanti_adresi,U_ip_info,U_System,U_OemProductCode,U_OemProductCode2,U_OemProductCodeDefinition",
                "$filter": f"ItemCode eq '{item_code}'"
            }
            
            items_response = requests.get(
                f"{self.sap_base_url}/Items",
                headers=headers,
                params=params,
                verify=False
            )
            
            if items_response.status_code != 200:
                print(f"Items request failed: {items_response.status_code} - {items_response.text}")
                # SerialNumberDetails bilgilerini döndür
                return serial_info
            
            items_data = items_response.json()
            if "value" not in items_data or len(items_data["value"]) == 0:
                print(f"No item data found for ItemCode: {item_code}")
                return serial_info
            
            item_info = items_data["value"][0]
            
            # 4. Tüm bilgileri birleştir
            device_knowledge = {
                # SerialNumberDetails bilgileri
                "DocEntry": doc_entry,
                "PRODUCT_CODE": item_code,
                "ItemDescription": serial_info.get("ItemDescription"),
                "MfrSerialNo": serial_info.get("MfrSerialNo"),
                "SerialNumber": serial_info.get("SerialNumber"),
                "SERIAL_NUMBER": serial_number,
                "IMEI_NUMBER": serial_info.get("U_4GImei"),
                "BT_MAC": serial_info.get("U_BluetoothMAC"),
                "LAN_MAC": serial_info.get("U_EthernetMAC"),
                "BT_NAME": serial_info.get("U_CPID"),
                "U_MRFID": serial_info.get("U_MRFID"),
                "U_KRFID": serial_info.get("U_KRFID"),
                "U_KRFID1": serial_info.get("U_KRFID1"),
                "U_AESKey": serial_info.get("U_AESKey"),
                "U_AESIV": serial_info.get("U_AESIV"),
                "PIN_CODE": serial_info.get("U_BLE_A_P"),
                

                # Items bilgileri
                "EAN_NUMBER": item_info.get("BarCode"),
                "ItemName": item_info.get("ItemName"),
                "ForeignName": item_info.get("ForeignName"),
                "MODEL_NUMBER": item_info.get("U_Model"),
                "RATED_VOLTAGE": item_info.get("U_RaletedVoltage"),
                "LOGO_NAME": item_info.get("U_LogoName"),
                "OEM_COMPANY_NAME": item_info.get("U_OemCompanyName"),
                "RATED_POWER": item_info.get("U_RaletedPower"),
                "BODY_COLOR": item_info.get("U_BodyColor"),
                "OPERATING_TEMP": item_info.get("U_operating_temp"),
                "MANUFACTURER": item_info.get("U_manufacturer"),
                "SITE_ID": item_info.get("U_baglanti_adresi"),
                "IP": item_info.get("U_ip_info"),
                "SYSTEM": item_info.get("U_System"),
                "OemProductCode": item_info.get("U_OemProductCode"),
                "OemProductCodeDefinition": item_info.get("U_OemProductCodeDefinition"),
                "OemProductCode2": item_info.get("U_OemProductCode2"),
            }
            
            print(f"Device knowledge retrieved successfully for serial: {serial_number}")
            return device_knowledge
            
        except Exception as e:
            print(f"get_sap_device_knowledge error: {e}")
            return None

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

    def print_paket(self, serial_number, sap_data):
        try:
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
                    value_data["content"] = sap_data.get("PRODUCT_CODE", "")
                elif value_data["valueId"] == "MODEL_NUMBER":
                    value_data["content"] = sap_data.get("MODEL_NUMBER", "")
                elif value_data["valueId"] == "SYSTEM_ID":
                    value_data["content"] = sap_data.get("SYSTEM", "")
                elif value_data["valueId"] == "RATED_VOLTAGE":
                    value_data["content"] = sap_data.get("RATED_VOLTAGE", "")
                elif value_data["valueId"] == "BODY_COLOR":
                    value_data["content"] = sap_data.get("BODY_COLOR", "")
                elif value_data["valueId"] == "SERIAL_NUMBER":
                    value_data["content"] = sap_data.get("SERIAL_NUMBER", "")
                elif value_data["valueId"] == "EAN_NUMBER":
                    value_data["content"] = sap_data.get("EAN_NUMBER", "")
                elif value_data["valueId"] == "MANUFACTURER":
                    value_data["content"] = sap_data.get("MANUFACTURER", "")
                elif value_data["valueId"] == "SITE_ID":
                    value_data["content"] = sap_data.get("SITE_ID", "")
                elif value_data["valueId"] == "LOGO_NAME":
                    logo_name = sap_data.get("LOGO_NAME", "")
                    if logo_name:
                        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                        images_dir = os.path.join(project_root, "database", "images")
                        image_path = os.path.join(images_dir, f"{logo_name}.png")
                        if os.path.exists(image_path):
                            with open(image_path, "rb") as img_file:
                                encoded = base64.b64encode(img_file.read()).decode("ascii")
                            value_data["type"] = "image"
                            value_data["content"] = ""
                            value_data["imageFile"] = encoded
                elif value_data["valueId"] == "OEM_COMPANY_NAME":
                    value_data["content"] = sap_data.get("OEM_COMPANY_NAME", "")
                elif value_data["valueId"] == "OemProductCode":
                    value_data["content"] = sap_data.get("OemProductCode", "")
                elif value_data["valueId"] == "OemProductCodeDefinition":
                    value_data["content"] = sap_data.get("OemProductCodeDefinition", "")
                

            for barcode_item in barcode_items:
                if barcode_item["sira"] == 1:
                    barcode_item["data"] = sap_data.get("SERIAL_NUMBER", "")
                elif barcode_item["sira"] == 2:
                    barcode_item["data"] = sap_data.get("EAN_NUMBER", "")
                elif barcode_item["sira"] == 3:
                    oem_product_code = sap_data.get("OemProductCode", "")
                    serial_number = sap_data.get("SERIAL_NUMBER", "")
                    if oem_product_code and oem_product_code.strip():
                        barcode_item["data"] = f"{oem_product_code}/{serial_number}"
                    else:
                        barcode_item["data"] = ""

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

    def print_qr(self, serial_number, sap_data):
        try:
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
                    value_data["content"] = sap_data.get("PRODUCT_CODE", "")
                elif value_id == "SERIAL_NUMBER":
                    value_data["content"] = sap_data.get("SERIAL_NUMBER", "")
                elif value_id == "BT_NAME":
                    value_data["content"] = sap_data.get("BT_NAME", "")
                elif value_id == "PIN_CODE":
                    value_data["content"] = sap_data.get("PIN_CODE", "")
                elif value_data["valueId"] == "LOGO_NAME":
                    logo_name = sap_data.get("LOGO_NAME", "")
                    if logo_name:
                        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                        images_dir = os.path.join(project_root, "database", "images")
                        image_path = os.path.join(images_dir, f"{logo_name}.png")
                        if os.path.exists(image_path):
                            with open(image_path, "rb") as img_file:
                                encoded = base64.b64encode(img_file.read()).decode("ascii")
                            value_data["type"] = "image"
                            value_data["content"] = ""
                            value_data["imageFile"] = encoded
                elif value_data["valueId"] == "OEM_COMPANY_NAME":
                    value_data["content"] = sap_data.get("OEM_COMPANY_NAME", "")

            pin_code = sap_data.get("PIN_CODE", "")
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


    def create_arcelik_serial_number(self, OemProductCode2, serial_number):
        '''
        STOK KODU (10 hane)       : OemProductCode2 
        YIL (2 hane)              : DATE_NUMBER
        SERİ NUMARASI (6 hane)    : kendi ürettiğimiz seri numarasının son 5 hanesi başında 1 olacak şekilde ÖRNEK 101148471138      
                                    5 hanesi : 71138     başında 1 koyarak :  171138
        AY (2 hane)               : DATE_NUMBER
        PAKET ADEDİ (2 hane)      : zaten paketlerde 1 cihaz olacağı için bütün hepsinde 01 koyacağız hepsinde 
        '''
        try:
            # Şu anki yıl ve ayı al
            now = datetime.now()
            year = now.strftime("%y")  # 2 haneli yıl (örn: 24)
            month = now.strftime("%m")  # 2 haneli ay (örn: 01, 12)
            
            # Serial number'ı string'e çevir ve son 5 hanesini al, başına 1 ekle
            serial_str = str(serial_number)
            last_5_digits = serial_str[-5:] if len(serial_str) >= 5 else serial_str.zfill(5)
            serial_with_prefix = "1" + last_5_digits  # Başına 1 ekle (örn: 171138)
            
            arcelik_serial_number = OemProductCode2 + year + serial_with_prefix + month + "01"
            return arcelik_serial_number
        except Exception as e:
            print(f"create_arcelik_serial_number error: {e}")
            return None



