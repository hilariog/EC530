import os
import sys
import sqlite3
import unittest
import pandas as pd
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) #set parent path

from schema_conflicts import (
    create_table_dynamically,
    table_exists,
    get_existing_schema,
    load_csv_and_create_table_with_interactive_conflict
)

class TestCSVtoSQLiteDynamicConflictInteractive(unittest.TestCase):
    def setUp(self):
        # Setup temporary database and CSV file.
        self.db_path = "test_interactive.db"
        self.csv_path = "test_interactive_data.csv"
        self.table_name = "interactive_table"
        
        # Create a sample DataFrame with columns: id, name, value.
        self.sample_data = pd.DataFrame({
            "id": [1, 2],
            "name": ["Alice", "Bob"],
            "value": [3.14, 2.71]
        })
        self.sample_data.to_csv(self.csv_path, index=False)
        
        # Pre-create the table with a conflict on the 'value' column.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Here, we intentionally define "value" as TEXT instead of REAL.
        create_sql = f"CREATE TABLE IF NOT EXISTS {self.table_name} (id INTEGER, name TEXT, value TEXT);"
        cursor.execute(create_sql)
        conn.commit()
        conn.close()
    
    def tearDown(self):
        # Remove temporary files after each test.
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)
    
    @patch('builtins.input', side_effect=["S"])  # Simulate "Skip" for the type conflict.
    def test_handle_conflict_skip(self, mock_input):
        # With simulated input "S", the conflicting column 'value' should be skipped.
        df = load_csv_and_create_table_with_interactive_conflict(self.csv_path, self.db_path, self.table_name)
        
        # Verify that 'value' column was removed from the dataframe (since user chose skip).
        self.assertNotIn("value", df.columns)
        
        # Verify that data was inserted. Since 'value' is skipped, only 'id' and 'name' should be inserted.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {self.table_name} ORDER BY id;")
        rows = cursor.fetchall()
        conn.close()
        self.assertEqual(len(rows), 2)
        # The 'value' column in the table should be NULL for inserted rows.
        self.assertEqual(rows[0][0], 1)
        self.assertEqual(rows[0][1], "Alice")
    
    @patch('builtins.input', side_effect=["R", "value_new"])
    def test_handle_conflict_rename(self, mock_input):
        # With simulated input "R" and then "value_new", the conflicting column should be renamed.
        df = load_csv_and_create_table_with_interactive_conflict(self.csv_path, self.db_path, self.table_name)
        # The dataframe should now have 'value_new' instead of 'value'.
        self.assertIn("value_new", df.columns)
        
        # Verify that data was inserted and the new column exists.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({self.table_name});")
        schema_info = cursor.fetchall()
        conn.close()
        columns = [col_info[1] for col_info in schema_info]
        self.assertIn("value_new", columns)
    
    @patch('builtins.input', side_effect=["O"])
    def test_handle_conflict_overwrite(self, mock_input):
        # With simulated input "O", the table will be dropped and recreated.
        df = load_csv_and_create_table_with_interactive_conflict(self.csv_path, self.db_path, self.table_name)
        # Verify that the recreated table has the inferred schema for all columns.
        inferred_schema, _ = ("id INTEGER, name TEXT, value REAL", None)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({self.table_name});")
        schema_info = cursor.fetchall()
        conn.close()
        columns = {col_info[1]: col_info[2] for col_info in schema_info}
        self.assertEqual(columns.get("value"), "REAL")
    
if __name__ == "__main__":
    unittest.main()
