import sqlite3
import pandas as pd
import os

def get_connection():
    """Establishes a connection to the SQLite database."""
    db_path = os.path.join('database', 'cricbuzz.db')
    if not os.path.exists(db_path):
        db_path = os.path.join('..', 'database', 'cricbuzz.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row 
    return conn

def execute_query(query, params=()):
    """Executes a SQL query and returns a Pandas DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df