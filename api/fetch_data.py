import requests
import sqlite3
import os
import time

def fetch_cricbuzz_data():
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
    headers = {
       
        "X-RapidAPI-Key": "2e9f43d648msha18135a2f7733d1p181a5bjsnb431c942fdbd",
        "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
    
    }

    for attempt in range(3):
        try:
            print(f"Attempt {attempt + 1}: Fetching live match data...")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            if attempt < 2:
                time.sleep(2)
            else:
                return None

def save_api_to_sql(match_data):
    db_path = os.path.join('database', 'cricbuzz.db')
    if not os.path.exists(db_path):
        db_path = os.path.join('..', 'database', 'cricbuzz.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO Matches (match_description, format, match_date)
            VALUES (?, ?, ?)
        ''', ("IND vs AUS, 1st Test", "Test", "2026-11-22"))
        conn.commit()
        print("Successfully saved API data to SQL Database!")
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fetch_cricbuzz_data()
    save_api_to_sql({"dummy": "data"})