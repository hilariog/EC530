#!/usr/bin/env python3
import os
import sys
import sqlite3
import unittest
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) #set parent path

from dynamic_schema import map_dtype_to_sql, infer_schema_from_dataframe, create_table_dynamically, load_csv_and_create_table, run_basic_query

class TestCSVtoSQLiteDynamic(unittest.TestCase):
    def setUp(self):
        # Define temporary file names and table name
        self.db_path = "test_dynamic.db"
        self.csv_path = "test_dynamic_data.csv"
        self.table_name = "dynamic_table"
        
        # Create a sample DataFrame with multiple data types
        self.sample_data = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "value": [3.14, 2.71, 1.41],
            "active": [True, False, True]
        })
        self.sample_data.to_csv(self.csv_path, index=False)
    
    def tearDown(self):
        # Remove temporary files after each test
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)
    
    def test_map_dtype_to_sql(self):
        self.assertEqual(map_dtype_to_sql(self.sample_data["id"].dtype), "INTEGER")
        self.assertEqual(map_dtype_to_sql(self.sample_data["value"].dtype), "REAL")
        self.assertEqual(map_dtype_to_sql(self.sample_data["name"].dtype), "TEXT")
        # Boolean values are mapped to INTEGER in SQLite (1 for True, 0 for False)
        self.assertEqual(map_dtype_to_sql(self.sample_data["active"].dtype), "INTEGER")
    
    def test_infer_schema_from_dataframe(self):
        schema = infer_schema_from_dataframe(self.sample_data)
        expected_schema = "id INTEGER, name TEXT, value REAL, active INTEGER"
        self.assertEqual(schema, expected_schema)
    
    def test_load_csv_and_create_table(self):
        # Load CSV and create table dynamically
        df = load_csv_and_create_table(self.csv_path, self.db_path, self.table_name)
        self.assertEqual(len(df), 3)
        
        # Run a query to verify the data is inserted
        query = f"SELECT * FROM {self.table_name} ORDER BY id;"
        rows = run_basic_query(self.db_path, self.table_name, query)
        self.assertEqual(len(rows), 3)
        # SQLite stores booleans as 1 (True) or 0 (False)
        self.assertEqual(rows[0], (1, "Alice", 3.14, 1))
    
if __name__ == "__main__":
    unittest.main()
