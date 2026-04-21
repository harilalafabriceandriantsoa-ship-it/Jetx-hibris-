import streamlit as st
import numpy as np
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import pytz
from collections import deque

from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.preprocessing import RobustScaler
from sklearn.pipeline import Pipeline

# ===================== CONFIG =====================
st.set_page_config(page_title="JETX COSMOS V16.0", layout="wide", initial_sidebar_state="collapsed")

# ===================== PASSWORD =====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
        .stApp { background: linear-gradient(135deg, #020210, #0d001a, #00001a); }
        .login-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 4rem; font-weight: 900; text-align: center;
            background: linear-gradient(90deg, #00ffcc, #a855f7, #00ccff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            animation: pulse-glow 2.5s ease-in-out infinite alternate;
            margin-bottom: 0.2rem;
        }
        .login-sub {
            text-align: center; color: #00ffcc99; font-family: 'Orbitron', sans-serif;
            font-size: 1rem; letter-spacing: 0.3em; margin-bottom: 2rem;
        }
        @keyframes pulse-glow {
            from { filter: drop-shadow(0 0 10px #00ffcc88); }
            to   { filter: drop-shadow(0 0 35px #a855f788); }
        }
    </style>
    <div class='login-title'>JETX COSMOS</div>
    <div class='login-sub'>V 1 6 . 0 &nbsp;&nbsp; U L T R A</div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        pw = st.text_input("ðŸ”‘ Mot de passe", type="password", placeholder="Entrez le code d'accÃ¨s...")
        if st.button("âœ… ACCÃ‰DER AU COSMOS", use_container_width=True):
            if pw == "JET2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("âŒ Mot de passe incorrect")
    st.stop()

# ===================== CSS COSMOS =====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600&display=swap');

    .stApp {
        background: radial-gradient(ellipse at 20% 0%, #0d0030 0%, #020210 40%, #00001a 100%);
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }

    /* Stars background */
    .stApp::before {
        content: '';
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-image:
            radial-gradient(1px 1px at 20% 30%, #ffffff44, transparent),
            radial-gradient(1px 1px at 80% 10%, #ffffff33, transparent),
            radial-gradient(1px 1px at 50% 60%, #ffffff22, transparent),
            radial-gradient(1.5px 1.5px at 35% 85%, #00ffcc33, transparent),
            radial-gradient(1px 1px at 65% 45%, #a855f733, transparent);
        pointer-events: none; z-index: 0;
    }

    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.2rem; font-weight: 900; text-align: center;
        background: linear-gradient(90deg, #00ffcc, #a855f7, #00ccff, #00ffcc);
        background-size: 300%;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: gradient-flow 4s ease infinite;
        text-shadow: none; margin-bottom: 0;
    }
    @keyframes gradient-flow {
        0%,100% { background-position: 0%; }
        50%      { background-position: 100%; }
    }

    .subtitle {
        text-align: center; color: #00ffcc88;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.75rem; letter-spacing: 0.4em; margin-bottom: 1.5rem;
    }

    /* Glass cards */
    .glass {
        background: rgba(10, 5, 30, 0.85);
        border: 1px solid rgba(0,255,204,0.25);
        border-radius: 20px; padding: 24px;
        box-shadow: 0 0 40px rgba(0,255,204,0.08), inset 0 1px 0 rgba(255,255,255,0.05);
        backdrop-filter: blur(12px);
    }

    .glass-signal {
        background: rgba(5, 0, 20, 0.92);
        border: 1px solid rgba(168,85,247,0.4);
        border-radius: 20px; padding: 24px;
        box-shadow: 0 0 50px rgba(168,85,247,0.12), 0 0 80px rgba(0,255,204,0.06);
    }

    /* Signal badges */
    .sig-ultra {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.3rem; font-weight: 700;
        color: #00ffcc;
        text-shadow: 0 0 20px #00ffcc, 0 0 40px #00ffcc88;
        letter-spacing: 0.05em;
    }
    .sig-strong {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.2rem; font-weight: 700;
        color: #a855f7;
        text-shadow: 0 0 20px #a855f7, 0 0 40px #a855f788;
    }
    .sig-good {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.1rem; font-weight: 700;
        color: #38bdf8;
        text-shadow: 0 0 15px #38bdf8;
    }

    /* Entry time display */
    .entry-time {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.6rem; font-weight: 900; text-align: center;
        color: #00ffcc;
        text-shadow: 0 0 30px #00ffcc, 0 0 60px #00ffcc44;
        letter-spacing: 0.08em;
        margin: 12px 0;
    }

    /* Metric boxes */
    .metric-min {
        background: linear-gradient(135deg, rgba(0,255,136,0.15), rgba(0,200,100,0.08));
        border: 1px solid rgba(0,255,136,0.4);
        border-radius: 14px; padding: 16px; text-align: center;
    }
    .metric-moy {
        background: linear-gradient(135deg, rgba(255,215,0,0.15), rgba(255,170,0,0.08));
        border: 1px solid rgba(255,215,0,0.4);
        border-radius: 14px; padding: 16px; text-align: center;
    }
    .metric-max {
        background: linear-gradient(135deg, rgba(255,51,102,0.18), rgba(200,0,60,0.08));
        border: 1px solid rgba(255,51,102,0.4);
        border-radius: 14px; padding: 16px; text-align: center;
    }
    .metric-val { font-size: 2rem; font-weight: 700; font-family: 'Orbitron', sans-serif; }
    .metric-lbl { font-size: 0.75rem; color: #ffffff88; letter-spacing: 0.15em; margin-top: 4px; }

    /* Streak badge */
    .streak-hot {
        display: inline-block;
        background: linear-gradient(90deg, #ff6600, #ff0066);
        color: white; border-radius: 20px;
        padding: 4px 14px; font-size: 0.8rem; font-weight: 600;
    }
    .streak-cold {
        display: inline-block;
        background: linear-gradient(90deg, #0066ff, #00ccff);
        color: white; border-radius: 20px;
        padding: 4px 14px; font-size: 0.8rem; font-weight: 600;
    }

    /* Strength bar */
    .strength-track {
        background: rgba(255,255,255,0.07);
        border-radius: 99px; height: 10px; overflow: hidden; margin-top: 6px;
    }
    .strength-fill {
        height: 100%; border-radius: 99px;
        background: linear-gradient(90deg, #a855f7, #00ffcc);
        transition: width 0.8s cubic-bezier(0.4,0,0.2,1);
        box-shadow: 0 0 12px #00ffcc88;
    }

    /* Buttons */
    .stButton>button {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1rem !important; font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        transition: all 0.2s ease !important;
    }

    /* Histogram bars */
    .hist-bar {
        display: inline-block; width: 12px; border-radius: 3px 3px 0 0;
        background: linear-gradient(180deg, #00ffcc, #a855f7);
        vertical-align: bottom; margin: 0 1px;
        transition: height 0.4s ease;
    }

    /* Alert cosmos */
    .alert-cosmos {
        background: rgba(168,85,247,0.12);
        border: 1px solid rgba(168,85,247,0.35);
        border-radius: 12px; padding: 12px 16px;
        font-size: 0.9rem; color: #d4aaff;
        margin-top: 12px;
    }

    /* Section label */
    .sec-lbl {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.65rem; letter-spacing: 0.3em;
        color: #00ffcc66; text-transform: uppercase;
        margin-bottom: 8px;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #020210; }
    ::-webkit-scrollbar-thumb { background: #a855f744; border-radius: 3px; }

    /* Input styling */
    .stTextInput input, .stNumberInput input {
        background: rgba(0,255,204,0.04) !important;
        border: 1px solid rgba(0,255,204,0.2) !important;
        color: #e0fbfc !important;
        border-radius: 12px !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: rgba(0,255,204,0.6) !important;
        box-shadow: 0 0 0 3px rgba(0,255,204,0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# ===================== HELPERS =====================
def get_time():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def get_streak_info(history):
    """Sliding window streak analysis â€” last 10 results"""
    marked = [h.get("real_result") for h in history if h.get("real_result") in ["win", "loss"]]
    if not marked:
        return 0, 0, "neutral", 0

    # Current streak
    last_r = marked[-1]
    streak = 0
    for r in reversed(marked):
        if r == last_r:
            streak += 1
        else:
            break

    # Win rate over last 10
    recent = marked[-10:]
    win_rate = sum(1 for r in recent if r == "win") / len(recent) if recent else 0.5

    # Hot/cold
    if last_r == "win" and streak >= 2:
        mode = "hot"
    elif last_r == "loss" and streak >= 2:
        mode = "cold"
    else:
        mode = "neutral"

    return (streak if last_r == "win" else 0), (streak if last_r == "loss" else 0), mode, win_rate

def get_adaptive_cashout(history, base_min, base_moy, base_max):
    """Compute cashout targets from real history (adaptive)"""
    real_vals = [h.get("real_cote") for h in history if h.get("real_cote") is not None]
    if len(real_vals) < 5:
        return base_min, base_moy, base_max

    arr = np.array(real_vals)
    p10 = float(np.percentile(arr, 10))
    p50 = float(np.median(arr))
    p85 = float(np.percentile(arr, 85))

    # Blend: 60% historical, 40% simulation
    a_min = round(0.6*p10 + 0.4*base_min, 2)
    a_moy = round(0.6*p50 + 0.4*base_moy, 2)
    a_max = round(0.6*p85 + 0.4*base_max, 2)
    return a_min, a_moy, a_max

def build_features(prob_x3, conf, moy, spread, last_cote, win_s, loss_s, volatility, win_rate, streak_mode_val):
    return [prob_x3, conf, moy, spread, last_cote, win_s, loss_s, volatility, win_rate * 100, streak_mode_val]

# ===================== SESSION STATE =====================
defaults = {
    "history": [],
    "last": None,
    "ml_clf": None,
    "ml_reg": None,
    "ml_trained_count": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def get_or_build_models():
    if st.session_state.ml_clf is None:
        st.session_state.ml_clf = Pipeline([
            ("scaler", RobustScaler()),
            ("clf", GradientBoostingClassifier(
                n_estimators=200, max_depth=5,
                learning_rate=0.08, subsample=0.85, random_state=42
            ))
        ])
        st.session_state.ml_reg = Pipeline([
            ("scaler", RobustScaler()),
            ("reg", GradientBoostingRegressor(
                n_estimators=150, max_depth=4,
                learning_rate=0.1, subsample=0.85, random_state=42
            ))
        ])

get_or_build_models()

def try_train_ml(history):
    """Progressive training â€” recalibrate at every labeled result"""
    labeled = [h for h in history if h.get("real_result") in ["win", "loss"] and h.get("features")]
    if len(labeled) < 3:
        return False

    X = np.array([h["features"] for h in labeled])
    y_clf = np.array([1 if h["real_result"] == "win" else 0 for h in labeled])
    y_reg = np.array([h.get("real_cote", h["moy"]) for h in labeled])

    try:
        st.session_state.ml_clf.fit(X, y_clf)
        st.session_state.ml_reg.fit(X, y_reg)
        st.session_state.ml_trained_count = len(labeled)
        return True
    except Exception:
        return False

# ===================== V16.0 COSMOS ENGINE =====================
def run_engine_cosmos(h_in, t_in, last_cote):
    # --- Hash entropy ---
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:48], 16)
    np.random.seed(h_num & 0xFFFFFFFF)

    # --- Simulation 100k ---
    base = 1.97 + (h_num % 1100) / 130
    last_cote_adj = max(1.1, last_cote)
    sigma = 0.22 - (last_cote_adj * 0.0025)
    sims = np.random.lognormal(np.log(base), sigma, 100_000)

    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 1)
    moy      = round(float(np.mean(sims)), 2)
    maxv     = round(float(np.percentile(sims, 97.5)), 2)
    minv     = round(float(np.percentile(sims, 2.5)), 2)
    spread   = round(maxv - minv, 2)

    # --- Streak & win_rate ---
    win_s, loss_s, streak_mode, win_rate = get_streak_info(st.session_state.history)
    streak_mode_val = {"hot": 1, "cold": -1, "neutral": 0}[streak_mode]

    # --- Volatility (dynamic 20-window) ---
    recent_moys = [h.get("moy", 2.5) for h in st.session_state.history[-20:]]
    volatility = round(float(np.std(recent_moys)) if len(recent_moys) >= 3 else 1.2, 2)

    # --- Base confidence ---
    conf = round(max(48, min(99,
        prob_x3 * 0.70 +
        moy * 22.0 +
        (h_num % 220) / 3.5 +
        last_cote_adj * 13.5 +
        win_rate * 15 +
        streak_mode_val * 4
    )), 1)

    # --- Features for ML ---
    features = build_features(prob_x3, conf, moy, spread, last_cote_adj, win_s, loss_s, volatility, win_rate, streak_mode_val)

    # --- AI score (progressive ML) ---
    ai_score = round(conf * 0.92, 1)
    ml_used = False
    if st.session_state.ml_trained_count >= 3:
        try:
            X = np.array(features).reshape(1, -1)
            prob_ml = float(st.session_state.ml_clf.predict_proba(X)[0][1]) * 100
            reg_ml  = float(st.session_state.ml_reg.predict(X)[0])
            ai_score = round(0.65 * prob_ml + 0.25 * reg_ml + 0.10 * conf, 1)
            ml_used = True
        except Exception:
            pass

    # --- Final strength (multi-signal weighted) ---
    strength = round(
        prob_x3 * 0.30 +
        ai_score * 0.30 +
        conf    * 0.20 +
        win_rate * 25 +
        streak_mode_val * 6 -
        volatility * 3.5 +
        (h_num % 80) / 8,
    1)
    strength = max(40.0, min(99.0, strength))

    # --- Adaptive cashout ---
    sim_min, sim_moy, sim_max = minv, moy, maxv
    a_min, a_moy, a_max = get_adaptive_cashout(st.session_state.history, sim_min, sim_moy, sim_max)

    # --- Dynamic entry time ---
    try:
        bt = datetime.combine(get_time().date(), datetime.strptime(t_in.strip(), "%H:%M:%S").time())
    except Exception:
        bt = get_time()

    hash_shift = (int(h_hex[:20], 16) % 80) - 40
    vol_adj    = int(volatility * 5.5)
    str_bonus  = 28 if strength > 88 else 19 if strength > 76 else 12
    streak_adj = 4 if streak_mode == "hot" else -3 if streak_mode == "cold" else 0

    final_sec = max(18, min(99, 18 + (h_num % 55) + hash_shift + vol_adj + str_bonus + streak_adj))
    entry = (bt + timedelta(seconds=final_sec)).strftime("%H:%M:%S")

    # --- Signal classification ---
    if strength > 88:
        signal     = "ðŸ’Ž ULTRA X3+ BUY â€” COSMOS LOCK"
        sig_class  = "sig-ultra"
    elif strength > 76:
        signal     = "ðŸ”¥ STRONG X3 TARGET â€” ENGAGE"
        sig_class  = "sig-strong"
    else:
        signal     = "ðŸŸ¢ GOOD X3 SCALP â€” WATCH"
        sig_class  = "sig-good"

    # --- Histogram data (distribution buckets) ---
    buckets = np.histogram(sims, bins=20, range=(1.0, 8.0))[0]
    hist_data = [int(b) for b in buckets]

    res = {
        "entry": entry, "signal": signal, "sig_class": sig_class,
        "x3_prob": prob_x3, "conf": conf, "ai_score": ai_score,
        "min": a_min, "moy": a_moy, "max": a_max,
        "sim_min": sim_min, "sim_moy": sim_moy, "sim_max": sim_max,
        "strength": strength, "volatility": volatility,
        "win_s": win_s, "loss_s": loss_s,
        "streak_mode": streak_mode, "win_rate": round(win_rate * 100, 1),
        "ml_used": ml_used, "ml_trained": st.session_state.ml_trained_count,
        "hist": hist_data,
        "features": features,
        "real_result": None, "real_cote": None,
    }

    st.session_state.history.append(res)
    if len(st.session_state.history) > 80:
        st.session_state.history.pop(0)

    # Progressive ML retrain after each result (async on next WIN/LOSS click)
    return res

# ===================== HEADER =====================
st.markdown("<div class='main-title'>JETX COSMOS</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>V 1 6 . 0 &nbsp;â€¢&nbsp; U L T R A &nbsp;â€¢&nbsp; C O S M O S &nbsp;â€¢&nbsp; A D A P T I V E &nbsp;â€¢&nbsp; A I</div>", unsafe_allow_html=True)

# ===================== LAYOUT =====================
col_input, col_result = st.columns([1, 2], gap="large")

# â”€â”€â”€ INPUT â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
with col_input:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("<div class='sec-lbl'>â–¸ ParamÃ¨tres du round</div>", unsafe_allow_html=True)

    h_in      = st.text_input("HASH (Provably Fair)", placeholder="Collez le hash complet ici...")
    t_in      = st.text_input("TIME (HH:MM:SS)", placeholder="Ex: 08:18:48")
    last_cote = st.number_input("LAST COTE", value=2.50, step=0.10, format="%.2f", min_value=1.01)

    launch = st.button("ðŸš€ LANCER â€” COSMOS V16.0", use_container_width=True)
    if launch:
        if h_in.strip() and len(t_in.strip()) >= 7:
            with st.spinner("Simulation 100 000x + AI multi-signal..."):
                st.session_state.last = run_engine_cosmos(h_in.strip(), t_in.strip(), float(last_cote))
            st.rerun()
        else:
            st.warning("âš ï¸ Entrez le hash et l'heure avant de lancer.")

    # ML status
    n_trained = st.session_state.ml_trained_count
    if n_trained >= 3:
        st.markdown(f"<div class='alert-cosmos'>ðŸ¤– IA COSMOS active â€” entraÃ®nÃ© sur <b>{n_trained}</b> round(s) rÃ©el(s)</div>", unsafe_allow_html=True)
    else:
        needed = 3 - n_trained
        st.markdown(f"<div class='alert-cosmos'>ðŸ“¡ IA COSMOS â€” encore <b>{needed}</b> rÃ©sultat(s) pour activer le ML adaptatif</div>", unsafe_allow_html=True)

    # Stats rapides
    if st.session_state.history:
        labeled = [h for h in st.session_state.history if h.get("real_result") in ["win","loss"]]
        if labeled:
            w = sum(1 for h in labeled if h["real_result"] == "win")
            st.markdown(f"""
            <div style='margin-top:18px; display:flex; gap:10px; flex-wrap:wrap;'>
                <div style='background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);border-radius:10px;padding:10px 14px;text-align:center;'>
                    <div style='font-size:1.4rem;font-weight:700;color:#00ff88;'>{w}</div>
                    <div style='font-size:0.7rem;color:#ffffff66;'>WINS</div>
                </div>
                <div style='background:rgba(255,51,102,0.1);border:1px solid rgba(255,51,102,0.3);border-radius:10px;padding:10px 14px;text-align:center;'>
                    <div style='font-size:1.4rem;font-weight:700;color:#ff3366;'>{len(labeled)-w}</div>
                    <div style='font-size:0.7rem;color:#ffffff66;'>LOSS</div>
                </div>
                <div style='background:rgba(168,85,247,0.1);border:1px solid rgba(168,85,247,0.3);border-radius:10px;padding:10px 14px;text-align:center;'>
                    <div style='font-size:1.4rem;font-weight:700;color:#c
