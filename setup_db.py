import sqlite3
import os

# Connect to SQLite (this will create cricbuzz.db inside the database folder)
db_path = os.path.join('database', 'cricbuzz.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Read the schema.sql file
with open('database/schema.sql', 'r') as file:
    sql_script = file.read()

# Execute the SQL script
cursor.executescript(sql_script)

# Save and close the connection
conn.commit()
conn.close()

print(f"Database created successfully at {db_path}!")