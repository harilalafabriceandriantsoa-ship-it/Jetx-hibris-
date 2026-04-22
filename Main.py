import streamlit as st
import numpy as np
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import pytz
import json
import os
from pathlib import Path

from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.preprocessing import RobustScaler
from sklearn.pipeline import Pipeline

# ===================== PERSISTENCE SYSTEM =====================
DATA_DIR = Path("/home/claude/jetx_data")
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "history.json"
ML_CLF_FILE = DATA_DIR / "ml_clf.pkl"
ML_REG_FILE = DATA_DIR / "ml_reg.pkl"

def save_history(history):
    """Save history to disk"""
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        st.warning(f"⚠️ Erreur sauvegarde: {e}")

def load_history():
    """Load history from disk"""
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.warning(f"⚠️ Erreur chargement: {e}")
    return []

def save_models(clf, reg):
    """Save ML models"""
    try:
        import pickle
        with open(ML_CLF_FILE, 'wb') as f:
            pickle.dump(clf, f)
        with open(ML_REG_FILE, 'wb') as f:
            pickle.dump(reg, f)
    except Exception:
        pass

def load_models():
    """Load ML models"""
    try:
        import pickle
        if ML_CLF_FILE.exists() and ML_REG_FILE.exists():
            with open(ML_CLF_FILE, 'rb') as f:
                clf = pickle.load(f)
            with open(ML_REG_FILE, 'rb') as f:
                reg = pickle.load(f)
            return clf, reg
    except Exception:
        pass
    return None, None

# ===================== CONFIG =====================
st.set_page_config(page_title="JETX X3+ LASER V16.1", layout="wide", initial_sidebar_state="collapsed")

# ===================== PASSWORD =====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
        .stApp { background: radial-gradient(ellipse at 50% 0%, #1a0033 0%, #000011 100%); }
        .login-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 4.5rem; font-weight: 900; text-align: center;
            background: linear-gradient(90deg, #ff0066, #00ffcc, #ff0066);
            background-size: 200%;
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            animation: laser-glow 3s ease infinite;
            margin-bottom: 0.2rem;
        }
        .login-sub {
            text-align: center; color: #ff0066dd; font-family: 'Orbitron', sans-serif;
            font-size: 1.1rem; letter-spacing: 0.4em; margin-bottom: 2rem;
            text-shadow: 0 0 20px #ff006688;
        }
        @keyframes laser-glow {
            0%, 100% { background-position: 0%; filter: drop-shadow(0 0 15px #ff006688); }
            50%      { background-position: 100%; filter: drop-shadow(0 0 40px #00ffcc88); }
        }
    </style>
    <div class='login-title'>X3+ LASER</div>
    <div class='login-sub'>V 1 6 . 1 &nbsp; F O C U S</div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        pw = st.text_input("🔑 Mot de passe", type="password", placeholder="Code d'accès...")
        if st.button("✅ ACCÈS X3+ LASER", use_container_width=True):
            if pw == "JET2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Mot de passe incorrect")
    st.stop()

# ===================== CSS X3+ LASER =====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');

    .stApp {
        background: radial-gradient(ellipse at 30% 0%, #1a0033 0%, #000011 50%, #001a1a 100%);
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.8rem; font-weight: 900; text-align: center;
        background: linear-gradient(90deg, #ff0066, #00ffcc, #ff0066);
        background-size: 200%;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: laser-pulse 3s ease infinite;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center; color: #ff006699;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.7rem; letter-spacing: 0.5em; margin-bottom: 1.2rem;
        text-shadow: 0 0 15px #ff006666;
    }
    .glass {
        background: rgba(10, 0, 20, 0.88);
        border: 1px solid rgba(255,0,102,0.3);
        border-radius: 18px; padding: 22px;
        backdrop-filter: blur(10px);
    }
    .entry-time-x3 {
        font-family: 'Orbitron', sans-serif;
        font-size: 4.2rem; font-weight: 900; text-align: center;
        color: #ff0066;
        text-shadow: 0 0 40px #ff0066;
    }
    .x3-prob-mega {
        font-size: 4.5rem; font-weight: 900;
        font-family: 'Orbitron', sans-serif;
        text-align: center;
        color: #ff0066;
    }
    .x3-target {
        background: rgba(255,0,102,0.1);
        border: 2px solid rgba(255,0,102,0.6);
        border-radius: 16px; padding: 18px; text-align: center;
    }
    .metric-val-x3 { font-size: 2.4rem; font-weight: 900; font-family: 'Orbitron', sans-serif; }
    .sig-ultra-x3 { color: #ff0066; font-family: 'Orbitron'; font-size: 1.5rem; font-weight: 900; }
</style>
""", unsafe_allow_html=True)

# ===================== HELPERS =====================
def get_time():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def get_x3_streak_info(history):
    x3_results = [h.get("x3_hit") for h in history if h.get("x3_hit") is not None]
    if not x3_results: return 0, 0, "neutral", 0.0
    last = x3_results[-1]
    streak = 0
    for r in reversed(x3_results):
        if r == last: streak += 1
        else: break
    recent = x3_results[-15:]
    x3_rate = sum(recent) / len(recent) if recent else 0.0
    mode = "x3_hot" if last and streak >= 2 else "x3_cold" if not last and streak >= 3 else "neutral"
    return sum(1 for r in x3_results if r), sum(1 for r in x3_results if not r), mode, x3_rate

def get_adaptive_x3_target(history):
    x3_cotes = [h.get("real_cote") for h in history if h.get("x3_hit") and h.get("real_cote")]
    if len(x3_cotes) < 3: return 3.25
    arr = np.array(x3_cotes)
    target = round(0.6 * np.median(arr) + 0.4 * np.percentile(arr, 75), 2)
    return max(3.0, min(6.0, target))

# ===================== SESSION STATE =====================
if "history" not in st.session_state: st.session_state.history = load_history()
if "last" not in st.session_state: st.session_state.last = None
if "ml_trained_count" not in st.session_state: st.session_state.ml_trained_count = 0

clf_loaded, reg_loaded = load_models()
st.session_state.ml_clf = clf_loaded or Pipeline([("scaler", RobustScaler()), ("clf", GradientBoostingClassifier())])
st.session_state.ml_reg = reg_loaded or Pipeline([("scaler", RobustScaler()), ("reg", GradientBoostingRegressor())])

# ===================== ENGINE =====================
def run_x3_laser_engine(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:48], 16)
    np.random.seed(h_num & 0xFFFFFFFF)

    sims = np.random.lognormal(np.log(2.05 + (h_num % 1300) / 140), 0.19, 150_000)
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    
    x3_hits, x3_misses, x3_mode, x3_rate = get_x3_streak_info(st.session_state.history)
    
    strength_x3 = max(30.0, min(99.0, prob_x3 * 1.5 + x3_rate * 20))
    
    try:
        bt = datetime.combine(get_time().date(), datetime.strptime(t_in.strip(), "%H:%M:%S").time())
    except:
        bt = get_time()
    
    entry = (bt + timedelta(seconds=45)).strftime("%H:%M:%S")

    res = {
        "timestamp": get_time().isoformat(),
        "entry": entry,
        "signal": "💎 ULTRA X3+ LASER" if strength_x3 > 80 else "🔥 STRONG X3+",
        "sig_class": "sig-ultra-x3",
        "x3_prob": prob_x3,
        "x3_target": get_adaptive_x3_target(st.session_state.history),
        "strength_x3": strength_x3,
        "x3_hits": x3_hits,
        "x3_misses": x3_misses,
        "x3_mode": x3_mode,
        "x3_rate": round(x3_rate * 100, 1),
        "x3_hit": None,
        "real_cote": None,
        "hist": np.histogram(sims, bins=20, range=(1, 6))[0].tolist(),
        "sim_x3_count": int(np.sum(sims >= 3.0))
    }
    st.session_state.history.append(res)
    save_history(st.session_state.history)
    return res

# ===================== UI =====================
st.markdown("<div class='main-title'>X3+ LASER</div>", unsafe_allow_html=True)

col_input, col_result = st.columns([1, 2], gap="large")

with col_input:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    h_in = st.text_input("HASH")
    t_in = st.text_input("TIME (HH:MM:SS)")
    l_c = st.number_input("LAST COTE", value=2.50)
    if st.button("🚀 LANCER X3+"):
        if h_in and t_in:
            st.session_state.last = run_x3_laser_engine(h_in, t_in, l_c)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col_result:
    r = st.session_state.last
    if r:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown(f"<div class='sig-ultra-x3'>{r['signal']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='x3-prob-mega'>{r['x3_prob']}%</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-time-x3'>{r['entry']}</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        c1.metric("TARGET", f"{r['x3_target']}x")
        c2.metric("STRENGTH", f"{r['strength_x3']}%")
        
        if st.button("🎯 ENREGISTRER WIN"):
            st.session_state.history[-1]["x3_hit"] = True
            save_history(st.session_state.history)
            st.success("Gagné !")
        st.markdown("</div>", unsafe_allow_html=True)
