#!/usr/bin/env python3
import os
import sqlite3
import unittest
import pandas as pd
import sys

# Add the parent directory (the repository root) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from csv_to_sql import create_table_manually, load_csv_to_dataframe, load_dataframe_to_sqlite, run_basic_query

class TestCSVtoSQLite(unittest.TestCase):
    def setUp(self):
        # Setup temporary test files and parameters
        self.db_path = "test_example.db"
        self.csv_path = "test_sample_data.csv"
        self.table_name = "test_data_table"
        
        # Create a sample CSV file for testing
        sample_data = pd.DataFrame({
            "id": [1, 2, 3, 4],
            "name": ["Alice", "Bob", "Charlie", "Diana"],
            "value": [3.14, 2.71, 1.41, 0.577]
        })
        sample_data.to_csv(self.csv_path, index=False)
        
        # Define a sample schema matching the CSV columns
        self.sample_schema = "id INTEGER, name TEXT, value REAL"
        create_table_manually(self.db_path, self.table_name, self.sample_schema)
    
    def tearDown(self):
        # Clean up test files after each test run
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)
    
    def test_load_csv_to_dataframe(self):
        df = load_csv_to_dataframe(self.csv_path)
        self.assertEqual(len(df), 4)
        self.assertListEqual(list(df.columns), ["id", "name", "value"])
    
    def test_load_dataframe_to_sqlite_and_query(self):
        df = load_csv_to_dataframe(self.csv_path)
        load_dataframe_to_sqlite(df, self.db_path, self.table_name, if_exists='replace')
        
        # Execute a basic query to retrieve all rows ordered by id.
        query = f"SELECT * FROM {self.table_name} ORDER BY id;"
        rows = run_basic_query(self.db_path, self.table_name, query)
        
        # Validate the number of rows and the content of the first row.
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0], (1, "Alice", 3.14))
    
if __name__ == "__main__":
    unittest.main()
