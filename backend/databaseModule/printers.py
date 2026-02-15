from typing import List, Dict, Any

# Import with PyInstaller compatibility
try:
    from backend.databaseModule.databaseModule import DatabaseModule
    from backend.configModule import DatabaseConfig
except ImportError:
    # Fallback for PyInstaller
    from databaseModule import DatabaseModule
    from configModule import DatabaseConfig

class Printers(DatabaseModule):
    def __init__(self):
        self.databaseConfig = DatabaseConfig()
        super().__init__(self.databaseConfig.database_path)
        
        self.create_printers_table()
        self.create_bitmap_settings_table()
        
    
    def create_printers_table(self):
        """Create printers table"""
        printers_columns = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "ip": "TEXT NOT NULL",
            "name": "TEXT NOT NULL",
            "dpi": "INTEGER NOT NULL",
            "width": "INTEGER NOT NULL",
            "height": "INTEGER NOT NULL"
        }
        return self.create_table("printers", printers_columns)

    def create_bitmap_settings_table(self):
        """Create bitmap settings table"""
        bitmap_settings_columns = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "printer_ip": "TEXT NOT NULL",
            "printer_name": "TEXT NOT NULL",  # Printer'ın adı (aynı IP'de farklı printer'lar için)
            "name": "TEXT NOT NULL",  # Bitmap ayarının adı (default, test, vb.)
            "settings_data": "TEXT NOT NULL",  # JSON string
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }
        result = self.create_table("bitmap_settings", bitmap_settings_columns)
        
        # Eğer tablo zaten varsa ve printer_name kolonu yoksa ekle (migration)
        try:
            self.execute_query("SELECT printer_name FROM bitmap_settings LIMIT 1")
        except:
            # printer_name kolonu yok, ekle
            try:
                self.execute_update("ALTER TABLE bitmap_settings ADD COLUMN printer_name TEXT")
                # Mevcut kayıtlar için printer_name'i printer_ip'den al (geçici çözüm)
                self.execute_update("UPDATE bitmap_settings SET printer_name = printer_ip WHERE printer_name IS NULL")
            except Exception as e:
                print(f"Migration warning: {e}")
        
        return result

    def insert_printer(self, ip: str, name: str, dpi: int, width: int, height: int) -> bool:
        """Insert a new printer"""
        query = "INSERT INTO printers (ip, name, dpi, width, height) VALUES (?, ?, ?, ?, ?)"
        return self.execute_update(query, (ip, name, dpi, width, height))

    def get_all_printers(self) -> List[Dict[str, Any]]:
        """Get all printers"""
        return self.execute_query("SELECT * FROM printers")

    def get_printer_by_id(self, printer_id: int) -> List[Dict[str, Any]]:
        """Get printer by ID"""
        return self.execute_query("SELECT * FROM printers WHERE id = ?", (printer_id,))

    def get_printer_by_ip(self, ip: str) -> List[Dict[str, Any]]:
        """Get printer by IP"""
        return self.execute_query("SELECT * FROM printers WHERE ip = ?", (ip,))

    def update_printer(self, printer_id: int, ip: str, name: str, dpi: int, width: int, height: int) -> bool:
        """Update printer"""
        query = "UPDATE printers SET ip = ?, name = ?, dpi = ?, width = ?, height = ? WHERE id = ?"
        return self.execute_update(query, (ip, name, dpi, width, height, printer_id))

    def delete_printer(self, printer_id: int) -> bool:
        """Delete printer"""
        query = "DELETE FROM printers WHERE id = ?"
        return self.execute_update(query, (printer_id,))

    def search_printers_by_name(self, name_pattern: str) -> List[Dict[str, Any]]:
        """Search printers by name pattern"""
        query = "SELECT * FROM printers WHERE name LIKE ?"
        return self.execute_query(query, (f"%{name_pattern}%",))

    def get_printer_count(self) -> int:
        """Get total number of printers"""
        result = self.execute_query("SELECT COUNT(*) as count FROM printers")
        return result[0]["count"] if result else 0

    # Bitmap Settings Methods
    def save_bitmap_settings(self, printer_ip: str, printer_name: str, name: str, settings_data: str) -> bool:
        """Save bitmap settings for a printer"""
        print(f"Database: Saving bitmap settings for {printer_ip} (printer: {printer_name}) with settings name: {name}")
        print(f"Database: Settings data length: {len(settings_data)}")
        
        # Check if settings already exist for this printer (ip + name combination) and settings name
        existing = self.get_bitmap_settings(printer_ip, printer_name, name)
        print(f"Database: Existing settings found: {len(existing) if existing else 0}")
        
        if existing:
            # Update existing settings
            query = "UPDATE bitmap_settings SET settings_data = ?, updated_at = CURRENT_TIMESTAMP WHERE printer_ip = ? AND printer_name = ? AND name = ?"
            result = self.execute_update(query, (settings_data, printer_ip, printer_name, name))
            print(f"Database: Update result: {result}")
            return result
        else:
            # Insert new settings
            query = "INSERT INTO bitmap_settings (printer_ip, printer_name, name, settings_data) VALUES (?, ?, ?, ?)"
            result = self.execute_update(query, (printer_ip, printer_name, name, settings_data))
            print(f"Database: Insert result: {result}")
            return result

    def get_bitmap_settings(self, printer_ip: str, printer_name: str = None, name: str = None) -> List[Dict[str, Any]]:
        """Get bitmap settings for a printer"""
        print(f"Database: Getting bitmap settings for {printer_ip} (printer: {printer_name}) with settings name: {name}")
        
        if printer_name and name:
            # Hem printer name hem de settings name belirtilmiş
            query = "SELECT * FROM bitmap_settings WHERE printer_ip = ? AND printer_name = ? AND name = ?"
            result = self.execute_query(query, (printer_ip, printer_name, name))
        elif printer_name:
            # Sadece printer name belirtilmiş
            query = "SELECT * FROM bitmap_settings WHERE printer_ip = ? AND printer_name = ?"
            result = self.execute_query(query, (printer_ip, printer_name))
        elif name:
            # Sadece settings name belirtilmiş (geriye dönük uyumluluk)
            query = "SELECT * FROM bitmap_settings WHERE printer_ip = ? AND name = ?"
            result = self.execute_query(query, (printer_ip, name))
        else:
            # Sadece IP belirtilmiş (geriye dönük uyumluluk)
            query = "SELECT * FROM bitmap_settings WHERE printer_ip = ?"
            result = self.execute_query(query, (printer_ip,))
        
        return result

    def get_all_bitmap_settings(self) -> List[Dict[str, Any]]:
        """Get all bitmap settings"""
        return self.execute_query("SELECT * FROM bitmap_settings ORDER BY printer_ip, name")

    def delete_bitmap_settings(self, printer_ip: str, printer_name: str, name: str) -> bool:
        """Delete bitmap settings"""
        query = "DELETE FROM bitmap_settings WHERE printer_ip = ? AND printer_name = ? AND name = ?"
        return self.execute_update(query, (printer_ip, printer_name, name))

    def get_default_bitmap_settings(self, printer_ip: str) -> Dict[str, Any]:
        """Get default bitmap settings for a printer (first one if exists)"""
        settings = self.get_bitmap_settings(printer_ip)
        if settings:
            return settings[0]
        return None

    def get_printer_ip_by_name(self, printer_name: str) -> Dict[str, Any]:
        try:
            query = "SELECT ip FROM printers WHERE name = ?"
            result = self.execute_query(query, (printer_name,))
            if result:
                return result[0]["ip"]
            return None
        except Exception as e:
            print(f"Error getting printer IP by name: {e}")
            return None

    def get_printer_data_by_ip(self, ip: str) -> Dict[str, Any]:
        """Get printer data by IP (geriye dönük uyumluluk için - ilk bulunan ayarı döndürür)"""
        try:
            query = "SELECT * FROM bitmap_settings WHERE printer_ip = ? LIMIT 1"
            result = self.execute_query(query, (ip,))
            if result:
                return result[0]["settings_data"]
            return None
        except Exception as e:
            print(f"Error getting printer data by IP: {e}")
            return None
    
    def get_printer_data_by_name(self, printer_name: str, settings_name: str = "default") -> Dict[str, Any]:
        """Get printer bitmap settings by printer name"""
        try:
            # Önce printer'ın IP'sini bul
            printer = self.get_printer_by_name(printer_name)
            if not printer:
                return None
            
            ip = printer[0]["ip"]
            query = "SELECT * FROM bitmap_settings WHERE printer_ip = ? AND printer_name = ? AND name = ? LIMIT 1"
            result = self.execute_query(query, (ip, printer_name, settings_name))
            if result:
                return result[0]["settings_data"]
            return None
        except Exception as e:
            print(f"Error getting printer data by name: {e}")
            return None
    
    def get_printer_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Get printer by name"""
        return self.execute_query("SELECT * FROM printers WHERE name = ?", (name,))

