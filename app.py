import streamlit as st
import os
import sqlite3

# Page Configuration with Sports Theme
st.set_page_config(
    page_title="Cricbuzz LiveStats Pro",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Elite Sports Dashboard UI & Interactivity
st.markdown("""
<style>
    /* Main Background & Font */
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Header Banner Styling */
    .hero-container {
        background: linear-gradient(135deg, #1f4068 0%, #162447 50%, #1a1a2e 100%);
        padding: 40px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 30px;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: #a0aec0;
        font-weight: 400;
    }
    
    /* Interactive Cards */
    .stat-card {
        background: #1a202c;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #2d3748;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4);
        border-color: #ff4b4b;
    }
    
    .card-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    
    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 8px;
    }
    
    .card-desc {
        font-size: 0.9rem;
        color: #a0aec0;
    }
</style>
""", unsafe_allow_html=True)

# Hero Header with Cricket Bat & Ball Logo/Emblem
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🏏⚾ Cricbuzz LiveStats Pro</div>
    <div class="hero-subtitle">Real-Time Cricket Intelligence, Advanced SQL Analytics & Professional Sports Management Suite</div>
</div>
""", unsafe_allow_html=True)

# Quick Database Metrics Calculation
db_path = os.path.join('database', 'cricbuzz.db')
total_players = 0
total_matches = 0
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Players")
        total_players = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Matches")
        total_matches = cursor.fetchone()[0]
        conn.close()
    except:
        pass

# Interactive Metrics Overview Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="⚡ System Status", value="Online", delta="Connected")
with col2:
    st.metric(label="👥 Tracked Athletes", value=total_players, delta="Database Active")
with col3:
    st.metric(label="🏆 Recorded Matches", value=total_matches, delta="Synced")
with col4:
    st.metric(label="📊 SQL Reports", value="25 Modules", delta="Ready")

st.markdown("---")

# Navigation Guide Cards Section
st.markdown("### 🚀 Explore Platform Modules")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    <div class="stat-card">
        <div class="card-icon">🔴</div>
        <div class="card-title">Live Matches</div>
        <div class="card-desc">Stream live scorecards and recent international telemetry instantly.</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="stat-card">
        <div class="card-icon">🏆</div>
        <div class="card-title">Top Player Stats</div>
        <div class="card-desc">Analyze elite run scorers and wicket-takers via visual charts.</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="stat-card">
        <div class="card-icon">🧮</div>
        <div class="card-title">SQL Analytics</div>
        <div class="card-desc">Run 25 advanced business intelligence queries with automated plots.</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="stat-card">
        <div class="card-icon">🛠️</div>
        <div class="card-title">CRUD Operations</div>
        <div class="card-desc">Securely manage, insert, update, and delete athlete records.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Footer Banner
st.markdown("""
<div style="text-align: center; color: #718096; padding: 20px; font-size: 0.85rem;">
    Cricbuzz LiveStats Intelligence Suite • Powered by Python, Streamlit & SQLite
</div>
""", unsafe_allow_html=True)