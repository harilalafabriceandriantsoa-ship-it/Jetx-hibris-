import streamlit as st
import numpy as np
import pandas as pd
import hashlib
from datetime import datetime, timedelta
import pytz
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ================= CONFIG =================

st.set_page_config(page_title="ANDR-X AI SAFE V13", layout="centered")

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

if "model" not in st.session_state:
    st.session_state.model = None

# ================= SAFE TIME =================

def safe_time(t):
    try:
        hh, mm, ss = t.split(":")
        hh, mm, ss = int(hh), int(mm), int(ss)

        mm = min(mm, 59)
        ss = min(ss, 59)

        return datetime.strptime(f"{hh}:{mm}:{ss}", "%H:%M:%S")

    except:
        tz = pytz.timezone("Indian/Antananarivo")
        return datetime.now(tz)

# ================= HASH =================

def hash_val(x):
    h = hashlib.sha256(x.encode()).hexdigest()
    return int(h[:10], 16) / 0xFFFFFFFFFF

# ================= FEATURES =================

def build_features(prob, moy, maxv, minv, conf, cote):
    spread = maxv - minv
    stability = 1 / (1 + spread)
    risk = spread * cote
    score = (moy * 2) + conf + (stability * 10) - risk
    return [prob, moy, maxv, minv, conf, cote, score]

# ================= TRAIN =================

def train_model():
    if len(st.session_state.dataset) < 20:
        return None, None

    data = np.array(st.session_state.dataset)

    X = data[:, :6]
    y = data[:, 6]

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    model = RandomForestClassifier(n_estimators=150, random_state=42)
    model.fit(Xs, y)

    st.session_state.model = model
    return model, scaler

# ================= PREDICT =================

def ai_predict(features):
    if st.session_state.model is None:
        return None

    try:
        return st.session_state.model.predict_proba([features])[0][1] * 100
    except:
        return None

# ================= ENGINE =================

def run(hash_input, time_input, cote):

    t = safe_time(time_input)
    h = hash_val(hash_input)

    np.random.seed(int(h * 100000) % (2**32 - 1))

    base = 1.1 + np.log1p(h * 10)

    sims = np.random.lognormal(np.log(base), 0.3, 5000)

    prob = np.mean(sims >= 3.0) * 100
    prob = round(max(5, min(prob, 90)), 1)

    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 95), 2)
    minv = round(np.percentile(sims, 10), 2)

    conf = round((prob + moy * 10) / 2, 1)

    features = build_features(prob, moy, maxv, minv, conf, cote)

    label = 1 if prob > 60 else 0
    st.session_state.dataset.append(features + [label])

    model, scaler = train_model()

    ai_score = None
    if model:
        ai_score = model.predict_proba([features])[0][1] * 100

    delay = int(10 + (h * 40))
    entry = t + timedelta(seconds=delay)

    # SIGNAL SIMPLE & TRANSPARENT
    if prob > 70 and conf > 70:
        signal = "🔥 STRONG"
    elif prob > 50:
        signal = "⚡ MID"
    else:
        signal = "❌ WEAK"

    return {
        "prob": prob,
        "moy": moy,
        "max": maxv,
        "min": minv,
        "conf": conf,
        "ai": ai_score,
        "signal": signal,
        "entry": entry.strftime("%H:%M:%S")
    }

# ================= UI =================

st.title("ANDR-X AI SAFE SYSTEM")

h = st.text_input("HASH")
t = st.text_input("TIME HH:MM:SS")
c = st.number_input("COTE REF", value=2.0)

if st.button("RUN"):
    if h and t:
        res = run(h, t, c)
        st.session_state["last"] = res

if "last" in st.session_state:
    r = st.session_state["last"]

    st.markdown(f"""
    ### SIGNAL: {r['signal']}

    PROB: {r['prob']}%  
    CONF: {r['conf']}  
    AI: {r['ai']}  

    ENTRY: {r['entry']}  
    """)

st.write("DATA SIZE:", len(st.session_state.dataset))
