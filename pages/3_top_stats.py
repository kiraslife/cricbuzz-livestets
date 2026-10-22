import streamlit as st
import pandas as pd
from utils.db_connection import execute_query

st.set_page_config(page_title="Top Player Statistics", page_icon="🏆", layout="wide")

st.title("🏆 Player Leaderboards & Performance Metrics")
st.markdown("Top performing athletes across batting and bowling departments based on real historical records.")

# Queries
runs_query = """
SELECT p.full_name AS Player, SUM(pms.runs_scored) AS Runs
FROM Players p
JOIN Player_Match_Stats pms ON p.player_id = pms.player_id
GROUP BY p.player_id
ORDER BY Runs DESC LIMIT 5;
"""

wickets_query = """
SELECT p.full_name AS Player, SUM(pms.wickets_taken) AS Wickets
FROM Players p
JOIN Player_Match_Stats pms ON p.player_id = pms.player_id
GROUP BY p.player_id
ORDER BY Wickets DESC LIMIT 5;
"""

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏏 Elite Run Scorers")
    try:
        runs_df = execute_query(runs_query)
        if not runs_df.empty:
            st.bar_chart(data=runs_df.set_index("Player")["Runs"], color="#ff4b4b", use_container_width=True)
            st.dataframe(runs_df, use_container_width=True)
        else:
            st.info("No run data available.")
    except Exception as e:
        st.error(f"Error: {e}")

with col2:
    st.subheader("🎯 Elite Wicket Takers")
    try:
        wickets_df = execute_query(wickets_query)
        if not wickets_df.empty:
            st.bar_chart(data=wickets_df.set_index("Player")["Wickets"], color="#21c354", use_container_width=True)
            st.dataframe(wickets_df, use_container_width=True)
        else:
            st.info("No wicket data available.")
    except Exception as e:
        st.error(f"Error: {e}")