import streamlit as st
import numpy as np
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import pytz
import json
import os
from pathlib import Path

# ===================== PERSISTENCE SYSTEM =====================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data_storage"
DATA_DIR.mkdir(exist_ok=True, parents=True)

HISTORY_FILE = DATA_DIR / "history.json"

def save_history(history):
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except:
        pass

def load_history():
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
    except:
        return []
    return []

# ===================== CONFIG & STYLE =====================
st.set_page_config(page_title="JETX X3+ LASER V16.1", layout="wide")
EAT = pytz.timezone("Indian/Antananarivo")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;700&display=swap');
    .stApp { background: #000008; color: #e0fbfc; font-family: 'Rajdhani', sans-serif; }
    .main-title {
        font-family: 'Orbitron'; font-size: 3rem; text-align: center;
        background: linear-gradient(90deg, #ff0066, #00ffcc);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .glass-card {
        background: rgba(20, 0, 40, 0.8);
        border: 1px solid #ff0066;
        border-radius: 15px; padding: 20px;
        margin-bottom: 20px;
    }
    .entry-time {
        font-family: 'Orbitron'; font-size: 4rem; color: #ff0066;
        text-align: center; text-shadow: 0 0 30px #ff0066;
    }
</style>
""", unsafe_allow_html=True)

# ===================== AUTHENTICATION =====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<div class='main-title'>X3+ LASER LOGIN</div>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        pw = st.text_input("PASSWORD", type="password")
        if st.button("ACTIVATE SYSTEM", use_container_width=True):
            if pw == "JET2026":
                st.session_state.authenticated = True
                st.rerun()
    st.stop()

# ===================== DATA INITIALIZATION =====================
if "history" not in st.session_state:
    st.session_state.history = load_history()

# RESET BUTTON IN SIDEBAR
with st.sidebar:
    st.header("⚙️ SETTINGS")
    if st.button("🗑️ RESET ALL DATA (Fix Error)"):
        st.session_state.history = []
        if HISTORY_FILE.exists():
            os.remove(HISTORY_FILE)
        st.session_state.last_res = None
        st.success("Data reset complete!")
        st.rerun()

if "last_res" not in st.session_state:
    st.session_state.last_res = None

# ===================== ENGINE =====================
def run_x3_engine(h_in, t_in):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:16], 16)
    np.random.seed(h_num & 0xFFFFFFFF)
    
    # Simulation logic
    sims = np.random.lognormal(np.log(2.2), 0.2, 100_000)
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    
    # Calculation of Cotes
    c_min = round(float(np.percentile(sims, 40)), 2)
    c_avg = round(float(np.mean(sims)), 2)
    c_max = round(float(np.max(sims[:1000]) * 0.8), 2)

    try:
        base_t = datetime.strptime(t_in.strip(), "%H:%M:%S")
        shift = 45 + (h_num % 10)
        entry_t = (base_t + timedelta(seconds=shift)).strftime("%H:%M:%S")
    except:
        entry_t = datetime.now(EAT).strftime("%H:%M:%S")

    res = {
        "id": h_hex[:8],
        "entry": entry_t,
        "prob": prob_x3,
        "min": max(3.0, c_min),
        "moyen": max(3.15, c_avg),
        "max": c_max,
        "signal": "💎 ULTRA X3+" if prob_x3 > 45 else "🔥 STRONG X3+",
        "status": "PENDING"
    }
    
    st.session_state.history.append(res)
    save_history(st.session_state.history)
    return res

# ===================== UI =====================
st.markdown("<div class='main-title'>JETX X3+ LASER</div>", unsafe_allow_html=True)

col_in, col_out = st.columns([1, 2], gap="large")

with col_in:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📥 INPUT")
    h_val = st.text_input("SERVER HASH")
    t_val = st.text_input("ROUND TIME")
    
    if st.button("🚀 ANALYSE", use_container_width=True):
        if h_val and t_val:
            st.session_state.last_res = run_x3_engine(h_val, t_val)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col_out:
    if st.session_state.last_res:
        r = st.session_state.last_res
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center;'>{r['signal']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-time'>{r['entry']}</div>", unsafe_allow_html=True)
        
        # Metrics with Safety Check (.get) to prevent KeyErrors
        m1, m2, m3 = st.columns(3)
        m1.metric("COTE MIN", f"{r.get('min', 3.0)}x")
        m2.metric("COTE MOYEN", f"{r.get('moyen', 3.15)}x")
        m3.metric("COTE MAX", f"{r.get('max', 5.0)}x")
        
        st.metric("PROBABILITÉ X3+", f"{r.get('prob', 0)}%")
        
        if st.button("🎯 CONFIRM WIN", use_container_width=True):
            for h in st.session_state.history:
                if h['id'] == r['id']: h['status'] = 'WIN ✅'
            save_history(st.session_state.history)
            st.success("Saved!")
        st.markdown("</div>", unsafe_allow_html=True)

# History table
st.write("### 🕒 RECENT LOGS")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history).iloc[::-1]
    # Ensure columns exist before displaying
    display_cols = ['entry', 'prob', 'min', 'moyen', 'max', 'status']
    available_cols = [c for c in display_cols if c in df.columns]
    st.dataframe(df[available_cols], use_container_width=True)
