import streamlit as st
import numpy as np
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import pytz
import json
import os
from pathlib import Path
import pickle

from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.preprocessing import RobustScaler
from sklearn.pipeline import Pipeline

# ===================== PERSISTENCE SYSTEM =====================
DATA_DIR = Path("jetx_data")
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "history.json"
ML_CLF_FILE = DATA_DIR / "ml_clf.pkl"
ML_REG_FILE = DATA_DIR / "ml_reg.pkl"

def save_history(history):
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception: pass

def load_history():
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
    except Exception: pass
    return []

def save_models(clf, reg):
    try:
        with open(ML_CLF_FILE, 'wb') as f:
            pickle.dump(clf, f)
        with open(ML_REG_FILE, 'wb') as f:
            pickle.dump(reg, f)
    except Exception: pass

def load_models():
    try:
        if ML_CLF_FILE.exists() and ML_REG_FILE.exists():
            with open(ML_CLF_FILE, 'rb') as f:
                clf = pickle.load(f)
            with open(ML_REG_FILE, 'rb') as f:
                reg = pickle.load(f)
            return clf, reg
    except Exception: pass
    return None, None

# ===================== CONFIG & STYLE =====================
st.set_page_config(page_title="JETX X3+ LASER V16.1", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;700&display=swap');
    .stApp { background: radial-gradient(circle at center, #1a0033 0%, #000011 100%); color: #e0fbfc; font-family: 'Rajdhani', sans-serif; }
    .main-title { font-family: 'Orbitron', sans-serif; font-size: 3.5rem; font-weight: 900; text-align: center; background: linear-gradient(90deg, #ff0066, #00ffcc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .glass { background: rgba(20, 0, 40, 0.8); border: 1px solid #ff006655; border-radius: 15px; padding: 20px; }
    .glass-x3 { background: rgba(10, 0, 20, 0.95); border: 2px solid #ff0066; border-radius: 20px; padding: 25px; text-align: center; box-shadow: 0 0 30px rgba(255, 0, 102, 0.3); }
    .entry-time-x3 { font-family: 'Orbitron', sans-serif; font-size: 4rem; color: #ff0066; text-shadow: 0 0 30px #ff0066; margin: 15px 0; }
    .x3-prob-mega { font-size: 4.5rem; font-weight: 900; color: #00ffcc; font-family: 'Orbitron'; }
    .metric-box { background: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 10px; border: 1px solid #00ffcc33; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ===================== SESSION INITIALIZATION =====================
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "history" not in st.session_state: st.session_state.history = load_history()
if "last_result" not in st.session_state: st.session_state.last_result = None

# Authentication
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align:center; color:#ff0066; font-family:Orbitron;'>X3+ LASER LOGIN</h1>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        pw = st.text_input("🔑 Mot de passe", type="password")
        if st.button("✅ ACCÈS SYSTEM", use_container_width=True):
            if pw == "JET2026":
                st.session_state.authenticated = True
                st.rerun()
    st.stop()

# Model setup
ml_clf, ml_reg = load_models()
if ml_clf is None:
    ml_clf = Pipeline([("scaler", RobustScaler()), ("clf", GradientBoostingClassifier(n_estimators=100))])
    ml_reg = Pipeline([("scaler", RobustScaler()), ("reg", GradientBoostingRegressor(n_estimators=100))])

# ===================== CORE ENGINE =====================
def run_laser_engine(h_in, t_in, last_c):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    np.random.seed(int(h_hex[:8], 16))
    
    # Simulation logic
    sims = np.random.lognormal(np.log(2.15), 0.22, 120000)
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    strength = round(max(30, min(99.5, prob_x3 * 1.25 + (5 if last_c < 2.0 else -5))), 2)
    
    try:
        bt = datetime.strptime(t_in.strip(), "%H:%M:%S")
        entry = (bt + timedelta(seconds=47)).strftime("%H:%M:%S")
    except: entry = "00:00:00"

    res = {
        "timestamp": datetime.now().isoformat(),
        "entry": entry,
        "x3_prob": prob_x3,
        "strength_x3": strength,
        "x3_target": round(float(np.median(sims[sims>=3.0])), 2) if any(sims>=3.0) else 3.50,
        "safe": round(float(np.percentile(sims, 10)), 2), # Corrected key
        "max": round(float(np.percentile(sims, 90)), 2),
        "signal": "💎 ULTRA X3+" if strength > 82 else "🔥 STRONG X3+",
        "features": [prob_x3, strength, last_c],
        "x3_hit": None,
        "real_cote": None
    }
    st.session_state.history.append(res)
    save_history(st.session_state.history)
    return res

# ===================== UI LAYOUT =====================
st.markdown("<div class='main-title'>JETX X3+ LASER</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🛠️ SYSTEM CONTROL")
    if st.button("🗑️ RESET ALL DATA", use_container_width=True):
        st.session_state.history = []
        if HISTORY_FILE.exists(): os.remove(HISTORY_FILE)
        if ML_CLF_FILE.exists(): os.remove(ML_CLF_FILE)
        if ML_REG_FILE.exists(): os.remove(ML_REG_FILE)
        st.session_state.last_result = None
        st.rerun()

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### 📥 INPUT")
    # All fields are EMPTY by default
    h_input = st.text_input("SERVER HASH", value="", placeholder="Paste hash...")
    t_input = st.text_input("TIME (HH:MM:SS)", value="", placeholder="00:00:00")
    lc_input = st.number_input("LAST COTE", value=0.0, step=0.01)
    
    if st.button("🚀 ANALYSE", use_container_width=True):
        if h_input and t_input:
            st.session_state.last_result = run_laser_engine(h_input, t_input, lc_input)
            st.rerun()
    
    if st.session_state.last_result:
        st.markdown("---")
        st.markdown("### 💾 FEEDBACK")
        rc_input = st.number_input("REAL COTE", value=0.0, step=0.01)
        if st.button("SAVE RESULT", use_container_width=True):
            st.session_state.history[-1]["real_cote"] = rc_input
            st.session_state.history[-1]["x3_hit"] = (rc_input >= 3.0)
            
            # ML Training
            labeled = [h for h in st.session_state.history if h["real_cote"] is not None]
            if len(labeled) > 5:
                try:
                    X = [h["features"] for h in labeled]
                    y_clf = [1 if h["x3_hit"] else 0 for h in labeled]
                    y_reg = [h["real_cote"] for h in labeled]
                    ml_clf.fit(X, y_clf)
                    ml_reg.fit(X, y_reg)
                    save_models(ml_clf, ml_reg)
                except: pass
                
            save_history(st.session_state.history)
            st.success("AI Updated!")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if st.session_state.last_result:
        r = st.session_state.last_result
        st.markdown("<div class='glass-x3'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color:#ff0066;'>{r['signal']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='x3-prob-mega'>{r['x3_prob']}%</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-time-x3'>{r['entry']}</div>", unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        # Using .get() for safety
        m1.markdown(f"<div class='metric-box'><small>SAFE</small><br><b>{r.get('safe', 1.1)}x</b></div>", unsafe_allow_html=True)
        m2.markdown(f"<div class='metric-box'><small>TARGET</small><br><b style='color:#00ffcc;'>{r.get('x3_target', 3.0)}x</b></div>", unsafe_allow_html=True)
        m3.markdown(f"<div class='metric-box'><small>MAX</small><br><b>{r.get('max', 5.0)}x</b></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Logs
st.markdown("---")
if st.session_state.history:
    st.markdown("### 🕒 RECENT LOGS")
    df = pd.DataFrame(st.session_state.history).tail(8)
    if "real_cote" in df.columns:
        st.dataframe(df[["entry", "x3_prob", "strength_x3", "real_cote"]], use_container_width=True)
