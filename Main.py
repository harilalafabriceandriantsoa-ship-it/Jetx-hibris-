import streamlit as st
import numpy as np
import pandas as pd
import hashlib
import sqlite3
from datetime import datetime, timedelta
import pytz

from sklearn.ensemble import RandomForestClassifier

# ================= CONFIG =================

st.set_page_config(page_title="ANDR-X AI V13 ULTRA FIXED", layout="centered")

st.markdown("""
<style>
.stApp {
    background:#000;
    color:#00ffcc;
    font-family: monospace;
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION =================

if "dataset" not in st.session_state:
    st.session_state.dataset = []

if "history" not in st.session_state:
    st.session_state.history = []

if "time_stats" not in st.session_state:
    st.session_state.time_stats = {}

if "model" not in st.session_state:
    st.session_state.model = RandomForestClassifier(n_estimators=200)

if "trained" not in st.session_state:
    st.session_state.trained = False

# ================= TIME SAFE =================

def safe_time(h):
    try:
        hh, mm, ss = h.split(":")
        hh, mm, ss = int(hh), int(mm), int(ss)

        if mm > 59: mm = 59
        if ss > 59: ss = 59

        return datetime.strptime(f"{hh}:{mm}:{ss}", "%H:%M:%S")

    except:
        tz = pytz.timezone("Indian/Antananarivo")
        return datetime.now(tz)

# ================= HASH =================

def hash_val(x):
    h = hashlib.sha256(x.encode()).hexdigest()
    return int(h[:10],16)/0xFFFFFFFFFF

# ================= FEATURES =================

def build_features(prob, moy, maxv, minv, conf, cote):
    spread = maxv - minv
    stability = 1 / (1 + spread)
    risk = spread * cote
    momentum = (prob * 0.4) + (conf * 0.6)
    score = (moy * 2) + momentum + (stability * 20) - risk
    return [prob, moy, maxv, minv, conf, cote, score]

# ================= ENTRY TIME =================

def entry_time_engine(hash_hex, cote):
    seed = int(hash_hex[:10], 16) % (2**32 - 1)
    np.random.seed(seed)

    micro = seed % 60
    market = int(cote * 6)
    return 20 + ((micro + market) % 45)

# ================= TRAIN =================

def train_model():
    if len(st.session_state.dataset) < 30:
        return

    data = np.array(st.session_state.dataset)

    try:
        X = data[:, :6]
        y = data[:, 6]
    except:
        return

    y = np.array([int(float(v)) for v in y])

    if len(np.unique(y)) < 2:
        return

    model = RandomForestClassifier(n_estimators=300, max_depth=8, random_state=42)
    model.fit(X, y)

    st.session_state.model = model
    st.session_state.trained = True

# ================= AI =================

def ai_predict(features):
    if not st.session_state.trained:
        return None
    try:
        return st.session_state.model.predict_proba([features])[0][1] * 100
    except:
        return None

# ================= ENGINE ULTRA =================

def run_prediction(hash_input, time_input, cote):

    t = safe_time(time_input)
    hash_hex = hashlib.sha256(hash_input.encode()).hexdigest()

    seed = int(hash_hex[:12], 16) % (2**32 - 1)
    np.random.seed(seed)

    base = (int(hash_hex[:8], 16) % 1000) / 100 + 1.1
    sims = np.random.lognormal(np.log(base), 0.25, 10000)

    prob = np.mean(sims >= 3.0) * 100
    prob = round(max(5, min(prob, 90)), 1)

    log_sims = np.log(sims + 1)

    moy = round(np.exp(np.mean(log_sims)) / 1.3, 2)
    maxv = round(np.exp(np.percentile(log_sims, 95)) / 1.2, 2)
    minv = round(np.exp(np.percentile(log_sims, 10)) / 1.4, 2)

    conf = round((prob * moy) / 10, 1)

    features = build_features(prob, moy, maxv, minv, conf, cote)
    ai_score = ai_predict(features)

    label = 1 if prob > 60 else 0
    st.session_state.dataset.append(features + [label])

    train_model()

    entry_seconds = entry_time_engine(hash_hex, cote)
    entry_time = (t + timedelta(seconds=entry_seconds)).strftime("%H:%M:%S")

    hour = t.hour

    if hour not in st.session_state.time_stats:
        st.session_state.time_stats[hour] = {"wins": 0, "total": 0}

    st.session_state.time_stats[hour]["total"] += 1
    if prob > 60:
        st.session_state.time_stats[hour]["wins"] += 1

    spread = maxv - minv

    # ================= SIGNAL ULTRA =================

    if spread > 5:
        signal = "❌ SKIP"

    elif prob < 50:
        signal = "❌ SKIP"

    elif ai_score and ai_score > 75:
        signal = "🔥 ULTRA X3+"

    elif prob > 65 and conf > 15:
        signal = "⚡ STRONG"

    else:
        signal = "⏳ WAIT"

    result = {
        "prob": prob,
        "moy": moy,
        "max": maxv,
        "min": minv,
        "conf": conf,
        "ai": ai_score,
        "signal": signal,
        "entry": entry_time,
        "hour": hour
    }

    st.session_state.history.append(result)
    return result

# ================= RESET SAFE =================

def reset_all():
    st.session_state.dataset = []
    st.session_state.history = []
    st.session_state.time_stats = {}
    st.session_state.trained = False
    st.session_state.model = RandomForestClassifier(n_estimators=200)

# ================= UI =================

st.title("🚀 ANDR-X AI V13 ULTRA FIXED SYSTEM")

h = st.text_input("HASH")
t = st.text_input("TIME (HH:MM:SS)")
c = st.number_input("COTE", value=1.5)

col1, col2 = st.columns(2)

with col1:
    if st.button("RUN"):
        if h:
            st.session_state["last"] = run_prediction(h, t, c)

with col2:
    if st.button("RESET ALL DATA"):
        reset_all()
        st.success("RESET DONE")

# ================= OUTPUT =================

if "last" in st.session_state:
    r = st.session_state["last"]

    st.markdown(f"""
# {r['signal']}

🎯 PROB: {r['prob']}%  
🧠 CONF: {r['conf']}  
🤖 AI: {r['ai']}  

📊 MOY: {r['moy']}  
🚀 MAX: {r['max']}  
📉 MIN: {r['min']}  

⏰ ENTRY: {r['entry']}
""")

# ================= STATS =================

st.sidebar.metric("DATA", len(st.session_state.dataset))
st.sidebar.metric("HISTORY", len(st.session_state.history))
