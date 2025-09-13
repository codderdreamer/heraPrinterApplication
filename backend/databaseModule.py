import sqlite3
import os

class DatabaseModule:
    def __init__(self, config) -> None:
        self.config = config
        
        self.connection = None
        self._create_database()
        self.connect()
    
    def _create_database(self):
        '''
        Create database directory if it doesn't exist
        '''
        try:
            os.makedirs(os.path.dirname(self.config.database_path), exist_ok=True)
            return True
        except Exception as e:
            print(f"create_database {e}")
            return False
            
    def connect(self):
        """Connect to SQLite database"""
        try:
            self._create_database()
            self.connection = sqlite3.connect(self.config.database_path)
            self.connection.row_factory = sqlite3.Row  # This enables column access by name
            print(f"Connected to database: {self.config.database_path}")
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            
    def disconnect(self):
        """Disconnect from SQLite database"""
        if self.connection:
            self.connection.close()
            print("Disconnected from database")
        else:
            print("No active database connection to close")
            
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results as list of dictionaries"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Query execution error: {e}")
            return []
        

    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """Execute INSERT, UPDATE, or DELETE query and return success status"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Query execution error: {e}")
            return False
        
        