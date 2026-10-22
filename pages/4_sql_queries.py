import streamlit as st
import pandas as pd
from utils.db_connection import execute_query

st.set_page_config(page_title="Cricket Analytics Dashboard", page_icon="📊", layout="wide")

st.title("📊 Advanced Cricket Intelligence & Analytics")
st.markdown("Explore deep statistical insights, team comparisons, and player trends through interactive visual dashboards.")

# Dictionary containing all 25 business analytical queries (Backend completely intact, SQL hidden from UI)
queries = {
    # ================= BEGINNER LEVEL =================
    "Q1: Indian Team Roster": """
        SELECT p.full_name AS Player, p.playing_role AS Role, p.batting_style AS Batting, p.bowling_style AS Bowling 
        FROM Players p JOIN Teams t ON p.team_id = t.team_id WHERE t.team_name = 'India';
    """,
    "Q2: Matches in Last 30 Days": """
        SELECT m.match_description AS Match, t1.team_name AS Team_1, t2.team_name AS Team_2, 
               v.venue_name || ', ' || v.city AS Venue, m.match_date AS Date 
        FROM Matches m 
        JOIN Teams t1 ON m.team1_id = t1.team_id 
        JOIN Teams t2 ON m.team2_id = t2.team_id 
        JOIN Venues v ON m.venue_id = v.venue_id 
        WHERE m.match_date >= date('now', '-30 days') 
        ORDER BY m.match_date DESC;
    """,
    "Q3: Top 10 Highest ODI Run Scorers": """
        SELECT p.full_name AS Player, SUM(pms.runs_scored) AS Total_Runs, 
               ROUND(CAST(SUM(pms.runs_scored) AS FLOAT) / COUNT(pms.stat_id), 2) AS Batting_Avg, 
               SUM(CASE WHEN pms.runs_scored >= 100 THEN 1 ELSE 0 END) AS Centuries 
        FROM Players p 
        JOIN Player_Match_Stats pms ON p.player_id = pms.player_id 
        JOIN Matches m ON pms.match_id = m.match_id 
        WHERE m.format = 'ODI' 
        GROUP BY p.player_id, p.full_name 
        ORDER BY Total_Runs DESC LIMIT 10;
    """,
    "Q4: Venues with >50k Capacity": """
        SELECT venue_name AS Venue, city AS City, country AS Country, capacity AS Capacity 
        FROM Venues WHERE capacity > 50000 ORDER BY capacity DESC;
    """,
    "Q5: Match Wins by Team": """
        SELECT t.team_name AS Team, COUNT(m.match_id) AS Total_Wins 
        FROM Teams t JOIN Matches m ON t.team_id = m.match_winner_id 
        GROUP BY t.team_name ORDER BY Total_Wins DESC;
    """,
    "Q6: Player Count by Role": """
        SELECT playing_role AS Role, COUNT(player_id) AS Player_Count 
        FROM Players GROUP BY playing_role;
    """,
    "Q7: Highest Individual Score by Format": """
        SELECT m.format AS Format, MAX(pms.runs_scored) AS Highest_Score 
        FROM Player_Match_Stats pms JOIN Matches m ON pms.match_id = m.match_id 
        GROUP BY m.format;
    """,
    "Q8: Series Starting in 2024": """
        SELECT series_name AS Series, host_country AS Host, match_type AS Type, start_date AS Start_Date, total_matches AS Matches 
        FROM Series WHERE strftime('%Y', start_date) = '2024';
    """,

    # ================= INTERMEDIATE LEVEL =================
    "Q9: All-Rounders (>1000 runs, >50 wickets)": """
        SELECT p.full_name AS Player, SUM(pms.runs_scored) AS Total_Runs, 
               SUM(pms.wickets_taken) AS Total_Wickets, m.format AS Format 
        FROM Players p 
        JOIN Player_Match_Stats pms ON p.player_id = pms.player_id 
        JOIN Matches m ON pms.match_id = m.match_id 
        WHERE p.playing_role = 'All-rounder' 
        GROUP BY p.player_id, p.full_name, m.format 
        HAVING SUM(pms.runs_scored) > 1000 AND SUM(pms.wickets_taken) > 50;
    """,
    "Q10: Details of Last 20 Completed Matches": """
        SELECT m.match_description AS Match, t1.team_name AS Team_1, t2.team_name AS Team_2, 
               tw.team_name AS Winner, m.victory_margin AS Margin, m.victory_type AS Type, v.venue_name AS Venue 
        FROM Matches m 
        JOIN Teams t1 ON m.team1_id = t1.team_id 
        JOIN Teams t2 ON m.team2_id = t2.team_id 
        JOIN Teams tw ON m.match_winner_id = tw.team_id 
        JOIN Venues v ON m.venue_id = v.venue_id 
        ORDER BY m.match_date DESC LIMIT 20;
    """,
    "Q11: Multi-Format Performance Comparison": """
        SELECT p.full_name AS Player, 
               SUM(CASE WHEN m.format = 'Test' THEN pms.runs_scored ELSE 0 END) AS Test_Runs, 
               SUM(CASE WHEN m.format = 'ODI' THEN pms.runs_scored ELSE 0 END) AS ODI_Runs, 
               SUM(CASE WHEN m.format = 'T20I' THEN pms.runs_scored ELSE 0 END) AS T20_Runs, 
               ROUND(CAST(SUM(pms.runs_scored) AS FLOAT) / NULLIF(COUNT(pms.stat_id), 0), 2) AS Overall_Avg 
        FROM Players p 
        JOIN Player_Match_Stats pms ON p.player_id = pms.player_id 
        JOIN Matches m ON pms.match_id = m.match_id 
        GROUP BY p.player_id, p.full_name 
        HAVING COUNT(DISTINCT m.format) >= 2;
    """,
    "Q12: Home vs Away Team Performance": """
        SELECT t.team_name AS Team, 
               SUM(CASE WHEN v.country = t.team_name AND m.match_winner_id = t.team_id THEN 1 ELSE 0 END) AS Home_Wins, 
               SUM(CASE WHEN v.country != t.team_name AND m.match_winner_id = t.team_id THEN 1 ELSE 0 END) AS Away_Wins 
        FROM Teams t 
        JOIN Matches m ON (t.team_id = m.team1_id OR t.team_id = m.team2_id) 
        JOIN Venues v ON m.venue_id = v.venue_id 
        GROUP BY t.team_id, t.team_name;
    """,
    "Q13: Consecutive Batting Partnerships >= 100": """
        SELECT p1.full_name AS Batter_1, p2.full_name AS Batter_2, 
               (pms1.runs_scored + pms2.runs_scored) AS Partnership_Runs, m.match_description AS Match 
        FROM Player_Match_Stats pms1 
        JOIN Player_Match_Stats pms2 ON pms1.match_id = pms2.match_id AND pms2.batting_position = pms1.batting_position + 1 
        JOIN Players p1 ON pms1.player_id = p1.player_id 
        JOIN Players p2 ON pms2.player_id = p2.player_id 
        JOIN Matches m ON pms1.match_id = m.match_id 
        WHERE (pms1.runs_scored + pms2.runs_scored) >= 100;
    """,
    "Q14: Bowling Performance by Venue": """
        SELECT p.full_name AS Bowler, v.venue_name AS Venue, 
               ROUND(SUM(pms.runs_conceded) / NULLIF(SUM(pms.overs_bowled), 0), 2) AS Economy, 
               SUM(pms.wickets_taken) AS Wickets, COUNT(m.match_id) AS Matches 
        FROM Players p 
        JOIN Player_Match_Stats pms ON p.player_id = pms.player_id 
        JOIN Matches m ON pms.match_id = m.match_id 
        JOIN Venues v ON m.venue_id = v.venue_id 
        WHERE pms.overs_bowled >= 4 
        GROUP BY p.player_id, p.full_name, v.venue_id, v.venue_name 
        HAVING COUNT(m.match_id) >= 3;
    """,
    "Q15: Performance in Close Matches": """
        SELECT p.full_name AS Player, ROUND(AVG(pms.runs_scored), 2) AS Avg_Runs, 
               COUNT(m.match_id) AS Close_Matches_Played, 
               SUM(CASE WHEN m.match_winner_id = p.team_id THEN 1 ELSE 0 END) AS Close_Matches_Won 
        FROM Players p 
        JOIN Player_Match_Stats pms ON p.player_id = pms.player_id 
        JOIN Matches m ON pms.match_id = m.match_id 
        WHERE (m.victory_type = 'runs' AND m.victory_margin < 50) OR (m.victory_type = 'wickets' AND m.victory_margin < 5) 
        GROUP BY p.player_id, p.full_name;
    """,
    "Q16: Batting Performance Over Years (Since 2020)": """
        SELECT p.full_name AS Player, strftime('%Y', m.match_date) AS Year, 
               ROUND(AVG(pms.runs_scored), 2) AS Avg_Runs, 
               ROUND((SUM(pms.runs_scored) * 100.0) / NULLIF(SUM(pms.balls_faced), 0), 2) AS Strike_Rate 
        FROM Players p 
        JOIN Player_Match_Stats pms ON p.player_id = pms.player_id 
        JOIN Matches m ON pms.match_id = m.match_id 
        WHERE m.match_date >= '2020-01-01' 
        GROUP BY p.player_id, p.full_name, Year 
        HAVING COUNT(m.match_id) >= 5;
    """,

    # ================= ADVANCED LEVEL =================
    "Q17: Toss Advantage Impact": """
        SELECT toss_decision AS Decision, COUNT(match_id) AS Total_Matches, 
               SUM(CASE WHEN toss_winner_id = match_winner_id THEN 1 ELSE 0 END) AS Matches_Won, 
               ROUND((SUM(CASE WHEN toss_winner_id = match_winner_id THEN 1 ELSE 0 END) * 100.0) / COUNT(match_id), 2) AS Win_Percentage 
        FROM Matches GROUP BY toss_decision;
    """,
    "Q18: Most Economical Limited-Overs Bowlers": """
        SELECT p.full_name AS Bowler, ROUND(SUM(pms.runs_conceded) / NULLIF(SUM(pms.overs_bowled), 0), 2) AS Economy, 
               SUM(pms.wickets_taken) AS Wickets 
        FROM Players p 
        JOIN Player_Match_Stats pms ON p.player_id = pms.player_id 
        JOIN Matches m ON pms.match_id = m.match_id 
        WHERE m.format IN ('ODI', 'T20I') 
        GROUP BY p.player_id, p.full_name 
        HAVING COUNT(m.match_id) >= 10 AND AVG(pms.overs_bowled) >= 2 
        ORDER BY Economy ASC;
    """,
    "Q19: Batsman Consistency (Std Deviation)": """
        SELECT p.full_name AS Batsman, ROUND(AVG(pms.runs_scored), 2) AS Avg_Runs, 
               ROUND(SQRT(AVG(pms.runs_scored * pms.runs_scored) - (AVG(pms.runs_scored) * AVG(pms.runs_scored))), 2) AS Run_Std_Dev 
        FROM Players p 
        JOIN Player_Match_Stats pms ON p.player_id = pms.player_id 
        JOIN Matches m ON pms.match_id = m.match_id 
        WHERE pms.balls_faced >= 10 AND m.match_date >= '2022-01-01' 
        GROUP BY p.player_id, p.full_name 
        ORDER BY Run_Std_Dev ASC;
    """,
    "Q20: Match Counts and Averages by Format": """
        SELECT p.full_name AS Player, 
               SUM(CASE WHEN m.format = 'Test' THEN 1 ELSE 0 END) AS Test_Matches, 
               ROUND(AVG(CASE WHEN m.format = 'Test' THEN pms.runs_scored ELSE NULL END), 2) AS Test_Avg, 
               SUM(CASE WHEN m.format = 'ODI' THEN 1 ELSE 0 END) AS ODI_Matches, 
               ROUND(AVG(CASE WHEN m.format = 'ODI' THEN pms.runs_scored ELSE NULL END), 2) AS ODI_Avg, 
               SUM(CASE WHEN m.format = 'T20I' THEN 1 ELSE 0 END) AS T20_Matches, 
               ROUND(AVG(CASE WHEN m.format = 'T20I' THEN pms.runs_scored ELSE NULL END), 2) AS T20_Avg 
        FROM Players p 
        JOIN Player_Match_Stats pms ON p.player_id = pms.player_id 
        JOIN Matches m ON pms.match_id = m.match_id 
        GROUP BY p.player_id, p.full_name 
        HAVING COUNT(m.match_id) >= 20;
    """,
    "Q21: Comprehensive Performance Ranking": """
        SELECT p.full_name AS Player, m.format AS Format, 
               ROUND(((SUM(pms.runs_scored) * 0.01) + (AVG(pms.runs_scored) * 0.5) + ((SUM(pms.runs_scored)*100.0/NULLIF(SUM(pms.balls_faced),0)) * 0.3)), 2) AS Batting_Points, 
               ROUND(((SUM(pms.wickets_taken) * 2) + ((50 - (SUM(pms.runs_conceded)/NULLIF(SUM(pms.wickets_taken),0))) * 0.5) + ((6 - (SUM(pms.runs_conceded)/NULLIF(SUM(pms.overs_bowled),0))) * 2)), 2) AS Bowling_Points, 
               ((SUM(pms.catches) * 3) + (SUM(pms.stumpings) * 5)) AS Fielding_Points 
        FROM Players p 
        JOIN Player_Match_Stats pms ON p.player_id = pms.player_id 
        JOIN Matches m ON pms.match_id = m.match_id 
        GROUP BY p.player_id, p.full_name, m.format;
    """,
    "Q22: Head-to-Head Prediction Analysis": """
        WITH H2H AS (
            SELECT m.team1_id, m.team2_id, COUNT(m.match_id) AS Total_Matches, 
                   SUM(CASE WHEN m.match_winner_id = m.team1_id THEN 1 ELSE 0 END) AS Team1_Wins, 
                   SUM(CASE WHEN m.match_winner_id = m.team2_id THEN 1 ELSE 0 END) AS Team2_Wins 
            FROM Matches m 
            WHERE m.match_date >= date('now', '-3 years') 
            GROUP BY m.team1_id, m.team2_id 
            HAVING COUNT(m.match_id) >= 5
        )
        SELECT t1.team_name AS Team_1, t2.team_name AS Team_2, h.Total_Matches, 
               h.Team1_Wins, h.Team2_Wins, ROUND((h.Team1_Wins * 100.0 / h.Total_Matches), 2) AS Team1_Win_Pct 
        FROM H2H h 
        JOIN Teams t1 ON h.team1_id = t1.team_id 
        JOIN Teams t2 ON h.team2_id = t2.team_id;
    """,
    "Q23: Recent Player Form & Momentum": """
        WITH RecentMatches AS (
            SELECT pms.player_id, pms.runs_scored, 
                   ROW_NUMBER() OVER (PARTITION BY pms.player_id ORDER BY m.match_date DESC) as match_rank 
            FROM Player_Match_Stats pms 
            JOIN Matches m ON pms.match_id = m.match_id
        )
        SELECT p.full_name AS Player, 
               ROUND(AVG(CASE WHEN match_rank <= 5 THEN runs_scored ELSE NULL END), 2) AS Avg_Last_5, 
               ROUND(AVG(CASE WHEN match_rank <= 10 THEN runs_scored ELSE NULL END), 2) AS Avg_Last_10, 
               SUM(CASE WHEN runs_scored >= 50 AND match_rank <= 10 THEN 1 ELSE 0 END) AS Fifties_Last_10,
               CASE WHEN AVG(CASE WHEN match_rank <= 5 THEN runs_scored ELSE NULL END) > 50 THEN '🔥 Excellent Form' 
                    WHEN AVG(CASE WHEN match_rank <= 5 THEN runs_scored ELSE NULL END) > 30 THEN '👍 Good Form' 
                    ELSE '⚠️ Average/Poor Form' END AS Current_Form 
        FROM RecentMatches rm 
        JOIN Players p ON rm.player_id = p.player_id 
        WHERE match_rank <= 10 
        GROUP BY p.player_id, p.full_name;
    """,
    "Q24: Successful Batting Partnerships": """
        SELECT p1.full_name AS Batter_1, p2.full_name AS Batter_2, COUNT(*) AS Total_Partnerships, 
               ROUND(AVG(pms1.runs_scored + pms2.runs_scored), 2) AS Avg_Partnership, 
               SUM(CASE WHEN (pms1.runs_scored + pms2.runs_scored) > 50 THEN 1 ELSE 0 END) AS Fifties_Plus, 
               MAX(pms1.runs_scored + pms2.runs_scored) AS Highest_Partnership 
        FROM Player_Match_Stats pms1 
        JOIN Player_Match_Stats pms2 ON pms1.match_id = pms2.match_id AND pms2.batting_position = pms1.batting_position + 1 
        JOIN Players p1 ON pms1.player_id = p1.player_id 
        JOIN Players p2 ON pms2.player_id = p2.player_id 
        GROUP BY p1.player_id, p2.player_id 
        HAVING COUNT(*) >= 5 
        ORDER BY Avg_Partnership DESC;
    """,
    "Q25: Time-Series Player Performance Evolution": """
        SELECT p.full_name AS Player, 
               strftime('%Y', m.match_date) || '-Q' || ((CAST(strftime('%m', m.match_date) AS INTEGER) + 2) / 3) AS Quarter, 
               ROUND(AVG(pms.runs_scored), 2) AS Avg_Runs 
        FROM Players p 
        JOIN Player_Match_Stats pms ON p.player_id = pms.player_id 
        JOIN Matches m ON pms.match_id = m.match_id 
        GROUP BY p.player_id, p.full_name, Quarter 
        HAVING COUNT(m.match_id) >= 3 
        ORDER BY p.full_name, Quarter;
    """
}

st.markdown("---")

# Clean, professional business dropdown (Zero raw SQL visible to users)
selected_category = st.selectbox(
    "🎯 Select Business Insight Report:", 
    list(queries.keys()),
    help="Choose an intelligence report to instantly generate visual charts, graphs, and structured metrics."
)

sql_syntax = queries[selected_category]

# Execute query and render interactive visualizations
with st.spinner("Crunching analytics data..."):
    try:
        df = execute_query(sql_syntax)
        
        if df.empty:
            st.warning("⚠️ No records found for this specific insight yet. Try syncing more match files.")
        else:
            st.success(f"Successfully generated: **{selected_category}**")
            
            # --- TOP METRIC CARDS ---
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", len(df))
            with col2:
                numeric_cols_count = len(df.select_dtypes(include=['number']).columns)
                st.metric("Metrics Analyzed", numeric_cols_count)
            with col3:
                st.metric("Data Status", "Live & Synced")
            
            st.markdown("---")
            st.markdown("### 📈 Interactive Visual Plots & Graphs")
            
            # --- INTELLIGENT AUTO-CHARTING ---
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            text_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
            
            if len(numeric_cols) > 0 and len(text_cols) > 0:
                x_col = text_cols[0]
                y_col = numeric_cols[0]
                
                # Render interactive bar chart for comparison reports
                st.bar_chart(data=df.set_index(x_col)[y_col], use_container_width=True)
            elif len(numeric_cols) >= 2:
                # Render line chart for trend analysis
                st.line_chart(data=df[numeric_cols[:2]], use_container_width=True)
            else:
                st.info("ℹ️ Tabular report view rendered below.")
            
            st.markdown("---")
            st.markdown("### 📋 Structured Data Report")
            st.dataframe(df, use_container_width=True)
            
    except Exception as e:
        st.error(f"❌ Analytics Engine Error: {e}")
