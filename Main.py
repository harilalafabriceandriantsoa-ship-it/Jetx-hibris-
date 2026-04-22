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
# Ampiasaina ny path azo antoka kokoa amin'ny Streamlit Cloud
DATA_DIR = Path("jetx_data")
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
        pass
    return []

def save_models(clf, reg):
    """Save ML models"""
    try:
        with open(ML_CLF_FILE, 'wb') as f:
            pickle.dump(clf, f)
        with open(ML_REG_FILE, 'wb') as f:
            pickle.dump(reg, f)
    except Exception:
        pass

def load_models():
    """Load ML models"""
    try:
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
    .stApp { background: radial-gradient(ellipse at 30% 0%, #1a0033 0%, #000011 50%, #001a1a 100%); color: #e0fbfc; font-family: 'Rajdhani', sans-serif; }
    .main-title { font-family: 'Orbitron', sans-serif; font-size: 3.8rem; font-weight: 900; text-align: center; background: linear-gradient(90deg, #ff0066, #00ffcc, #ff0066); background-size: 200%; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: laser-pulse 3s ease infinite; margin-bottom: 0; }
    .subtitle { text-align: center; color: #ff006699; font-family: 'Orbitron', sans-serif; font-size: 0.7rem; letter-spacing: 0.5em; margin-bottom: 1.2rem; }
    .glass { background: rgba(10, 0, 20, 0.88); border: 1px solid rgba(255,0,102,0.3); border-radius: 18px; padding: 22px; backdrop-filter: blur(10px); }
    .glass-x3 { background: rgba(5, 0, 15, 0.94); border: 2px solid rgba(255,0,102,0.6); border-radius: 18px; padding: 24px; box-shadow: 0 0 60px rgba(255,0,102,0.2); }
    .sig-ultra-x3 { font-family: 'Orbitron', sans-serif; font-size: 1.5rem; font-weight: 900; color: #ff0066; text-shadow: 0 0 25px #ff0066; }
    .entry-time-x3 { font-family: 'Orbitron', sans-serif; font-size: 4.2rem; font-weight: 900; text-align: center; color: #ff0066; text-shadow: 0 0 40px #ff0066; margin: 16px 0; }
    .x3-prob-mega { font-size: 4.5rem; font-weight: 900; font-family: 'Orbitron', sans-serif; background: linear-gradient(135deg, #ff0066, #ff3399); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin: 20px 0; }
    .x3-target { background: linear-gradient(135deg, rgba(255,0,102,0.25), rgba(255,0,102,0.08)); border: 2px solid rgba(255,0,102,0.6); border-radius: 16px; padding: 18px; text-align: center; }
    .metric-val-x3 { font-size: 2.4rem; font-weight: 900; font-family: 'Orbitron', sans-serif; }
    .x3-confidence-track { background: rgba(255,255,255,0.05); border-radius: 99px; height: 14px; overflow: hidden; margin-top: 8px; border: 1px solid rgba(255,0,102,0.2); }
    .x3-confidence-fill { height: 100%; border-radius: 99px; background: linear-gradient(90deg, #ff0066, #00ffcc); transition: width 1s ease; }
    .sec-lbl-x3 { font-family: 'Orbitron', sans-serif; font-size: 0.6rem; letter-spacing: 0.35em; color: #ff006666; text-transform: uppercase; margin-bottom: 8px; }
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
    mode = "x3_hot" if (last and streak >= 2) else "x3_cold" if (not last and streak >= 3) else "neutral"
    return sum(x3_results), len(x3_results) - sum(x3_results), mode, x3_rate

def get_adaptive_x3_target(history):
    x3_cotes = [h.get("real_cote") for h in history if h.get("x3_hit") and h.get("real_cote")]
    if len(x3_cotes) < 3: return 3.25
    arr = np.array(x3_cotes)
    return max(3.0, min(6.0, round(float(np.median(arr)) * 0.6 + float(np.percentile(arr, 75)) * 0.4, 2)))

def build_x3_features(prob_x3, conf_x3, moy, spread, last_cote, x3_hits, x3_misses, volatility, x3_rate, mode_val, sim_x3_count):
    return [prob_x3, conf_x3, moy, spread, last_cote, x3_hits, x3_misses, volatility, x3_rate * 100, mode_val, sim_x3_count]

# ===================== SESSION STATE =====================
if "history" not in st.session_state: st.session_state.history = load_history()
if "last" not in st.session_state: st.session_state.last = None
if "ml_trained_count" not in st.session_state: st.session_state.ml_trained_count = 0

def get_or_build_models():
    clf, reg = load_models()
    if clf is None:
        st.session_state.ml_clf = Pipeline([("scaler", RobustScaler()), ("clf", GradientBoostingClassifier(n_estimators=300, random_state=42))])
        st.session_state.ml_reg = Pipeline([("scaler", RobustScaler()), ("reg", GradientBoostingRegressor(n_estimators=250, random_state=42))])
    else:
        st.session_state.ml_clf, st.session_state.ml_reg = clf, reg
        st.session_state.ml_trained_count = len([h for h in st.session_state.history if h.get("features") and h.get("x3_hit") is not None])

get_or_build_models()

def try_train_x3_ml(history):
    labeled = [h for h in history if h.get("x3_hit") is not None and h.get("features")]
    if len(labeled) < 3: return False
    try:
        X = np.array([h["features"] for h in labeled])
        y_clf = np.array([1 if h["x3_hit"] else 0 for h in labeled])
        y_reg = np.array([h.get("real_cote", 3.0) for h in labeled])
        st.session_state.ml_clf.fit(X, y_clf)
        st.session_state.ml_reg.fit(X, y_reg)
        st.session_state.ml_trained_count = len(labeled)
        save_models(st.session_state.ml_clf, st.session_state.ml_reg)
        return True
    except: return False

# ===================== ENGINE =====================
def run_x3_laser_engine(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:48], 16)
    np.random.seed(h_num & 0xFFFFFFFF)
    
    sims = np.random.lognormal(np.log(2.05 + (h_num % 1300)/140), 0.19, 150000)
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    sim_x3_count = int(np.sum(sims >= 3.0))
    moy, minv = round(float(np.mean(sims)), 2), round(float(np.percentile(sims, 2.0)), 2)
    spread = round(float(np.percentile(sims, 98.0)) - minv, 2)

    x3_hits, x3_misses, x3_mode, x3_rate = get_x3_streak_info(st.session_state.history)
    mode_val = {"x3_hot": 2, "neutral": 0, "x3_cold": -2}[x3_mode]
    volatility = round(float(np.std([h.get("x3_prob", 30) for h in st.session_state.history[-25:]])) if len(st.session_state.history) > 3 else 8.0, 2)

    conf_x3 = round(max(35, min(99, prob_x3 * 1.2 + x3_rate * 35 + mode_val * 8 + last_cote * 6)), 2)
    features = build_x3_features(prob_x3, conf_x3, moy, spread, last_cote, x3_hits, x3_misses, volatility, x3_rate, mode_val, sim_x3_count)
    
    strength_x3 = round(max(30, min(99, prob_x3 * 0.6 + conf_x3 * 0.4 + mode_val * 5)), 2)
    
    try:
        bt = datetime.combine(get_time().date(), datetime.strptime(t_in.strip(), "%H:%M:%S").time())
    except:
        bt = get_time()
    entry = (bt + timedelta(seconds=int(45 + (h_num % 40)))).strftime("%H:%M:%S")

    res = {
        "timestamp": get_time().isoformat(), "entry": entry, "x3_prob": prob_x3,
        "conf_x3": conf_x3, "strength_x3": strength_x3, "x3_target": get_adaptive_x3_target(st.session_state.history),
        "safe_target": round(minv * 1.15, 2), "max_target": round(np.percentile(sims[sims>=3.0], 70), 2) if sim_x3_count > 0 else 4.0,
        "x3_mode": x3_mode, "x3_hits": x3_hits, "x3_misses": x3_misses, "x3_rate": round(x3_rate*100, 1),
        "sim_x3_count": sim_x3_count, "volatility": volatility, "features": features, "x3_hit": None, "real_cote": None,
        "sig_class": "sig-ultra-x3" if strength_x3 > 80 else "sig-strong-x3", "signal": "💎 ULTRA X3+" if strength_x3 > 80 else "🔥 STRONG X3+"
    }
    st.session_state.history.append(res)
    save_history(st.session_state.history)
    return res

# ===================== UI =====================
st.markdown("<div class='main-title'>X3+ LASER</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>V 1 6 . 1 &nbsp; F O C U S</div>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2.2])

with col1:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    h_in = st.text_input("HASH")
    t_in = st.text_input("TIME (HH:MM:SS)", value=get_time().strftime("%H:%M:%S"))
    lc = st.number_input("LAST COTE", value=2.5)
    if st.button("🚀 ANALYSE"):
        if h_in and t_in:
            st.session_state.last = run_x3_laser_engine(h_in, t_in, lc)
            st.rerun()
    
    if st.session_state.last:
        st.markdown("---")
        rc = st.number_input("REAL COTE", value=3.0)
        if st.button("💾 SAVE RESULT"):
            st.session_state.history[-1]["real_cote"] = rc
            st.session_state.history[-1]["x3_hit"] = (rc >= 3.0)
            try_train_x3_ml(st.session_state.history)
            save_history(st.session_state.history)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    r = st.session_state.last
    if r:
        st.markdown("<div class='glass-x3'>", unsafe_allow_html=True)
        st.markdown(f"<div class='{r['sig_class']}' style='text-align:center;'>{r['signal']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='x3-prob-mega'>{r['x3_prob']}%</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-time-x3'>{r['entry']}</div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("SAFE", f"{r['safe_target']}x")
        c2.metric("TARGET", f"{r['x3_target']}x")
        c3.metric("MAX", f"{r['max_target']}x")
        
        st.markdown(f"<div class='x3-confidence-track'><div class='x3-confidence-fill' style='width:{r['strength_x3']}%;'></div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
if st.session_state.history:
    st.table(pd.DataFrame(st.session_state.history).tail(5)[["entry", "x3_prob", "x3_rate", "real_cote"]])
