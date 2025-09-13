from backend.databaseModule.databaseModule import DatabaseModule
from typing import List, Dict, Any
from backend.configModule import DatabaseConfig

class Printers(DatabaseModule):
    def __init__(self):
        self.databaseConfig = DatabaseConfig()
        super().__init__(self.databaseConfig.database_path)
        
        self.create_printers_table()
        print("test")
        
    
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
