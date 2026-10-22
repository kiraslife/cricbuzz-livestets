import unittest
import os
import sqlite3
import sys

# Allow the test script to find our utils folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.db_connection import get_connection

class TestDatabase(unittest.TestCase):
    
    def test_db_exists(self):
        """Test 1: Check if the SQLite database file was created."""
        db_path = os.path.join('database', 'cricbuzz.db')
        self.assertTrue(os.path.exists(db_path), "❌ Database file is missing!")

    def test_connection(self):
        """Test 2: Check if the connection function works."""
        conn = get_connection()
        self.assertIsInstance(conn, sqlite3.Connection, "❌ Failed to connect to DB!")
        conn.close()

if __name__ == '__main__':
    unittest.main()