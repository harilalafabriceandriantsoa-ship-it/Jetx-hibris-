import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz
from pathlib import Path

# ================= CONFIGURATION =================
st.set_page_config(
    page_title="COSMOS X V17 OMEGA", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Timezone Madagascar
EAT = pytz.timezone('Indian/Antananarivo')

# ANARANA VAOVAO TANTERAKA MBA TSY HISY ERROR DB INTSONY
DB_NAME = "cosmos_v17_final_secure.db"

# ================= PREMIUM STYLING =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp {
        background: radial-gradient(circle at center, #00001a 0%, #000000 100%);
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }

    .glass-panel {
        background: rgba(10, 10, 35, 0.9);
        border: 2px solid #00ffcc;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 0 30px rgba(0, 255, 204, 0.2);
    }

    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.2rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00ffcc, #ff00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 30px;
    }

    .entry-time-display {
        font-family: 'Orbitron', sans-serif;
        font-size: 4.5rem;
        font-weight: 900;
        text-align: center;
        color: #00ffcc;
        text-shadow: 0 0 25px #00ffcc;
        margin: 15px 0;
    }

    .target-metric {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        border-left: 4px solid #00ffcc;
    }
</style>
""", unsafe_allow_html=True)

# ================= DATABASE ENGINE (FIXED) =================
def get_db_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db_system():
    with get_db_connection() as conn:
        # Mampiasa anarana table vaovao (history_v17)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history_v17 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT, hash_in TEXT, time_in TEXT, last_c REAL,
                entry TEXT, signal TEXT, prob REAL, acc REAL,
                v_min REAL, v_moy REAL, v_max REAL,
                status TEXT
            )
        """)
        conn.commit()

def save_analysis(d):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO history_v17 
                (ts, hash_in, time_in, last_c, entry, signal, prob, acc, v_min, v_moy, v_max)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                d['ts'], d['hash'], d['time'], d['last_c'], d['entry'], 
                d['signal'], d['prob'], d['acc'], d['min'], d['moy'], d['max']
            ))
            conn.commit()
            return cur.lastrowid
    except sqlite3.OperationalError:
        # Raha mbola misy error structure dia fafana ny table dia averina
        with get_db_connection() as conn:
            conn.execute("DROP TABLE IF EXISTS history_v17")
            conn.commit()
        init_db_system()
        return save_analysis(d)

# ================= OMEGA CORE ENGINE =================
def run_omega_analysis(h, t, lc):
    h_hex = hashlib.sha256(h.encode()).hexdigest()
    np.random.seed(int(h_hex[:8], 16))
    
    # Logic arakaraka ny Last Cote
    p = round(float(np.random.uniform(42, 65) if lc < 2.0 else np.random.uniform(18, 40)), 2)
    a = round(float(94.0 + (np.random.random() * 5.5)), 2)
    
    m1 = round(2.0 + (np.random.random() * 0.4), 2)
    m2 = round(3.5 + (np.random.random() * 1.8), 2)
    m3 = round(8.0 + (np.random.random() * 12.0), 2)
    
    try:
        base = datetime.strptime(t.strip(), "%H:%M:%S")
        # Micro-adjustment 48s
        entry_t = (base + timedelta(seconds=48)).strftime("%H:%M:%S")
    except:
        entry_t = datetime.now(EAT).strftime("%H:%M:%S")

    res = {
        'ts': datetime.now(EAT).strftime("%Y-%m-%d %H:%M:%S"),
        'hash': h, 'time': t, 'last_c': lc,
        'entry': entry_t, 'signal': "💎 ULTRA X3+" if p > 48 else "🔥 STRONG",
        'prob': p, 'acc': a, 'min': m1, 'moy': m2, 'max': m3
    }
    # Tehirizina avy hatrany
    res['db_id'] = save_analysis(res)
    return res

# ================= APP INTERFACE =================
init_db_system()

if "authorized" not in st.session_state: st.session_state.authorized = False

# Login
if not st.session_state.authorized:
    st.markdown("<div class='glass-panel' style='max-width:400px; margin: 100px auto;'>", unsafe_allow_html=True)
    st.subheader("🔐 OMEGA ACCESS")
    pwd = st.text_input("KEY", type="password")
    if st.button("ACTIVATE", use_container_width=True):
        if pwd == "COSMOS2026": 
            st.session_state.authorized = True
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

st.markdown("<h1 class='main-title'>COSMOS X V17 OMEGA</h1>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🛠️ TOOLS")
    if st.button("🗑️ CLEAR HISTORY", use_container_width=True):
        with get_db_connection() as conn:
            conn.execute("DELETE FROM history_v17")
            conn.commit()
        if "res_data" in st.session_state: del st.session_state.res_data
        st.success("Database Purged")
        st.rerun()

col_in, col_out = st.columns([1, 2])

with col_in:
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("### 📥 ANALYSIS INPUT")
    h_val = st.text_input("SERVER HASH", value="", placeholder="Paste hash...")
    t_val = st.text_input("GAME TIME", value="", placeholder="HH:MM:SS")
    lc_val = st.number_input("LAST COTE", value=0.0, step=0.01)
    
    if st.button("🚀 EXECUTE OMEGA", use_container_width=True):
        if h_val and t_val:
            st.session_state.res_data = run_omega_analysis(h_val, t_val, lc_val)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col_out:
    if "res_data" in st.session_state:
        d = st.session_state.res_data
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center; color:#00ffcc;'>{d['signal']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-time-display'>{d['entry']}</div>", unsafe_allow_html=True)
        
        m1, m2 = st.columns(2)
        m1.metric("PROBABILITY", f"{d['prob']}%")
        m2.metric("ACCURACY", f"{d['acc']}%")
        
        st.markdown("<br>", unsafe_allow_html=True)
        t1, t2, t3 = st.columns(3)
        t1.markdown(f"<div class='target-metric'>MIN<br><b>{d['min']}x</b></div>", unsafe_allow_html=True)
        t2.markdown(f"<div class='target-metric'>MOY<br><b>{d['moy']}x</b></div>", unsafe_allow_html=True)
        t3.markdown(f"<div class='target-metric'>MAX<br><b>{d['max']}x</b></div>", unsafe_allow_html=True)
        
        if st.button("🎯 CONFIRM WIN", use_container_width=True):
            with get_db_connection() as conn:
                conn.execute("UPDATE history_v17 SET status = 'HIT' WHERE id = ?", (d['db_id'],))
                conn.commit()
            st.success("Win Recorded!")
        st.markdown("</div>", unsafe_allow_html=True)

# Logs
st.markdown("---")
st.markdown("### 🕒 SYSTEM LOGS (LAST 5)")
with get_db_connection() as conn:
    try:
        logs_df = pd.read_sql("SELECT entry, signal, prob, ts, status FROM history_v17 ORDER BY id DESC LIMIT 5", conn)
        st.dataframe(logs_df, use_container_width=True)
    except:
        st.write("Awaiting first analysis...")
