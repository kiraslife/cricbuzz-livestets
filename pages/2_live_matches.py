import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.fetch_data import fetch_cricbuzz_data

st.set_page_config(page_title="Live Matches", page_icon="🔴", layout="wide")
st.title("🔴 Live & Recent Cricket Scoreboard")
st.markdown("Fetches real-time match data from the Cricbuzz API, displays human-readable scorecards, and syncs matches to the SQL database.")

def sync_api_matches_to_db(parsed_matches):
    """Saves parsed live API matches directly into the SQLite database."""
    db_path = os.path.join('database', 'cricbuzz.db')
    if not os.path.exists(db_path):
        db_path = os.path.join('..', 'database', 'cricbuzz.db')
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    saved_count = 0

    for m in parsed_matches:
        try:
            # 1. Insert Teams if they don't exist
            cursor.execute("INSERT OR IGNORE INTO Teams (team_name) VALUES (?)", (m['Team 1'],))
            cursor.execute("INSERT OR IGNORE INTO Teams (team_name) VALUES (?)", (m['Team 2'],))
            
            cursor.execute("SELECT team_id FROM Teams WHERE team_name = ?", (m['Team 1'],))
            t1_id = cursor.fetchone()[0]
            cursor.execute("SELECT team_id FROM Teams WHERE team_name = ?", (m['Team 2'],))
            t2_id = cursor.fetchone()[0]

            # 2. Insert Venue
            cursor.execute(
                "INSERT OR IGNORE INTO Venues (venue_name, city, country, capacity) VALUES (?, ?, ?, ?)",
                (m['Venue'], m['City'], 'International', 45000)
            )
            cursor.execute("SELECT venue_id FROM Venues WHERE venue_name = ?", (m['Venue'],))
            venue_id = cursor.fetchone()[0]

            # 3. Insert Match
            cursor.execute("""
                INSERT INTO Matches (match_description, format, venue_id, match_date, team1_id, team2_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (f"{m['Team 1']} vs {m['Team 2']} ({m['Match']})", m['Format'], venue_id, m['Date'], t1_id, t2_id))
            saved_count += 1
        except Exception:
            continue

    conn.commit()
    conn.close()
    return saved_count

if st.button("📡 Fetch Live Scores & Sync to Database"):
    with st.spinner("Fetching live data from Cricbuzz API..."):
        live_data = fetch_cricbuzz_data()
        
        if live_data and "typeMatches" in live_data:
            parsed_matches = []
            
            # Navigate the exact Cricbuzz RapidAPI JSON hierarchy
            for match_type_block in live_data.get("typeMatches", []):
                m_Category = match_type_block.get("matchType", "International")
                for series_block in match_type_block.get("seriesMatches", []):
                    wrapper = series_block.get("seriesAdWrapper", {})
                    series_name = wrapper.get("seriesName", "Cricket Series")
                    
                    for match in wrapper.get("matches", []):
                        info = match.get("matchInfo", {})
                        score = match.get("matchScore", {})
                        
                        t1_name = info.get("team1", {}).get("teamName", "Team 1")
                        t2_name = info.get("team2", {}).get("teamName", "Team 2")
                        
                        # Extract Team 1 & Team 2 Scores safely
                        t1_inngs = score.get("team1Score", {}).get("inngs1", {})
                        t2_inngs = score.get("team2Score", {}).get("inngs1", {})
                        
                        t1_score_str = f"{t1_inngs.get('runs', 0)}/{t1_inngs.get('wickets', 0)} ({t1_inngs.get('overs', 0)} ov)" if t1_inngs else "Yet to bat"
                        t2_score_str = f"{t2_inngs.get('runs', 0)}/{t2_inngs.get('wickets', 0)} ({t2_inngs.get('overs', 0)} ov)" if t2_inngs else "Yet to bat"
                        
                        # Convert timestamp to readable date
                        start_ts = info.get("startDate")
                        match_date = datetime.fromtimestamp(int(start_ts)/1000).strftime('%Y-%m-%d') if start_ts else datetime.today().strftime('%Y-%m-%d')
                        
                        parsed_matches.append({
                            "Category": m_Category,
                            "Series": series_name,
                            "Match": info.get("matchDesc", "Match"),
                            "Format": info.get("matchFormat", "T20"),
                            "Team 1": t1_name,
                            "Team 1 Score": t1_score_str,
                            "Team 2": t2_name,
                            "Team 2 Score": t2_score_str,
                            "Status": info.get("status", "In Progress"),
                            "Venue": info.get("venueInfo", {}).get("ground", "Unknown Ground"),
                            "City": info.get("venueInfo", {}).get("city", "Unknown City"),
                            "Date": match_date
                        })

            if parsed_matches:
                saved = sync_api_matches_to_db(parsed_matches)
                st.success(f"✅ Loaded {len(parsed_matches)} live/recent matches from Cricbuzz API and synced {saved} records to SQLite!")
                
                # 1. Display clean summary cards for top 3 matches
                st.subheader("🏏 Featured Match Scorecards")
                cols = st.columns(3)
                for idx, m in enumerate(parsed_matches[:3]):
                    with cols[idx]:
                        st.markdown(f"""
                        <div style="padding:15px; border-radius:10px; background-color:#1e2129; border-left: 5px solid #ff4b4b; margin-bottom:10px;">
                            <small style="color:#a0a8b8;">{m['Series']} • {m['Format']}</small>
                            <h4 style="margin:5px 0;">{m['Team 1']} vs {m['Team 2']}</h4>
                            <p style="margin:2px 0;"><b>{m['Team 1']}:</b> {m['Team 1 Score']}</p>
                            <p style="margin:2px 0;"><b>{m['Team 2']}:</b> {m['Team 2 Score']}</p>
                            <p style="color:#4caf50; margin-top:8px;"><b>📌 {m['Status']}</b></p>
                            <small>🏟️ {m['Venue']}, {m['City']}</small>
                        </div>
                        """, unsafe_allow_html=True)

                # 2. Display Full Clean Table for all matches
                st.subheader("📋 All Live & Recent Matches Table")
                df_matches = pd.DataFrame(parsed_matches)
                st.dataframe(df_matches, use_container_width=True)
                
                # Optional expander for developers
                with st.expander("🔍 View Raw JSON (For Debugging Only)"):
                    st.json(live_data)
            else:
                st.warning("Connected to API, but no match records were found in the payload.")
        else:
            st.error("❌ Failed to fetch data from Cricbuzz API. Check your RapidAPI quota or key.")