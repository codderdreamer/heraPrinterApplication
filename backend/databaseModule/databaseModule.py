import sqlite3
import os
from typing import List, Dict, Any

class DatabaseModule:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self.connection = None
        self._create_database()
        self.connect()
    
    def _create_database(self):
        '''
        Create database directory if it doesn't exist
        '''
        try:
            os.makedirs(os.path.dirname(self.database_path), exist_ok=True)
            return True
        except Exception as e:
            print(f"create_database {e}")
            return False
            
    def connect(self):
        """Connect to SQLite database"""
        try:
            self._create_database()
            # Thread-safe connection
            self.connection = sqlite3.connect(
                self.database_path, 
                check_same_thread=False
            )
            self.connection.row_factory = sqlite3.Row  # This enables column access by name
            print(f"Connected to database: {self.database_path}")
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

    def create_table(self, table_name: str, columns: dict) -> bool:
        """
        Create a table with given columns
        columns: dict - column_name: column_definition
        Example: {"id": "INTEGER PRIMARY KEY", "name": "TEXT NOT NULL", "age": "INTEGER"}
        """
        try:
            column_definitions = []
            for column_name, column_type in columns.items():
                column_definitions.append(f"{column_name} {column_type}")
            
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)})"
            return self.execute_update(query)
        except Exception as e:
            print(f"Table creation error: {e}")
            return False
