import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG & PREMIUM UI ----------------
st.set_page_config(page_title="ANDR-X AI V12.6 ⚡ GOLD TERMINAL", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Share+Tech+Mono&display=swap');

    .stApp {
        background-color: #05050A;
        background-image: radial-gradient(circle at 50% 0%, #002222 0%, #05050A 70%);
        color: #00ffcc;
        font-family: 'Share Tech Mono', monospace;
    }

    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: #00ffcc;
        text-shadow: 0 0 15px rgba(0,255,204,0.5);
        text-align: center;
        letter-spacing: 2px;
    }

    .result-card {
        background: rgba(0, 20, 20, 0.7);
        border: 2px solid #00ffcc;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 0 30px rgba(0,255,204,0.2);
        margin-top: 15px;
        text-align: center;
        backdrop-filter: blur(10px);
    }

    .cote-grid {
        display: flex;
        justify-content: space-around;
        margin: 20px 0;
        gap: 10px;
    }

    .cote-box {
        background: rgba(0,0,0,0.5);
        border: 1px solid rgba(0,255,204,0.3);
        padding: 12px 5px;
        border-radius: 12px;
        width: 32%;
    }

    .cote-box span { font-size: 0.65rem; color: #888; display: block; }
    .cote-box strong { font-size: 1.2rem; font-family: Orbitron; color: #fff; }

    .time-grid {
        display: flex;
        justify-content: space-around;
        margin-top: 20px;
        gap: 8px;
    }

    .time-box {
        background: #001111;
        border: 1px solid rgba(0,255,204,0.4);
        padding: 10px 5px;
        border-radius: 8px;
        text-align: center;
        width: 32%;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "pred_log" not in st.session_state:
    st.session_state.pred_log = []

if "auth" not in st.session_state:
    st.session_state.auth = False

if "ml_model" not in st.session_state:
    st.session_state.ml_model = RandomForestClassifier(n_estimators=150)

if "ml_ready" not in st.session_state:
    st.session_state.ml_ready = False

if "rl_score" not in st.session_state:
    st.session_state.rl_score = {"win": 0, "lose": 0}


# ---------------- RESET ----------------
def reset_history():
    st.session_state.pred_log = []
    st.session_state.rl_score = {"win": 0, "lose": 0}
    st.rerun()


# ---------------- 🔥 ULTRA VARIABLE ENTRY TIME FIX ----------------
def ultra_sync_delay(t_obj, raw_delay, hash_mix, cote):

    server_tick = 6

    t_sec = t_obj.hour * 3600 + t_obj.minute * 60 + t_obj.second

    # HASH ENTROPY LAYERS (NEW)
    h1 = int(hash_mix[0:8], 16) % 20
    h2 = int(hash_mix[8:16], 16) % 15
    h3 = int(hash_mix[16:24], 16) % 10

    phase = (t_sec + h1) % server_tick

    # COTE influence (NEW)
    cote_factor = int((cote * 10) % 7)

    aligned = raw_delay + h1 + h2 + h3 + cote_factor - phase

    # jitter anti-fixed
    if phase >= 4:
        aligned -= 2
    elif phase <= 1:
        aligned += 3

    # ensure variability
    jitter = int((h3 * h2) % 9)
    aligned += jitter

    if aligned < 12:
        aligned += server_tick * 2

    return aligned


# ---------------- ENGINE ----------------
def run_prediction(hash_str, h_act, last_cote):

    try:
        t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except:
        t_obj = datetime.now(pytz.timezone('Indian/Antananarivo'))

    h_hex = hashlib.sha256(hash_str.encode()).hexdigest()
    h_int = int(h_hex[:10], 16)
    np.random.seed(h_int % (2**32))

    base_val = (int(h_hex[10:15], 16) % 100) / 20 + 1.25
    sims = np.random.lognormal(mean=np.log(base_val), sigma=0.38, size=15000)

    prob = round(len([s for s in sims if s >= 2.0]) / 15000 * 100, 1)
    moy = round(np.mean(sims) * (1 + (last_cote / 18)), 2)

    min_v = round(max(1.20, moy * 0.65), 2)
    max_v = round(moy * 1.9, 2)

    confidence = round((prob * moy) / 10, 1)

    # 🔥 ULTRA VARIABLE ENTRY TIME
    delay = ultra_sync_delay(
        t_obj,
        20 + (h_int % 15),
        h_hex,
        last_cote
    )

    e_time = t_obj + timedelta(seconds=delay)

    if confidence > 90:
        sig, emo, col = "ULTRA SNIPER", "🔥", "#ff00cc"
    elif confidence > 65:
        sig, emo, col = "STRONG BUY", "🎯", "#00ffcc"
    else:
        sig, emo, col = "WAITING / SKIP", "⏳", "#ffcc00"

    return {
        "h_ent": e_time.strftime("%H:%M:%S"),
        "h_early": (e_time - timedelta(seconds=2)).strftime("%H:%M:%S"),
        "h_late": (e_time + timedelta(seconds=2)).strftime("%H:%M:%S"),
        "min": min_v,
        "moy": moy,
        "max": max_v,
        "prob": prob,
        "confidence": confidence,
        "signal": sig,
        "emoji": emo,
        "color": col,
        "ref_raw": last_cote,
        "result": None
    }


# ---------------- UI ----------------
if not st.session_state.auth:
    st.title("⚡ ANDR-X LOGIN")
    pwd = st.text_input("ACCESS", type="password")
    if st.button("ACTIVATE"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

st.title("🚀 JET X ANDR V12.6")

h_in = st.text_input("HASH")
t_in = st.text_input("HEURE (HH:MM:SS)")
c_in = st.number_input("COTE REF", value=1.5)

if st.button("RUN"):
    if h_in and t_in:
        res = run_prediction(h_in, t_in, c_in)
        st.session_state.pred_log.append(res)
        st.rerun()

if st.session_state.pred_log:
    r = st.session_state.pred_log[-1]

    st.markdown(f"""
    <div class="result-card">
        <h2>{r['emoji']} {r['signal']}</h2>
        <p>PROB: {r['prob']}% | CONF: {r['confidence']}</p>

        <div class="time-grid">
            <div class="time-box"><b>EARLY</b><br>{r['h_early']}</div>
            <div class="time-box"><b>ENTRY</b><br>{r['h_ent']}</div>
            <div class="time-box"><b>LATE</b><br>{r['h_late']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
