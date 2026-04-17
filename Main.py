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
    text-align: center;
}
.result-card {
    background: rgba(0, 20, 20, 0.7);
    border: 2px solid #00ffcc;
    border-radius: 20px;
    padding: 25px;
}
.cote-grid {display:flex;justify-content:space-around;margin:20px 0;}
.cote-box {background:#000;padding:10px;border-radius:10px;width:32%;}
.time-grid {display:flex;justify-content:space-around;margin-top:15px;}
.time-box {background:#001111;padding:10px;border-radius:10px;width:32%;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "pred_log" not in st.session_state: st.session_state.pred_log = []
if "auth" not in st.session_state: st.session_state.auth = False
if "ml_model" not in st.session_state: st.session_state.ml_model = RandomForestClassifier(n_estimators=150)
if "ml_ready" not in st.session_state: st.session_state.ml_ready = False
if "rl_score" not in st.session_state: st.session_state.rl_score = {"win": 0, "lose": 0}

# ---------------- RESET ----------------
def reset_history():
    st.session_state.pred_log = []
    st.session_state.rl_score = {"win": 0, "lose": 0}
    st.rerun()

# ---------------- ULTRA SYNC ENGINE (FIXED) ----------------
def ultra_sync_delay(t_obj, hash_str, last_cote):

    h = hashlib.sha256((hash_str + str(last_cote)).encode()).hexdigest()

    # multi-layer entropy
    a = int(h[0:10], 16)
    b = int(h[10:20], 16)
    c = int(h[20:30], 16)

    base = (a % 25) + (b % 15) + (c % 10)

    # cote influence (IMPORTANT FIX)
    cote_factor = 1.0
    if last_cote < 1.5:
        cote_factor = 1.8
    elif last_cote < 2.5:
        cote_factor = 1.2
    else:
        cote_factor = 0.9

    sec = t_obj.hour*3600 + t_obj.minute*60 + t_obj.second

    # dynamic phase sync
    phase = (sec % 60) / 60

    jitter = int((a % 7) + (b % 5))

    delay = int((base * cote_factor) + (phase * 20) + jitter)

    # anti too close fix
    if delay < 15:
        delay += 18
    if delay > 90:
        delay = 60 + (delay % 20)

    return delay

# ---------------- ENGINE ----------------
def run_prediction(hash_str, h_act, last_cote):

    tz = pytz.timezone('Indian/Antananarivo')

    try:
        t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except:
        t_obj = datetime.now(tz)

    h_hex = hashlib.sha256(hash_str.encode()).hexdigest()

    seed = int(h_hex[:12], 16)
    np.random.seed(seed % (2**32))

    base = (int(h_hex[10:15], 16) % 100) / 18 + 1.2

    sims = np.random.lognormal(mean=np.log(base), sigma=0.35, size=15000)

    prob = round(len([x for x in sims if x >= 2.0]) / 15000 * 100, 1)
    moy = round(np.mean(sims), 2)

    maxv = round(np.percentile(sims, 95), 2)
    minv = round(max(1.2, moy * 0.6), 2)

    confidence = round((prob * moy) / 10, 1)

    # 🔥 FIXED ENTRY TIME (ULTRA VARIABLE)
    delay = ultra_sync_delay(t_obj, hash_str, last_cote)

    entry = t_obj + timedelta(seconds=delay)

    window = 4 + int((seed % 6))  # dynamic window

    early = entry - timedelta(seconds=window)
    late = entry + timedelta(seconds=window)

    # SIGNAL LOGIC
    if confidence > 85 and moy > 2.4:
        sig = "🔥 ULTRA ENTRY"
    elif confidence > 65:
        sig = "🟢 STRONG ENTRY"
    elif confidence > 45:
        sig = "🟡 WAIT"
    else:
        sig = "🔴 NO ENTRY"

    return {
        "h_ent": entry.strftime("%H:%M:%S"),
        "h_early": early.strftime("%H:%M:%S"),
        "h_late": late.strftime("%H:%M:%S"),
        "h_window": f"{window}s",
        "min": minv,
        "moy": moy,
        "max": maxv,
        "prob": prob,
        "confidence": confidence,
        "signal": sig,
        "ref_raw": last_cote,
        "result": None
    }

# ---------------- AUTH ----------------
if not st.session_state.auth:
    st.title("⚡ ANDR-X LOGIN")
    pwd = st.text_input("ACCESS", type="password")
    if st.button("ENTER"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

st.title("🚀 V12.6 ULTRA SYNC FIX")

# ---------------- INPUT ----------------
h = st.text_input("HASH")
t = st.text_input("HEURE (HH:MM:SS)")
c = st.number_input("COTE REF", value=1.5)

if st.button("RUN"):
    if h and t:
        r = run_prediction(h, t, c)
        st.session_state.pred_log.append(r)
        st.rerun()

if st.session_state.pred_log:
    r = st.session_state.pred_log[-1]

    st.markdown(f"""
    <div class="result-card">
        <h2>{r['signal']}</h2>
        <p>PROB: {r['prob']}% | CONF: {r['confidence']} | WINDOW: {r['h_window']}</p>

        <h3>ENTRY: {r['h_ent']}</h3>
        <h4>{r['h_early']} → {r['h_late']}</h4>

        <div class="cote-grid">
            <div class="cote-box">MIN<br>{r['min']}</div>
            <div class="cote-box">MOY<br>{r['moy']}</div>
            <div class="cote-box">MAX<br>{r['max']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
