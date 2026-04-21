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
        pw = st.text_input("🔑 Mot de passe", type="password", placeholder="Entrez le code d'accès...")
        if st.button("✅ ACCÉDER AU COSMOS", use_container_width=True):
            if pw == "JET2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Mot de passe incorrect")
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

    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.2rem; font-weight: 900; text-align: center;
        background: linear-gradient(90deg, #00ffcc, #a855f7, #00ccff, #00ffcc);
        background-size: 300%;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: gradient-flow 4s ease infinite;
        margin-bottom: 0;
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

    .glass {
        background: rgba(10, 5, 30, 0.85);
        border: 1px solid rgba(0,255,204,0.25);
        border-radius: 20px; padding: 24px;
        backdrop-filter: blur(12px);
    }

    .glass-signal {
        background: rgba(5, 0, 20, 0.92);
        border: 1px solid rgba(168,85,247,0.4);
        border-radius: 20px; padding: 24px;
        box-shadow: 0 0 50px rgba(168,85,247,0.12);
    }

    .sig-ultra { font-family: 'Orbitron', sans-serif; font-size: 1.3rem; color: #00ffcc; text-shadow: 0 0 20px #00ffcc; }
    .sig-strong { font-family: 'Orbitron', sans-serif; font-size: 1.2rem; color: #a855f7; text-shadow: 0 0 20px #a855f7; }
    .sig-good { font-family: 'Orbitron', sans-serif; font-size: 1.1rem; color: #38bdf8; text-shadow: 0 0 15px #38bdf8; }

    .entry-time {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.6rem; font-weight: 900; text-align: center;
        color: #00ffcc; text-shadow: 0 0 30px #00ffcc;
        margin: 12px 0;
    }

    .metric-min { background: rgba(0,255,136,0.1); border: 1px solid rgba(0,255,136,0.4); border-radius: 14px; padding: 16px; text-align: center; }
    .metric-moy { background: rgba(255,215,0,0.1); border: 1px solid rgba(255,215,0,0.4); border-radius: 14px; padding: 16px; text-align: center; }
    .metric-max { background: rgba(255,51,102,0.1); border: 1px solid rgba(255,51,102,0.4); border-radius: 14px; padding: 16px; text-align: center; }
    
    .metric-val { font-size: 2rem; font-weight: 700; font-family: 'Orbitron', sans-serif; }
    .metric-lbl { font-size: 0.75rem; color: #ffffff88; }

    .strength-track { background: rgba(255,255,255,0.07); border-radius: 99px; height: 10px; overflow: hidden; margin-top: 6px; }
    .strength-fill { height: 100%; background: linear-gradient(90deg, #a855f7, #00ffcc); transition: width 0.8s ease; }

    .alert-cosmos { background: rgba(168,85,247,0.12); border: 1px solid rgba(168,85,247,0.35); border-radius: 12px; padding: 12px; font-size: 0.9rem; color: #d4aaff; margin-top: 12px; }
    .sec-lbl { font-family: 'Orbitron', sans-serif; font-size: 0.65rem; color: #00ffcc66; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# ===================== HELPERS =====================
def get_time():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def get_streak_info(history):
    marked = [h.get("real_result") for h in history if h.get("real_result") in ["win", "loss"]]
    if not marked: return 0, 0, "neutral", 0.5
    last_r = marked[-1]
    streak = 0
    for r in reversed(marked):
        if r == last_r: streak += 1
        else: break
    recent = marked[-10:]
    win_rate = sum(1 for r in recent if r == "win") / len(recent) if recent else 0.5
    mode = "hot" if (last_r == "win" and streak >= 2) else "cold" if (last_r == "loss" and streak >= 2) else "neutral"
    return (streak if last_r == "win" else 0), (streak if last_r == "loss" else 0), mode, win_rate

def get_adaptive_cashout(history, base_min, base_moy, base_max):
    real_vals = [h.get("real_cote") for h in history if h.get("real_cote") is not None]
    if len(real_vals) < 5: return base_min, base_moy, base_max
    arr = np.array(real_vals)
    return round(0.6*np.percentile(arr, 10) + 0.4*base_min, 2), round(0.6*np.median(arr) + 0.4*base_moy, 2), round(0.6*np.percentile(arr, 85) + 0.4*base_max, 2)

# ===================== SESSION STATE =====================
if "history" not in st.session_state: st.session_state.history = []
if "last" not in st.session_state: st.session_state.last = None
if "ml_clf" not in st.session_state:
    st.session_state.ml_clf = Pipeline([("scaler", RobustScaler()), ("clf", GradientBoostingClassifier(n_estimators=200, random_state=42))])
    st.session_state.ml_reg = Pipeline([("scaler", RobustScaler()), ("reg", GradientBoostingRegressor(n_estimators=150, random_state=42))])
if "ml_trained_count" not in st.session_state: st.session_state.ml_trained_count = 0

def try_train_ml(history):
    labeled = [h for h in history if h.get("real_result") in ["win", "loss"] and "features" in h]
    if len(labeled) < 3: return False
    X = np.array([h["features"] for h in labeled])
    y_clf = np.array([1 if h["real_result"] == "win" else 0 for h in labeled])
    y_reg = np.array([h.get("real_cote", h["moy_val"]) for h in labeled])
    try:
        st.session_state.ml_clf.fit(X, y_clf)
        st.session_state.ml_reg.fit(X, y_reg)
        st.session_state.ml_trained_count = len(labeled)
        return True
    except: return False

# ===================== ENGINE COSMOS =====================
def run_engine_cosmos(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:48], 16)
    np.random.seed(h_num & 0xFFFFFFFF)

    base = 1.97 + (h_num % 1100) / 130
    sigma = 0.22 - (max(1.1, last_cote) * 0.0025)
    sims = np.random.lognormal(np.log(base), sigma, 100_000)

    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 1)
    moy, maxv, minv = round(float(np.mean(sims)), 2), round(float(np.percentile(sims, 97.5)), 2), round(float(np.percentile(sims, 2.5)), 2)
    win_s, loss_s, mode, win_rate = get_streak_info(st.session_state.history)
    mode_val = {"hot": 1, "cold": -1, "neutral": 0}[mode]
    
    volatility = round(float(np.std([h.get("moy_val", 2.5) for h in st.session_state.history[-20:]])) if len(st.session_state.history) >= 3 else 1.2, 2)
    conf = round(max(48, min(99, prob_x3*0.7 + moy*22 + (h_num%220)/3.5 + last_cote*13.5 + win_rate*15 + mode_val*4)), 1)
    
    features = [prob_x3, conf, moy, maxv-minv, last_cote, win_s, loss_s, volatility, win_rate*100, mode_val]
    ai_score = round(conf * 0.92, 1)
    if st.session_state.ml_trained_count >= 3:
        try:
            X_in = np.array(features).reshape(1, -1)
            ai_score = round(0.65*st.session_state.ml_clf.predict_proba(X_in)[0][1]*100 + 0.35*conf, 1)
        except: pass

    strength = max(40, min(99, prob_x3*0.3 + ai_score*0.3 + conf*0.2 + win_rate*25 + mode_val*6))
    a_min, a_moy, a_max = get_adaptive_cashout(st.session_state.history, minv, moy, maxv)

    try: bt = datetime.combine(get_time().date(), datetime.strptime(t_in.strip(), "%H:%M:%S").time())
    except: bt = get_time()
    
    f_sec = max(18, min(99, 18 + (h_num%55) + (int(h_hex[:20],16)%80-40) + int(volatility*5.5) + (28 if strength>88 else 12)))
    res = {
        "entry": (bt + timedelta(seconds=f_sec)).strftime("%H:%M:%S"),
        "signal": "💎 ULTRA LOCK" if strength > 88 else "🔥 STRONG TARGET" if strength > 76 else "🟢 GOOD WATCH",
        "sig_class": "sig-ultra" if strength > 88 else "sig-strong" if strength > 76 else "sig-good",
        "x3_prob": prob_x3, "conf": conf, "ai_score": ai_score, "min": a_min, "moy": a_moy, "max": a_max,
        "strength": strength, "win_rate": round(win_rate*100, 1), "features": features, "real_result": None, "moy_val": moy
    }
    st.session_state.history.append(res)
    return res

# ===================== INTERFACE =====================
st.markdown("<div class='main-title'>JETX COSMOS</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>V 1 6 . 0 • ULTRA COSMOS • ADAPTIVE AI</div>", unsafe_allow_html=True)

col_input, col_result = st.columns([1, 2], gap="large")

with col_input:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    h_in = st.text_input("HASH", placeholder="Hash complet...")
    t_in = st.text_input("TIME", placeholder="HH:MM:SS")
    last_cote = st.number_input("LAST COTE", value=2.50, step=0.1)
    if st.button("🚀 LANCER COSMOS", use_container_width=True):
        if h_in and t_in:
            st.session_state.last = run_engine_cosmos(h_in, t_in, last_cote)
            st.rerun()
    
    n_t = st.session_state.ml_trained_count
    st.markdown(f"<div class='alert-cosmos'>{'🤖 IA Active: ' + str(n_t) + ' rounds' if n_t >= 3 else '📡 IA: En attente de ' + str(3-n_t) + ' rounds'}</div>", unsafe_allow_html=True)
    
    if st.session_state.history:
        labeled = [h for h in st.session_state.history if h["real_result"]]
        if labeled:
            w = sum(1 for h in labeled if h["real_result"]=="win")
            wr = round(w/len(labeled)*100, 1)
            st.markdown(f"""
            <div style='display:flex; gap:10px; margin-top:15px;'>
                <div style='flex:1; background:rgba(0,255,136,0.1); padding:10px; border-radius:10px; text-align:center;'>
                    <b style='color:#00ff88; font-size:1.2rem;'>{w}</b><br><small>WINS</small>
                </div>
                <div style='flex:1; background:rgba(168,85,247,0.1); padding:10px; border-radius:10px; text-align:center;'>
                    <b style='color:#a855f7; font-size:1.2rem;'>{wr}%</b><br><small>RATE</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_result:
    if st.session_state.last:
        r = st.session_state.last
        st.markdown(f"""
        <div class="glass-signal">
            <div class="sec-lbl">▸ Signal Détécté</div>
            <div class="{r['sig_class']}">{r['signal']}</div>
            <div class="entry-time">{r['entry']}</div>
            <div style="display:flex; justify-content:space-between; font-size:0.9rem;">
                <span>STRENGTH: {r['strength']}%</span>
                <span>WIN RATE: {r['win_rate']}%</span>
            </div>
            <div class="strength-track"><div class="strength-fill" style="width:{r['strength']}%"></div></div>
        </div>
        """, unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f'<div class="metric-min"><div class="metric-val" style="color:#00ff88;">{r["min"]}</div><div class="metric-lbl">SAFE</div></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="metric-moy"><div class="metric-val" style="color:#ffd700;">{r["moy"]}</div><div class="metric-lbl">MOYEN</div></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="metric-max"><div class="metric-val" style="color:#ff3366;">{r["max"]}</div><div class="metric-lbl">ULTRA</div></div>', unsafe_allow_html=True)

        v1, v2 = st.columns(2)
        if v1.button("✅ WIN", use_container_width=True):
            st.session_state.history[-1]["real_result"] = "win"
            try_train_ml(st.session_state.history)
            st.rerun()
        if v2.button("❌ LOSS", use_container_width=True):
            st.session_state.history[-1]["real_result"] = "loss"
            try_train_ml(st.session_state.history)
            st.rerun()

st.markdown("---")
if st.session_state.history:
    st.markdown("### 📜 Historique des Signaux")
    st.dataframe(pd.DataFrame(st.session_state.history)[::-1], use_container_width=True)
