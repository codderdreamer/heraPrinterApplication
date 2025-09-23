from backend.databaseModule.databaseModule import DatabaseModule
from typing import List, Dict, Any
from backend.configModule import DatabaseConfig
import socket
import time

class Printers(DatabaseModule):
    def __init__(self):
        self.databaseConfig = DatabaseConfig()
        super().__init__(self.databaseConfig.database_path)
        
        self.create_printers_table()
        
    
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

    def check_printer_connection(self, ip: str, port: int = 9100, timeout: int = 3) -> bool:
        """Check if printer is online and reachable"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except Exception as e:
            print(f"Connection check error for {ip}: {e}")
            return False

    def get_printer_status(self, ip: str) -> Dict[str, Any]:
        """Get printer status including connection info"""
        printer_data = self.get_printer_by_ip(ip)
        if not printer_data:
            return {"error": "Printer not found"}
        
        printer = printer_data[0]
        is_online = self.check_printer_connection(ip)
        
        return {
            "id": printer["id"],
            "ip": printer["ip"],
            "name": printer["name"],
            "dpi": printer["dpi"],
            "width": printer["width"],
            "height": printer["height"],
            "is_online": is_online,
            "status": "Online" if is_online else "Offline"
        }

    def get_all_printers_with_status(self) -> List[Dict[str, Any]]:
        """Get all printers with their connection status"""
        printers = self.get_all_printers()
        result = []
        
        for printer in printers:
            is_online = self.check_printer_connection(printer["ip"])
            printer_with_status = {
                **printer,
                "is_online": is_online,
                "status": "Online" if is_online else "Offline"
            }
            result.append(printer_with_status)
        
        return result

    def get_printer_count(self) -> int:
        """Get total number of printers"""
        result = self.execute_query("SELECT COUNT(*) as count FROM printers")
        return result[0]["count"] if result else 0
