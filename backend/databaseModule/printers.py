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
        
        # Migration: Eğer tablo zaten varsa ve printer_name kolonu yoksa ekle
        self._migrate_bitmap_settings_table()
        
        return result
    
    def _migrate_bitmap_settings_table(self):
        """Migrate existing bitmap_settings table to add printer_name column"""
        try:
            # Tablonun var olup olmadığını kontrol et
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bitmap_settings'")
            if not cursor.fetchone():
                return  # Tablo yok, yeni oluşturulacak
            
            # printer_name kolonunun var olup olmadığını kontrol et
            table_info = self.execute_query("PRAGMA table_info(bitmap_settings)")
            has_printer_name = any(col.get('name') == 'printer_name' for col in table_info)
            
            if not has_printer_name:
                print("Migration: Adding printer_name column to bitmap_settings table")
                # printer_name kolonunu ekle (NOT NULL constraint olmadan, sonra güncelleyeceğiz)
                if not self.execute_update("ALTER TABLE bitmap_settings ADD COLUMN printer_name TEXT"):
                    print("Migration: Failed to add printer_name column")
                    return
                
                # Mevcut kayıtlar için printer_name'i printer tablosundan al
                # Eğer printer bulunamazsa, printer_ip'yi kullan
                existing_settings = self.execute_query("SELECT DISTINCT printer_ip FROM bitmap_settings")
                for setting in existing_settings:
                    printer_ip = setting.get('printer_ip')
                    if not printer_ip:
                        continue
                    
                    # Bu IP'ye sahip printer'ı bul
                    printers = self.execute_query("SELECT name FROM printers WHERE ip = ? LIMIT 1", (printer_ip,))
                    if printers and printers[0].get('name'):
                        printer_name = printers[0]['name']
                        # Bu IP'ye sahip tüm bitmap ayarlarını güncelle
                        self.execute_update("UPDATE bitmap_settings SET printer_name = ? WHERE printer_ip = ?", 
                                          (printer_name, printer_ip))
                    else:
                        # Printer bulunamadı, IP'yi kullan
                        self.execute_update("UPDATE bitmap_settings SET printer_name = ? WHERE printer_ip = ?", 
                                          (printer_ip, printer_ip))
                
                print("Migration: printer_name column added and populated successfully")
        except Exception as e:
            print(f"Migration error: {e}")
            import traceback
            traceback.print_exc()
            # Hata olsa bile devam et, çünkü yeni tablolarda sorun olmayacak

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
        
        # Migration kontrolü: Eğer printer_name kolonu yoksa ekle
        has_printer_name_col = self._has_printer_name_column()
        if not has_printer_name_col:
            print("Database: printer_name column not found, running migration...")
            self._migrate_bitmap_settings_table()
            has_printer_name_col = self._has_printer_name_column()
        
        # Check if settings already exist for this printer (ip + name combination) and settings name
        existing = self.get_bitmap_settings(printer_ip, printer_name, name)
        print(f"Database: Existing settings found: {len(existing) if existing else 0}")
        
        if has_printer_name_col:
            # Yeni format: printer_name kolonu var
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
        else:
            # Eski format: printer_name kolonu yok (geriye dönük uyumluluk)
            if existing:
                # Update existing settings
                query = "UPDATE bitmap_settings SET settings_data = ?, updated_at = CURRENT_TIMESTAMP WHERE printer_ip = ? AND name = ?"
                result = self.execute_update(query, (settings_data, printer_ip, name))
                print(f"Database: Update result (legacy): {result}")
                return result
            else:
                # Insert new settings
                query = "INSERT INTO bitmap_settings (printer_ip, name, settings_data) VALUES (?, ?, ?)"
                result = self.execute_update(query, (printer_ip, name, settings_data))
                print(f"Database: Insert result (legacy): {result}")
                return result

    def _has_printer_name_column(self) -> bool:
        """Check if printer_name column exists in bitmap_settings table"""
        try:
            # Önce tablonun var olup olmadığını kontrol et
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bitmap_settings'")
            if not cursor.fetchone():
                return False  # Tablo yok
            
            table_info = self.execute_query("PRAGMA table_info(bitmap_settings)")
            return any(col.get('name') == 'printer_name' for col in table_info)
        except Exception as e:
            print(f"Error checking printer_name column: {e}")
            return False
    
    def get_bitmap_settings(self, printer_ip: str, printer_name: str = None, name: str = None) -> List[Dict[str, Any]]:
        """Get bitmap settings for a printer"""
        print(f"Database: Getting bitmap settings for {printer_ip} (printer: {printer_name}) with settings name: {name}")
        
        has_printer_name_col = self._has_printer_name_column()
        
        if has_printer_name_col:
            # Yeni format: printer_name kolonu var
            if printer_name and name:
                # Hem printer name hem de settings name belirtilmiş
                query = "SELECT * FROM bitmap_settings WHERE printer_ip = ? AND printer_name = ? AND name = ?"
                result = self.execute_query(query, (printer_ip, printer_name, name))
            elif printer_name:
                # Sadece printer name belirtilmiş
                query = "SELECT * FROM bitmap_settings WHERE printer_ip = ? AND printer_name = ?"
                result = self.execute_query(query, (printer_ip, printer_name))
            elif name:
                # Sadece settings name belirtilmiş
                query = "SELECT * FROM bitmap_settings WHERE printer_ip = ? AND name = ?"
                result = self.execute_query(query, (printer_ip, name))
            else:
                # Sadece IP belirtilmiş
                query = "SELECT * FROM bitmap_settings WHERE printer_ip = ?"
                result = self.execute_query(query, (printer_ip,))
        else:
            # Eski format: printer_name kolonu yok (geriye dönük uyumluluk)
            if name:
                query = "SELECT * FROM bitmap_settings WHERE printer_ip = ? AND name = ?"
                result = self.execute_query(query, (printer_ip, name))
            else:
                query = "SELECT * FROM bitmap_settings WHERE printer_ip = ?"
                result = self.execute_query(query, (printer_ip,))
        
        return result

    def get_all_bitmap_settings(self) -> List[Dict[str, Any]]:
        """Get all bitmap settings"""
        return self.execute_query("SELECT * FROM bitmap_settings ORDER BY printer_ip, name")

    def delete_bitmap_settings(self, printer_ip: str, printer_name: str, name: str) -> bool:
        """Delete bitmap settings"""
        has_printer_name_col = self._has_printer_name_column()
        if has_printer_name_col:
            query = "DELETE FROM bitmap_settings WHERE printer_ip = ? AND printer_name = ? AND name = ?"
            return self.execute_update(query, (printer_ip, printer_name, name))
        else:
            # Eski format: printer_name kolonu yok
            query = "DELETE FROM bitmap_settings WHERE printer_ip = ? AND name = ?"
            return self.execute_update(query, (printer_ip, name))

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
            has_printer_name_col = self._has_printer_name_column()
            
            if has_printer_name_col:
                query = "SELECT * FROM bitmap_settings WHERE printer_ip = ? AND printer_name = ? AND name = ? LIMIT 1"
                result = self.execute_query(query, (ip, printer_name, settings_name))
            else:
                # Eski format: printer_name kolonu yok
                query = "SELECT * FROM bitmap_settings WHERE printer_ip = ? AND name = ? LIMIT 1"
                result = self.execute_query(query, (ip, settings_name))
            
            if result:
                return result[0]["settings_data"]
            return None
        except Exception as e:
            print(f"Error getting printer data by name: {e}")
            return None
    
    def get_printer_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Get printer by name"""
        return self.execute_query("SELECT * FROM printers WHERE name = ?", (name,))

