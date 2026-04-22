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
        st.warning(f"âš ï¸ Erreur sauvegarde: {e}")

def load_history():
    """Load history from disk"""
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.warning(f"âš ï¸ Erreur chargement: {e}")
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
        pw = st.text_input("ðŸ”‘ Mot de passe", type="password", placeholder="Code d'accÃ¨s...")
        if st.button("âœ… ACCÃˆS X3+ LASER", use_container_width=True):
            if pw == "JET2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("âŒ Mot de passe incorrect")
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

    /* Laser grid background */
    .stApp::before {
        content: '';
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-image:
            repeating-linear-gradient(0deg, transparent, transparent 100px, rgba(255,0,102,0.03) 100px, rgba(255,0,102,0.03) 101px),
            repeating-linear-gradient(90deg, transparent, transparent 100px, rgba(0,255,204,0.03) 100px, rgba(0,255,204,0.03) 101px);
        pointer-events: none; z-index: 0;
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
    @keyframes laser-pulse {
        0%, 100% { background-position: 0%; }
        50%      { background-position: 100%; }
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
        box-shadow: 0 0 30px rgba(255,0,102,0.08), inset 0 1px 0 rgba(255,255,255,0.03);
        backdrop-filter: blur(10px);
    }

    .glass-x3 {
        background: rgba(5, 0, 15, 0.94);
        border: 2px solid rgba(255,0,102,0.6);
        border-radius: 18px; padding: 24px;
        box-shadow: 0 0 60px rgba(255,0,102,0.2), 0 0 100px rgba(0,255,204,0.1);
    }

    /* X3+ FOCUS signals */
    .sig-ultra-x3 {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.5rem; font-weight: 900;
        color: #ff0066;
        text-shadow: 0 0 25px #ff0066, 0 0 50px #ff0066aa, 0 0 80px #ff006644;
        letter-spacing: 0.08em;
    }
    .sig-strong-x3 {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.3rem; font-weight: 700;
        color: #00ffcc;
        text-shadow: 0 0 20px #00ffcc, 0 0 40px #00ffcc88;
    }
    .sig-moderate-x3 {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.1rem; font-weight: 600;
        color: #fbbf24;
        text-shadow: 0 0 15px #fbbf24;
    }

    /* Entry time - X3+ focused */
    .entry-time-x3 {
        font-family: 'Orbitron', sans-serif;
        font-size: 4.2rem; font-weight: 900; text-align: center;
        color: #ff0066;
        text-shadow: 0 0 40px #ff0066, 0 0 80px #ff0066aa;
        letter-spacing: 0.1em;
        margin: 16px 0;
        animation: time-pulse 2s ease infinite alternate;
    }
    @keyframes time-pulse {
        from { text-shadow: 0 0 40px #ff0066, 0 0 80px #ff0066aa; }
        to   { text-shadow: 0 0 60px #ff0066, 0 0 120px #ff0066dd; }
    }

    /* X3+ probability display */
    .x3-prob-mega {
        font-size: 4.5rem; font-weight: 900;
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(135deg, #ff0066, #ff3399, #ff0066);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center;
        filter: drop-shadow(0 0 30px #ff0066aa);
        margin: 20px 0;
    }

    /* Cashout X3+ boxes */
    .x3-target {
        background: linear-gradient(135deg, rgba(255,0,102,0.25), rgba(255,0,102,0.08));
        border: 2px solid rgba(255,0,102,0.6);
        border-radius: 16px; padding: 18px; text-align: center;
        box-shadow: 0 0 25px rgba(255,0,102,0.3), inset 0 0 20px rgba(255,0,102,0.05);
    }
    .x3-target-safe {
        background: linear-gradient(135deg, rgba(0,255,204,0.18), rgba(0,255,204,0.06));
        border: 1.5px solid rgba(0,255,204,0.4);
        border-radius: 16px; padding: 18px; text-align: center;
    }
    .metric-val-x3 { font-size: 2.4rem; font-weight: 900; font-family: 'Orbitron', sans-serif; }
    .metric-lbl { font-size: 0.7rem; color: #ffffff88; letter-spacing: 0.2em; margin-top: 4px; }

    /* X3+ confidence bar */
    .x3-confidence-track {
        background: rgba(255,255,255,0.05);
        border-radius: 99px; height: 14px; overflow: hidden; margin-top: 8px;
        border: 1px solid rgba(255,0,102,0.2);
    }
    .x3-confidence-fill {
        height: 100%; border-radius: 99px;
        background: linear-gradient(90deg, #ff0066, #ff3399, #00ffcc);
        box-shadow: 0 0 20px #ff0066dd, inset 0 0 10px rgba(255,255,255,0.2);
        transition: width 1s cubic-bezier(0.4,0,0.2,1);
    }

    /* Alert X3+ */
    .alert-x3 {
        background: rgba(255,0,102,0.15);
        border: 1px solid rgba(255,0,102,0.4);
        border-radius: 12px; padding: 12px 16px;
        font-size: 0.85rem; color: #ffaac8;
        margin-top: 12px;
    }

    /* Section labels */
    .sec-lbl-x3 {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.6rem; letter-spacing: 0.35em;
        color: #ff006666; text-transform: uppercase;
        margin-bottom: 8px;
    }

    /* Buttons */
    .stButton>button {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1rem !important; font-weight: 700 !important;
        letter-spacing: 0.05em !important;
    }

    /* X3+ histogram */
    .hist-x3 {
        display: inline-block; width: 14px; border-radius: 4px 4px 0 0;
        vertical-align: bottom; margin: 0 1px;
        transition: all 0.4s ease;
    }
    .hist-x3:hover { filter: brightness(1.4); }

    /* Stats boxes */
    .stat-box-x3 {
        background: rgba(255,0,102,0.08);
        border: 1px solid rgba(255,0,102,0.25);
        border-radius: 12px; padding: 12px 16px; text-align: center;
    }
    .stat-val-x3 { font-size: 1.6rem; font-weight: 700; font-family: 'Orbitron', sans-serif; }

    /* Input focus */
    .stTextInput input, .stNumberInput input {
        background: rgba(255,0,102,0.05) !important;
        border: 1px solid rgba(255,0,102,0.25) !important;
        color: #e0fbfc !important;
        border-radius: 12px !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: rgba(255,0,102,0.7) !important;
        box-shadow: 0 0 0 3px rgba(255,0,102,0.15) !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #000011; }
    ::-webkit-scrollbar-thumb { background: #ff006644; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ===================== HELPERS =====================
def get_time():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def get_x3_streak_info(history):
    """Track X3+ specific streaks"""
    x3_results = [h.get("x3_hit") for h in history if h.get("x3_hit") is not None]
    if not x3_results:
        return 0, 0, "neutral", 0.0

    # Current X3+ streak
    last = x3_results[-1]
    streak = 0
    for r in reversed(x3_results):
        if r == last:
            streak += 1
        else:
            break

    # X3+ hit rate (last 15)
    recent = x3_results[-15:]
    x3_rate = sum(recent) / len(recent) if recent else 0.0

    # Mode
    if last and streak >= 2:
        mode = "x3_hot"
    elif not last and streak >= 3:
        mode = "x3_cold"
    else:
        mode = "neutral"

    x3_hits = sum(1 for r in x3_results if r)
    x3_misses = len(x3_results) - x3_hits

    return x3_hits, x3_misses, mode, x3_rate

def get_adaptive_x3_target(history):
    """Compute X3+ target from real X3+ hits"""
    x3_cotes = [h.get("real_cote") for h in history if h.get("x3_hit") and h.get("real_cote")]
    if len(x3_cotes) < 3:
        return 3.25  # Default conservative X3+ target

    arr = np.array(x3_cotes)
    median_x3 = float(np.median(arr))
    p75_x3 = float(np.percentile(arr, 75))
    
    # Blend median + P75 for realistic X3+ cashout
    target = round(0.6 * median_x3 + 0.4 * p75_x3, 2)
    return max(3.0, min(6.0, target))

def build_x3_features(prob_x3, conf_x3, moy, spread, last_cote, x3_hits, x3_misses, volatility, x3_rate, mode_val, sim_x3_count):
    return [prob_x3, conf_x3, moy, spread, last_cote, x3_hits, x3_misses, volatility, x3_rate * 100, mode_val, sim_x3_count]

# ===================== SESSION STATE =====================
defaults = {
    "history": load_history(),
    "last": None,
    "ml_clf": None,
    "ml_reg": None,
    "ml_trained_count": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def get_or_build_models():
    clf, reg = load_models()
    if clf is None or reg is None:
        st.session_state.ml_clf = Pipeline([
            ("scaler", RobustScaler()),
            ("clf", GradientBoostingClassifier(
                n_estimators=300, max_depth=6,
                learning_rate=0.06, subsample=0.9, random_state=42
            ))
        ])
        st.session_state.ml_reg = Pipeline([
            ("scaler", RobustScaler()),
            ("reg", GradientBoostingRegressor(
                n_estimators=250, max_depth=5,
                learning_rate=0.08, subsample=0.9, random_state=42
            ))
        ])
    else:
        st.session_state.ml_clf = clf
        st.session_state.ml_reg = reg

get_or_build_models()

def try_train_x3_ml(history):
    """Progressive X3+ ML training"""
    labeled = [h for h in history if h.get("x3_hit") is not None and h.get("features")]
    if len(labeled) < 3:
        return False

    X = np.array([h["features"] for h in labeled])
    y_clf = np.array([1 if h["x3_hit"] else 0 for h in labeled])
    y_reg = np.array([h.get("real_cote", 3.0) if h["x3_hit"] else 1.5 for h in labeled])

    try:
        st.session_state.ml_clf.fit(X, y_clf)
        st.session_state.ml_reg.fit(X, y_reg)
        st.session_state.ml_trained_count = len(labeled)
        save_models(st.session_state.ml_clf, st.session_state.ml_reg)
        return True
    except Exception:
        return False

# ===================== X3+ LASER ENGINE =====================
def run_x3_laser_engine(h_in, t_in, last_cote):
    # --- Hash entropy ---
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:48], 16)
    np.random.seed(h_num & 0xFFFFFFFF)

    # --- X3+ FOCUSED SIMULATION 150k ---
    base = 2.05 + (h_num % 1300) / 140
    last_cote_adj = max(1.1, last_cote)
    
    # Lower sigma = more concentrated around mean (better X3+ prediction)
    sigma = 0.19 - (last_cote_adj * 0.0022)
    
    sims = np.random.lognormal(np.log(base), sigma, 150_000)

    # X3+ probability (main metric)
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    
    # X3+ sub-categories
    prob_x3_5 = round(float(np.mean(sims >= 3.5)) * 100, 2)
    prob_x4   = round(float(np.mean(sims >= 4.0)) * 100, 2)
    prob_x5   = round(float(np.mean(sims >= 5.0)) * 100, 2)
    
    # Count X3+ hits in simulation
    sim_x3_count = int(np.sum(sims >= 3.0))
    
    moy   = round(float(np.mean(sims)), 2)
    maxv  = round(float(np.percentile(sims, 98.0)), 2)
    minv  = round(float(np.percentile(sims, 2.0)), 2)
    spread = round(maxv - minv, 2)

    # --- X3+ streak analysis ---
    x3_hits, x3_misses, x3_mode, x3_rate = get_x3_streak_info(st.session_state.history)
    mode_val = {"x3_hot": 2, "neutral": 0, "x3_cold": -2}[x3_mode]

    # --- Volatility (X3+ focused - 25 window) ---
    recent_x3_probs = [h.get("x3_prob", 30) for h in st.session_state.history[-25:]]
    volatility = round(float(np.std(recent_x3_probs)) if len(recent_x3_probs) >= 3 else 8.0, 2)

    # --- X3+ CONFIDENCE (heavily weighted toward X3+ prob) ---
    conf_x3 = round(max(35, min(99,
        prob_x3 * 1.20 +           # ðŸŽ¯ MAIN: X3+ probability weighted 120%
        prob_x3_5 * 0.40 +         # Bonus for higher X3+
        prob_x4 * 0.25 +
        x3_rate * 35 +             # Historical X3+ rate
        mode_val * 8 +             # Hot/cold streak
        (h_num % 180) / 4.5 -
        volatility * 1.8 +
        last_cote_adj * 6
    )), 2)

    # --- Features for X3+ ML ---
    features = build_x3_features(prob_x3, conf_x3, moy, spread, last_cote_adj, 
                                  x3_hits, x3_misses, volatility, x3_rate, mode_val, sim_x3_count)

    # --- X3+ AI score (ML trained specifically on X3+ hits) ---
    ai_x3_score = round(conf_x3 * 0.94, 2)
    ml_used = False
    if st.session_state.ml_trained_count >= 3:
        try:
            X = np.array(features).reshape(1, -1)
            prob_ml = float(st.session_state.ml_clf.predict_proba(X)[0][1]) * 100
            reg_ml  = float(st.session_state.ml_reg.predict(X)[0])
            
            # Heavily weight ML prediction for X3+
            ai_x3_score = round(0.70 * prob_ml + 0.20 * (reg_ml * 20) + 0.10 * conf_x3, 2)
            ml_used = True
        except Exception:
            pass

    # --- X3+ STRENGTH (laser-focused on X3+ probability) ---
    strength_x3 = round(
        prob_x3 * 0.50 +           # ðŸŽ¯ 50% weight on X3+ prob
        ai_x3_score * 0.30 +       # 30% AI
        conf_x3 * 0.15 +           # 15% confidence
        x3_rate * 40 +             # X3+ hit rate
        mode_val * 10 -            # Streak bonus
        volatility * 2.5 +
        (sim_x3_count / 1500),     # Normalized sim X3+ count
    2)
    strength_x3 = max(30.0, min(99.0, strength_x3))

    # --- Adaptive X3+ target ---
    x3_target = get_adaptive_x3_target(st.session_state.history)

    # --- Safe & Max targets ---
    safe_target = round(minv * 1.15, 2)  # 15% above min
    max_target  = round(np.percentile(sims[sims >= 3.0], 70) if np.any(sims >= 3.0) else 4.5, 2)

    # --- Dynamic entry time (X3+ optimized) ---
    try:
        bt = datetime.combine(get_time().date(), datetime.strptime(t_in.strip(), "%H:%M:%S").time())
    except Exception:
        bt = get_time()

    hash_shift = (int(h_hex[:20], 16) % 90) - 45
    vol_adj    = int(volatility * 0.8)
    str_bonus  = 35 if strength_x3 > 90 else 26 if strength_x3 > 78 else 18
    x3_adj     = 8 if x3_mode == "x3_hot" else -5 if x3_mode == "x3_cold" else 0

    final_sec = max(20, min(110, 22 + (h_num % 60) + hash_shift + vol_adj + str_bonus + x3_adj))
    entry = (bt + timedelta(seconds=final_sec)).strftime("%H:%M:%S")

    # --- X3+ SIGNAL classification (ultra strict) ---
    if strength_x3 >= 88 and prob_x3 >= 42:
        signal     = "ðŸ’ŽðŸ’ŽðŸ’Ž ULTRA X3+ LASER â€” BUY NOW"
        sig_class  = "sig-ultra-x3"
        confidence_label = "EXTREME"
    elif strength_x3 >= 75 and prob_x3 >= 35:
        signal     = "ðŸ”¥ðŸ”¥ STRONG X3+ TARGET â€” ENGAGE"
        sig_class  = "sig-strong-x3"
        confidence_label = "HIGH"
    elif strength_x3 >= 60 and prob_x3 >= 28:
        signal     = "ðŸŽ¯ MODERATE X3+ â€” WATCH CLOSE"
        sig_class  = "sig-moderate-x3"
        confidence_label = "MODERATE"
    else:
        signal     = "âš ï¸ LOW X3+ â€” SKIP OR MICRO BET"
        sig_class  = "sig-moderate-x3"
        confidence_label = "LOW"

    # --- X3+ distribution histogram (focused 1Ã— â†’ 6Ã—) ---
    buckets = np.histogram(sims, bins=25, range=(1.0, 6.0))[0]
    hist_data = [int(b) for b in buckets]

    res = {
        "timestamp": get_time().isoformat(),
        "entry": entry,
        "signal": signal,
        "sig_class": sig_class,
        "confidence_label": confidence_label,
        
        # X3+ core metrics
        "x3_prob": prob_x3,
        "x3_5_prob": prob_x3_5,
        "x4_prob": prob_x4,
        "x5_prob": prob_x5,
        
        "conf_x3": conf_x3,
        "ai_x3_score": ai_x3_score,
        "strength_x3": strength_x3,
        
        # Targets
        "safe_target": safe_target,
        "x3_target": x3_target,
        "max_target": max_target,
        
        # Support
