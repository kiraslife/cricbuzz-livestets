import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="CRUD Operations", page_icon="🛠️")

# Helper function to connect to the database
def get_connection():
    db_path = os.path.join('database', 'cricbuzz.db')
    # Adjust path if Streamlit runs from inside the pages folder
    if not os.path.exists(db_path):
        db_path = os.path.join('..', 'database', 'cricbuzz.db')
    return sqlite3.connect(db_path)

st.title("🛠️ Player CRUD Operations")
st.markdown("Use this dashboard to securely manage player records in the database.")

# Create tabs for the 4 operations
tab1, tab2, tab3, tab4 = st.tabs(["Create", "Read", "Update", "Delete"])

# 1. CREATE (Insert)
with tab1:
    st.subheader("Add a New Player")
    with st.form("create_player_form"):
        name = st.text_input("Full Name")
        role = st.selectbox("Playing Role", ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"])
        batting_style = st.selectbox("Batting Style", ["Right-hand bat", "Left-hand bat"])
        submit_create = st.form_submit_button("Add Player")

        if submit_create:
            if name.strip():
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO Players (full_name, playing_role, batting_style) 
                        VALUES (?, ?, ?)
                    ''', (name, role, batting_style))
                    conn.commit()
                    st.success(f"✅ Player '{name}' added successfully!")
                except Exception as e:
                    st.error(f"Database Error: {e}")
                finally:
                    conn.close()
            else:
                st.warning("⚠️ Please enter a player name.")

# 2. READ (Select)
with tab2:
    st.subheader("View All Players")
    if st.button("Refresh Player Database"):
        try:
            conn = get_connection()
            df = pd.read_sql_query("SELECT * FROM Players", conn)
            conn.close()
            if df.empty:
                st.info("No players found in the database. Add some first!")
            else:
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error reading data: {e}")

# 3. UPDATE
with tab3:
    st.subheader("Update a Player's Role")
    with st.form("update_player_form"):
        player_id = st.number_input("Enter Player ID to Update", min_value=1, step=1)
        new_role = st.selectbox("Select New Playing Role", ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"])
        submit_update = st.form_submit_button("Update Record")

        if submit_update:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE Players SET playing_role = ? WHERE player_id = ?", (new_role, player_id))
                conn.commit()
                if cursor.rowcount > 0:
                    st.success(f"✅ Player ID {player_id} updated successfully!")
                else:
                    st.error("❌ Player ID not found.")
            except Exception as e:
                 st.error(f"Database Error: {e}")
            finally:
                conn.close()

# 4. DELETE
with tab4:
    st.subheader("Delete a Player")
    with st.form("delete_player_form"):
        del_player_id = st.number_input("Enter Player ID to Delete", min_value=1, step=1)
        submit_delete = st.form_submit_button("Delete Record")

        if submit_delete:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Players WHERE player_id = ?", (del_player_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    st.success(f"✅ Player ID {del_player_id} deleted successfully!")
                else:
                    st.error("❌ Player ID not found.")
            except Exception as e:
                 st.error(f"Database Error: {e}")
            finally:
                conn.close()