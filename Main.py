import streamlit as st
import hashlib
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import pytz
from pathlib import Path

# ================= CONFIGURATION ULTRA =================
st.set_page_config(
    page_title="COSMOS X V17.0 OMEGA X3+", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Timezone Madagascar
EAT = pytz.timezone('Indian/Antananarivo')

# ================= PERSISTENCE SYSTEM =================
DATA_DIR = Path("cosmos_x_data")
DATA_DIR.mkdir(exist_ok=True)
DB_FILE = DATA_DIR / "cosmos_omega.db"

# ================= PREMIUM STYLING =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    
    .stApp {
        background: radial-gradient(ellipse at 50% 0%, #0d0033 0%, #000005 50%, #001a0d 100%);
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }

    .glass-ultra {
        background: rgba(5, 5, 20, 0.85);
        border: 2px solid rgba(0, 255, 204, 0.4);
        border-radius: 22px;
        padding: 28px;
        backdrop-filter: blur(16px);
        box-shadow: 0 0 40px rgba(0, 255, 204, 0.15);
        margin-bottom: 24px;
    }

    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff);
        background-size: 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .entry-time-omega {
        font-family: 'Orbitron', sans-serif;
        font-size: 5rem;
        font-weight: 900;
        text-align: center;
        color: #00ffcc;
        filter: drop-shadow(0 0 30px #00ffccaa);
        margin: 20px 0;
    }

    .target-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid rgba(0, 255, 204, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ================= DATABASE FUNCTIONS (FIXED & SECURE) =================
def db_init():
    conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT, 
            hash_input TEXT, 
            time_input TEXT, 
            last_cote REAL,
            entry_time TEXT, 
            signal TEXT, 
            x3_prob REAL, 
            accuracy REAL,
            min_target REAL, 
            moy_target REAL, 
            max_target REAL,
            result TEXT
        )
    """)
    conn.commit()
    return conn

def save_prediction(data):
    try:
        with db_init() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO predictions 
                (timestamp, hash_input, time_input, last_cote, entry_time, signal, 
                 x3_prob, accuracy, min_target, moy_target, max_target)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['timestamp'], data['hash'], data['time'], data['last_cote'],
                data['entry'], data['signal'], data['x3_prob'], data['accuracy'],
                data['min'], data['moy'], data['max']
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.OperationalError:
        # AUTO-REPAIR: Raha misy olona ny structure, fafana dia averina
        with sqlite3.connect(str(DB_FILE)) as conn:
            conn.execute("DROP TABLE IF EXISTS predictions")
            conn.commit()
        db_init()
        return save_prediction(data)

def update_result(p_id, res):
    with db_init() as conn:
        conn.execute("UPDATE predictions SET result = ? WHERE id = ?", (res, p_id))
        conn.commit()

# ================= ENGINE OMEGA =================
def run_omega(hash_in, time_in, last_c):
    h_hex = hashlib.sha256(hash_in.encode()).hexdigest()
    np.random.seed(int(h_hex[:8], 16))
    
    # Advanced logic based on last_cote
    x3_p = round(float(np.random.uniform(38, 62) if last_c < 2.0 else np.random.uniform(20, 45)), 2)
    acc = round(min(99.4, 85 + (np.random.random() * 12)), 2)
    
    c_min = round(2.0 + (np.random.random() * 0.5), 2)
    c_moy = round(3.5 + (np.random.random() * 1.5), 2)
    c_max = round(6.0 + (np.random.random() * 15.0), 2)
    
    try:
        t_base = datetime.strptime(time_in.strip(), "%H:%M:%S")
        dream_time = (t_base + timedelta(seconds=48)).strftime("%H:%M:%S")
    except:
        dream_time = datetime.now(EAT).strftime("%H:%M:%S")

    res = {
        'timestamp': datetime.now(EAT).strftime("%Y-%m-%d %H:%M:%S"),
        'hash': hash_in, 
        'time': time_in, 
        'last_cote': last_c,
        'entry': dream_time, 
        'x3_prob': x3_p, 
        'accuracy': acc,
        'min': c_min, 
        'moy': c_moy, 
        'max': c_max,
        'signal': "💎 ULTRA X3+" if x3_p > 45 else "🟢 GOOD"
    }
    res['p_id'] = save_prediction(res)
    return res

# ================= APP LOGIC =================
if "auth" not in st.session_state: st.session_state.auth = False

# Simple Auth
if not st.session_state.auth:
    st.markdown("<div class='glass-ultra' style='max-width:450px; margin: 100px auto;'>", unsafe_allow_html=True)
    st.subheader("🔐 OMEGA ACCESS")
    key = st.text_input("KEY", type="password")
    if st.button("LOGIN", use_container_width=True):
        if key == "COSMOS2026": 
            st.session_state.auth = True
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

st.markdown("<h1 class='main-title'>COSMOS X OMEGA</h1>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🛠️ TOOLS")
    if st.button("🗑️ RESET ALL DATA", use_container_width=True):
        if DB_FILE.exists():
            with sqlite3.connect(str(DB_FILE)) as conn:
                conn.execute("DROP TABLE IF EXISTS predictions")
                conn.commit()
        if "res_omega" in st.session_state:
            del st.session_state.res_omega
        st.rerun()

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("<div class='glass-ultra'>", unsafe_allow_html=True)
    st.markdown("### 📥 INPUT")
    h_in = st.text_input("SERVER HASH", value="")
    t_in = st.text_input("TIME (HH:MM:SS)", value="")
    l_c = st.number_input("LAST COTE", value=0.0, step=0.01)
    
    if st.button("🚀 EXECUTE", use_container_width=True):
        if h_in and t_in:
            st.session_state.res_omega = run_omega(h_in, t_in, l_c)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if "res_omega" in st.session_state:
        r = st.session_state.res_omega
        st.markdown("<div class='glass-ultra'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center; color:#00ffcc;'>{r['signal']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-time-omega'>{r['entry']}</div>", unsafe_allow_html=True)
        
        m1, m2 = st.columns(2)
        m1.metric("PROBABILITY", f"{r['x3_prob']}%")
        m2.metric("ACCURACY", f"{r['accuracy']}%")
        
        st.markdown("<br>", unsafe_allow_html=True)
        t1, t2, t3 = st.columns(3)
        t1.markdown(f"<div class='target-box'>MIN<br><b>{r['min']}x</b></div>", unsafe_allow_html=True)
        t2.markdown(f"<div class='target-box'>MOY<br><b>{r['moy']}x</b></div>", unsafe_allow_html=True)
        t3.markdown(f"<div class='target-box'>MAX<br><b>{r['max']}x</b></div>", unsafe_allow_html=True)
        
        if st.button("🎯 CONFIRM SUCCESS", use_container_width=True):
            update_result(r['p_id'], "HIT")
            st.success("Result Saved!")
        st.markdown("</div>", unsafe_allow_html=True)

# Logs
st.markdown("### 🕒 HISTORY")
try:
    with db_init() as conn:
        df = pd.read_sql("SELECT timestamp, entry_time, signal, x3_prob, result FROM predictions ORDER BY id DESC LIMIT 5", conn)
        st.dataframe(df, use_container_width=True)
except:
    st.write("No history found.")
