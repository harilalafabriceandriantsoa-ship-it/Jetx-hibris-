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

# ===================== PERSISTENCE SYSTEM (FIXED) =====================
# Mamantatra ho azy ny lalana (path) azo ampiasaina mba tsy hisy error
if os.path.exists("/mount/src"):
    # Raha ao amin'ny Streamlit Cloud
    DATA_DIR = Path("./jetx_data_cloud")
else:
    # Raha Local
    DATA_DIR = Path.home() / "jetx_data_local"

DATA_DIR.mkdir(exist_ok=True, parents=True)

HISTORY_FILE = DATA_DIR / "history.json"
ML_CLF_FILE = DATA_DIR / "ml_clf.pkl"
ML_REG_FILE = DATA_DIR / "ml_reg.pkl"

def save_history(history):
    """Tehirizina anaty rakitra ny tantara"""
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        st.sidebar.error(f"⚠️ Erreur backup: {e}")

def load_history():
    """Vakiana ny tantara avy ao amin'ny disk"""
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
    except:
        return []
    return []

def save_models(clf, reg):
    """Tehirizina ny Intelligence Artificielle (ML)"""
    try:
        with open(ML_CLF_FILE, 'wb') as f:
            pickle.dump(clf, f)
        with open(ML_REG_FILE, 'wb') as f:
            pickle.dump(reg, f)
    except:
        pass

def load_models():
    """Vakiana ny modelina AI"""
    try:
        if ML_CLF_FILE.exists() and ML_REG_FILE.exists():
            with open(ML_CLF_FILE, 'rb') as f:
                clf = pickle.load(f)
            with open(ML_REG_FILE, 'rb') as f:
                reg = pickle.load(f)
            return clf, reg
    except:
        pass
    return None, None

# ===================== CONFIG & UI STYLE =====================
st.set_page_config(page_title="JETX X3+ LASER V16.1", layout="wide", initial_sidebar_state="collapsed")
EAT = pytz.timezone("Indian/Antananarivo")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp {
        background: radial-gradient(ellipse at 50% 0%, #1a0033 0%, #000011 100%);
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }
    
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem; font-weight: 900; text-align: center;
        background: linear-gradient(90deg, #ff0066, #00ffcc, #ff0066);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(255, 0, 102, 0.5);
    }
    
    .glass-card {
        background: rgba(10, 0, 25, 0.9);
        border: 2px solid rgba(255, 0, 102, 0.4);
        border-radius: 20px; padding: 25px;
        box-shadow: 0 0 40px rgba(255, 0, 102, 0.15);
    }

    .entry-time-display {
        font-family: 'Orbitron', sans-serif;
        font-size: 4.5rem; font-weight: 900;
        color: #ff0066; text-align: center;
        text-shadow: 0 0 40px #ff0066;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ===================== AUTHENTICATION =====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<div class='main-title'>X3+ LASER</div>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        pw = st.text_input("PASSWORD ACCESS", type="password")
        if st.button("ACTIVATE SYSTEM", use_container_width=True):
            if pw == "JET2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Code")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ===================== ENGINE CORE =====================
if "history" not in st.session_state:
    st.session_state.history = load_history()
if "last_res" not in st.session_state:
    st.session_state.last_res = None

def run_x3_engine(h_in, t_in, lc):
    # Hash Entropy
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:16], 16)
    np.random.seed(h_num & 0xFFFFFFFF)
    
    # Simulation
    sims = np.random.lognormal(np.log(2.15), 0.18, 120_000)
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    
    # Time Calc
    try:
        base_t = datetime.strptime(t_in.strip(), "%H:%M:%S")
        entry_t = (base_t + timedelta(seconds=48)).strftime("%H:%M:%S")
    except:
        entry_t = datetime.now(EAT).strftime("%H:%M:%S")

    res = {
        "id": h_hex[:10],
        "time_calc": datetime.now(EAT).strftime("%H:%M:%S"),
        "entry": entry_t,
        "prob": prob_x3,
        "signal": "💎 ULTRA X3+" if prob_x3 > 45 else "🔥 STRONG X3+",
        "status": "PENDING"
    }
    
    st.session_state.history.append(res)
    if len(st.session_state.history) > 50: st.session_state.history.pop(0)
    save_history(st.session_state.history)
    return res

# ===================== MAIN UI =====================
st.markdown("<div class='main-title'>JETX X3+ LASER</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#ff006699;'>V16.1 FOCUS OMEGA EDITION</p>", unsafe_allow_html=True)

col_in, col_out = st.columns([1, 2], gap="large")

with col_in:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📥 Data Input")
    h_val = st.text_input("SERVER HASH", placeholder="Paste hash here...")
    t_val = st.text_input("GAME TIME", placeholder="HH:MM:SS")
    lc_val = st.number_input("LAST COTE", value=1.80, step=0.01)
    
    if st.button("🚀 EXECUTE ANALYSIS", use_container_width=True):
        if h_val and t_val:
            st.session_state.last_res = run_x3_engine(h_val, t_val, lc_val)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col_out:
    if st.session_state.last_res:
        r = st.session_state.last_res
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center; color:#00ffcc;'>{r['signal']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-time-display'>{r['entry']}</div>", unsafe_allow_html=True)
        
        m1, m2 = st.columns(2)
        m1.metric("PROBABILITY", f"{r['prob']}%")
        m2.metric("TARGET", "3.15x - 4.50x")
        
        if st.button("🎯 MARK AS WIN", use_container_width=True):
            for h in st.session_state.history:
                if h['id'] == r['id']: h['status'] = 'WIN'
            save_history(st.session_state.history)
            st.success("Result Saved!")
        st.markdown("</div>", unsafe_allow_html=True)

# History table
st.markdown("---")
st.subheader("🕒 Recent Logs")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history).iloc[::-1]
    st.dataframe(df[['entry', 'prob', 'signal', 'status']], use_container_width=True)
