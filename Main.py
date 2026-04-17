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
    }
    .result-card {
        background: rgba(0, 20, 20, 0.7);
        border: 2px solid #00ffcc;
        border-radius: 20px;
        padding: 25px;
        text-align: center;
    }
    .cote-grid {
        display: flex;
        justify-content: space-around;
        margin: 20px 0;
    }
    .cote-box {
        background: rgba(0,0,0,0.5);
        padding: 12px;
        border-radius: 12px;
        width: 32%;
        border: 1px solid rgba(0,255,204,0.3);
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

# ---------------- LOGIN ----------------
if not st.session_state.auth:
    st.title("⚡ ANDR-X AI V12.6 LOGIN")
    pwd = st.text_input("🔐 ACCESS CODE", type="password")
    if st.button("ACTIVATE"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# ---------------- AI TRAIN ----------------
def train_ai():
    data = []
    for h in st.session_state.pred_log:
        if h.get("result") is not None:
            data.append([
                h["prob"], h["moy"], h["max"], float(h["ref_raw"]), h["confidence"],
                1 if h["result"] == "win" else 0
            ])

    if len(data) < 5:
        return

    df = pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"])
    X = df.drop("label", axis=1)
    y = df["label"]

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    model = RandomForestClassifier(n_estimators=150)
    model.fit(Xs, y)

    st.session_state.ml_model = model
    st.session_state.scaler = scaler
    st.session_state.ml_ready = True

# ---------------- ENGINE ----------------
def run_prediction(hash_str, h_act, last_cote):

    tz = pytz.timezone('Indian/Antananarivo')

    try:
        t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except:
        t_obj = datetime.now(tz)

    h_hex = hashlib.sha256(hash_str.encode()).hexdigest()
    h_int = int(h_hex[:12], 16)

    np.random.seed(h_int % (2**32))

    base_val = (int(h_hex[10:15], 16) % 100) / 20 + 1.25

    sims = np.random.lognormal(mean=np.log(base_val), sigma=0.35, size=15000)

    prob = round(len([s for s in sims if s >= 2.0]) / 15000 * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 95), 2)
    minv = round(moy * 0.6, 2)

    confidence = round((prob * moy) / 10, 1)

    # ---------------- ULTRA VARIABLE ENTRY WINDOW ----------------
    hash_time = int(h_hex[8:16], 16)

    base_delay = (
        (hash_time % 40) +
        (int(last_cote * 3) % 12) +
        (int(base_val * 5) % 9)
    )

    # 🔥 VARIABLE JITTER (IMPORTANT)
    jitter = np.random.randint(-7, 8)

    raw_delay = base_delay + jitter

    # safety clamp
    raw_delay = max(10, min(85, raw_delay))

    entry_center = t_obj + timedelta(seconds=raw_delay)

    entry_start = entry_center - timedelta(seconds=5)
    entry_end = entry_center + timedelta(seconds=7)

    # SIGNAL
    if confidence > 85 and moy > 2.5:
        signal = "🔥 ULTRA SNIPER"
        emoji = "🔥"
    elif confidence > 65:
        signal = "🟢 STRONG ENTRY"
        emoji = "🎯"
    elif confidence > 45:
        signal = "🟡 WAIT"
        emoji = "⏳"
    else:
        signal = "🔴 NO ENTRY"
        emoji = "❌"

    return {
        "h_ent": entry_center.strftime("%H:%M:%S"),
        "h_window": f"{entry_start.strftime('%H:%M:%S')} → {entry_end.strftime('%H:%M:%S')}",
        "prob": prob,
        "moy": moy,
        "max": maxv,
        "min": minv,
        "confidence": confidence,
        "signal": signal,
        "emoji": emoji,
        "ref_raw": last_cote,
        "result": None
    }

# ---------------- UI ----------------
st.title("🚀 ANDR-X AI V12.6 GOLD TERMINAL")

h_in = st.text_input("🔑 HASH")
t_in = st.text_input("⏰ TIME (HH:MM:SS)")
c_in = st.number_input("📉 LAST COTE", value=1.5)

if st.button("RUN"):
    if h_in and t_in:
        r = run_prediction(h_in, t_in, c_in)
        st.session_state.pred_log.append(r)
        train_ai()
        st.rerun()

if st.session_state.pred_log:
    r = st.session_state.pred_log[-1]

    st.markdown(f"""
    <div class="result-card">
        <h2>{r['emoji']} {r['signal']}</h2>
        <p>PROB: {r['prob']}% | CONF: {r['confidence']}</p>
        <h3>ENTRY: {r['h_ent']}</h3>
        <p style="color:#ff00cc;">WINDOW: {r['h_window']}</p>

        <div class="cote-grid">
            <div class="cote-box">MIN<br>{r['min']}x</div>
            <div class="cote-box">MOY<br>{r['moy']}x</div>
            <div class="cote-box">MAX<br>{r['max']}x</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("⚡ ANDR-X V12.6 ACTIVE")
