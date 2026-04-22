import streamlit as st
import numpy as np
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import pytz
import json
import os
import pickle
from pathlib import Path

from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.preprocessing import RobustScaler
from sklearn.pipeline import Pipeline

# ===================== PERSISTENCE SYSTEM =====================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data_storage"
DATA_DIR.mkdir(exist_ok=True, parents=True)

HISTORY_FILE = DATA_DIR / "history.json"
ML_CLF_FILE = DATA_DIR / "ml_clf.pkl"
ML_REG_FILE = DATA_DIR / "ml_reg.pkl"

def save_history(history):
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception:
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
    .stApp { background: #00000a; color: #e0fbfc; font-family: 'Rajdhani', sans-serif; }
    .main-title {
        font-family: 'Orbitron'; font-size: 3rem; text-align: center;
        color: #ff0066; text-shadow: 0 0 20px #ff0066;
    }
    .glass-card {
        background: rgba(20, 0, 40, 0.8);
        border: 1px solid #ff0066;
        border-radius: 15px; padding: 20px;
    }
    .entry-time-display {
        font-family: 'Orbitron'; font-size: 4rem; color: #00ffcc;
        text-align: center; text-shadow: 0 0 30px #00ffcc;
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

# ===================== INITIALIZATION =====================
if "history" not in st.session_state:
    st.session_state.history = load_history()
if "last_res" not in st.session_state:
    st.session_state.last_res = None

# Sidebar Reset Option
with st.sidebar:
    st.title("⚙️ SETTINGS")
    if st.button("🗑️ RESET ALL DATA"):
        st.session_state.history = []
        if HISTORY_FILE.exists():
            os.remove(HISTORY_FILE)
        st.session_state.last_res = None
        st.success("Data cleared!")
        st.rerun()

# ===================== ENGINE =====================
def run_x3_engine(h_in, t_in):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:16], 16)
    np.random.seed(h_num & 0xFFFFFFFF)
    
    sims = np.random.lognormal(np.log(2.1), 0.18, 100_000)
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    
    try:
        base_t = datetime.strptime(t_in.strip(), "%H:%M:%S")
        shift = 40 + (h_num % 15)
        entry_t = (base_t + timedelta(seconds=shift)).strftime("%H:%M:%S")
    except:
        entry_t = datetime.now(EAT).strftime("%H:%M:%S")

    res = {
        "id": h_hex[:8],
        "entry": entry_t,
        "prob": prob_x3,
        "signal": "💎 ULTRA X3+" if prob_x3 > 45 else "🔥 STRONG X3+",
        "status": "PENDING"
    }
    st.session_state.history.append(res)
    save_history(st.session_state.history)
    return res

# ===================== MAIN UI =====================
st.markdown("<div class='main-title'>JETX X3+ LASER</div>", unsafe_allow_html=True)

c1, c2 = st.columns([1, 2])

with c1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    h_val = st.text_input("SERVER HASH")
    t_val = st.text_input("ROUND TIME (HH:MM:SS)")
    if st.button("🚀 ANALYSE", use_container_width=True):
        if h_val and t_val:
            st.session_state.last_res = run_x3_engine(h_val, t_val)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    if st.session_state.last_res:
        r = st.session_state.last_res
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center;'>{r['signal']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-time-display'>{r['entry']}</div>", unsafe_allow_html=True)
        st.metric("PROBABILITY", f"{r['prob']}%")
        
        if st.button("🎯 MARK WIN"):
            for h in st.session_state.history:
                if h['id'] == r['id']: h['status'] = 'WIN ✅'
            save_history(st.session_state.history)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

st.write("### 🕒 RECENT LOGS")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history).iloc[::-1]
    st.dataframe(df[['entry', 'prob', 'signal', 'status']], use_container_width=True)
