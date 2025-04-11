#!/usr/bin/env python3
import os
import sys
import sqlite3
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import functions from our AI SQL generator module.
from embedded_llm import get_table_schema, generate_sql_from_prompt

class TestAISQLGenerator(unittest.TestCase):
    def setUp(self):
        # Create a temporary SQLite database with a test table.
        self.db_path = "assistant.db"
        self.table_name = "test_table"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {self.table_name};")
        cursor.execute(f"CREATE TABLE {self.table_name} (id INTEGER, name TEXT, value REAL);")
        conn.commit()
        conn.close()
    
    def tearDown(self):
        import os
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_get_table_schema(self):
        schema = get_table_schema(self.db_path, self.table_name)
        expected_parts = ["id INTEGER", "name TEXT", "value REAL"]
        for part in expected_parts:
            self.assertIn(part, schema)
    
    @patch("embedded_llm.client.models.generate_content")
    def test_generate_sql_from_prompt(self, mock_generate):
        # Simulate a response from the GenAI API.
        fake_response = MagicMock()
        fake_response.text = (
            "You are an SQL generation assistant. Given the following table schema:\n"
            "id INTEGER, name TEXT, value REAL\n"
            "and the following user request:\n"
            "show me rows where value > 3\n"
            "Generate a valid SQL query for a SQLite database. Do not include any commentary.\n"
            "SELECT * FROM test_table WHERE value > 3;"
        )
        mock_generate.return_value = fake_response

        schema = "id INTEGER, name TEXT, value REAL"
        user_request = "show me rows where value > 3"
        sql_query = generate_sql_from_prompt(schema, user_request, self.table_name)
        self.assertIn("SELECT", sql_query)
        self.assertIn("test_table", sql_query)
    
if __name__ == "__main__":
    unittest.main()
