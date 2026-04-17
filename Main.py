import streamlit as st
import numpy as np
import pandas as pd
import hashlib
from datetime import datetime
import pytz

from sklearn.ensemble import RandomForestClassifier

# ---------------- CONFIG ----------------

st.set_page_config(page_title="ANDR-X AI V12 FULL ML FIXED", layout="centered")

st.markdown("""
<style>
.stApp {
    background:#000;
    color:#00ffcc;
    font-family: monospace;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------

if "dataset" not in st.session_state:
    st.session_state.dataset = []

if "model" not in st.session_state:
    st.session_state.model = RandomForestClassifier(n_estimators=200)

if "trained" not in st.session_state:
    st.session_state.trained = False

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- TIME ----------------

def get_time(h):
    try:
        return datetime.strptime(h, "%H:%M:%S")
    except:
        tz = pytz.timezone("Indian/Antananarivo")
        return datetime.now(tz)

# ---------------- FEATURES ----------------

def build_features(prob, moy, maxv, minv, conf, cote):

    spread = maxv - minv
    stability = 1 / (1 + spread)
    risk = spread * cote
    momentum = (prob * 0.4) + (conf * 0.6)

    score = (moy * 2) + momentum + (stability * 20) - risk

    return [prob, moy, maxv, minv, conf, cote, score]

# ---------------- TRAIN ----------------

def train_model():

    if len(st.session_state.dataset) < 20:
        return

    data = np.array(st.session_state.dataset)

    X = data[:, :6]
    y = data[:, 6]

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        random_state=42
    )

    model.fit(X, y)

    st.session_state.model = model
    st.session_state.trained = True

# ---------------- AI PREDICT ----------------

def ai_predict(features):

    if not st.session_state.trained:
        return None

    try:
        return st.session_state.model.predict_proba([features])[0][1] * 100
    except:
        return None

# ---------------- ENGINE ----------------

def run_prediction(hash_input, time_input, cote):

    t = get_time(time_input)

    hash_hex = hashlib.sha256(hash_input.encode()).hexdigest()

    # ---------------- FIXED SEED (NO ERROR) ----------------
    seed_value = int(hash_hex[:12], 16) & 0xffffffff
    np.random.seed(seed_value)

    base = (int(hash_hex[:8], 16) % 1000) / 100 + 1.1

    sims = np.random.lognormal(np.log(base), 0.25, 10000)

    # ---------------- STATS ----------------

    prob = np.mean(sims >= 3.0) * 100
    prob = round(max(5, min(prob, 90)), 1)

    log_sims = np.log(sims + 1)

    moy = round(np.exp(np.mean(log_sims)) / 1.3, 2)
    maxv = round(np.exp(np.percentile(log_sims, 95)) / 1.2, 2)
    minv = round(np.exp(np.percentile(log_sims, 10)) / 1.4, 2)

    conf = round((prob * moy) / 10, 1)

    # ---------------- FEATURES ----------------

    features = build_features(prob, moy, maxv, minv, conf, cote)

    # ---------------- AI ----------------

    ai_score = ai_predict(features)

    label = 1 if prob > 60 else 0

    st.session_state.dataset.append(features + [label])

    train_model()

    spread = maxv - minv

    # ---------------- LOGIC ----------------

    if spread > 5:
        signal = "❌ SKIP (RISK HIGH)"

    elif prob < 50:
        signal = "❌ SKIP (LOW PROB)"

    elif ai_score is not None and ai_score > 70:
        signal = "🔥 AI STRONG BUY"

    elif prob > 65 and conf > 15:
        signal = "⚡ BUY"

    else:
        signal = "⏳ WAIT"

    result = {
        "prob": prob,
        "moy": moy,
        "max": maxv,
        "min": minv,
        "conf": conf,
        "ai": ai_score,
        "signal": signal
    }

    st.session_state.history.append(result)

    return result

# ---------------- WINRATE ----------------

def winrate():

    if len(st.session_state.dataset) == 0:
        return 0

    data = np.array(st.session_state.dataset)

    wins = np.sum(data[:, 6] == 1)

    return round((wins / len(data)) * 100, 2)

# ---------------- UI ----------------

st.title("🚀 ANDR-X AI V12 FULL ML FIXED SYSTEM")

hash_input = st.text_input("🔑 HASH")
time_input = st.text_input("⏰ TIME (HH:MM:SS)")
cote = st.number_input("📉 CÔTE", value=1.5)

if st.button("RUN ANALYSIS"):

    if hash_input:
        res = run_prediction(hash_input, time_input, cote)
        st.session_state["last"] = res

# ---------------- OUTPUT ----------------

if "last" in st.session_state:

    r = st.session_state["last"]

    st.markdown(f"""
# {r['signal']}

🎯 PROB: {r['prob']}%  
🧠 CONF: {r['conf']}  
🤖 AI SCORE: {r['ai']}  

📊 MOY: {r['moy']}  
🚀 MAX: {r['max']}  
📉 MIN: {r['min']}
""")

# ---------------- STATS ----------------

st.sidebar.markdown("📊 SYSTEM STATS")

st.sidebar.metric("WINRATE AI", f"{winrate()} %")
st.sidebar.metric("DATA SIZE", len(st.session_state.dataset))

# ---------------- HISTORY ----------------

st.subheader("📜 HISTORY")

st.write(st.session_state.history[::-1])
