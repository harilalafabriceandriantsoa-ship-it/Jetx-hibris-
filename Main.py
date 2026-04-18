import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pytz

from sklearn.ensemble import RandomForestClassifier

# ================= CONFIG =================

st.set_page_config(page_title="ANDR-X AI V13 ULTRA SAFE", layout="centered")

st.markdown("""
<style>
.stApp {
    background:#000;
    color:#00ffcc;
    font-family: monospace;
}
.box {
    padding:15px;
    border:1px solid #00ffcc;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION SAFE INIT =================

if "dataset" not in st.session_state:
    st.session_state.dataset = []

if "history" not in st.session_state:
    st.session_state.history = []

# 🔥 IMPORTANT FIX (DICT ONLY)
if "time_stats" not in st.session_state:
    st.session_state.time_stats = {}

if "model" not in st.session_state:
    st.session_state.model = RandomForestClassifier(n_estimators=200)

if "trained" not in st.session_state:
    st.session_state.trained = False

if "auth" not in st.session_state:
    st.session_state.auth = False

# ================= LOGIN =================

if not st.session_state.auth:

    st.title("🔐 ACCESS SYSTEM")

    pwd = st.text_input("PASSWORD", type="password")

    if st.button("LOGIN"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("WRONG PASSWORD")

    st.stop()

# ================= RESET SYSTEM =================

st.sidebar.title("CONTROL")

if st.sidebar.button("🗑️ RESET DATA"):

    st.session_state.dataset = []
    st.session_state.history = []

    # 🔥 IMPORTANT FIX
    st.session_state.time_stats = {}

    st.session_state.trained = False

    st.success("RESET DONE")
    st.rerun()

# ================= TIME =================

def get_time(t):
    try:
        return datetime.strptime(t, "%H:%M:%S")
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
    momentum = (prob * 0.4) + (conf * 0.6)

    score = (moy * 2) + momentum + (stability * 20) - risk

    return [prob, moy, maxv, minv, conf, cote, score]

# ================= TRAIN =================

def train_model():

    if len(st.session_state.dataset) < 30:
        return

    data = np.array(st.session_state.dataset)

    X = data[:, :6]
    y = data[:, 6]

    try:
        y = np.array([int(float(v)) for v in y])
    except:
        return

    if len(np.unique(y)) < 2:
        return

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        random_state=42
    )

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

# ================= ENGINE =================

def run_prediction(hash_input, time_input, cote):

    t = get_time(time_input)

    h = hash_val(hash_input)

    seed = int(hashlib.sha256(hash_input.encode()).hexdigest()[:12], 16)
    np.random.seed(seed & 0xffffffff)

    base = (seed % 1000) / 100 + 1.1

    sims = np.random.lognormal(np.log(base), 0.25, 8000)

    prob = np.mean(sims >= 3.0) * 100
    prob = round(np.clip(prob, 5, 90), 1)

    log_sims = np.log(sims + 1)

    moy = round(np.exp(np.mean(log_sims)) / 1.3, 2)
    maxv = round(np.exp(np.percentile(log_sims, 95)) / 1.2, 2)
    minv = round(np.exp(np.percentile(log_sims, 10)) / 1.4, 2)

    spread = round(maxv - minv, 2)

    conf = round((prob * 0.6) + (moy * 20) - (spread * 2), 1)
    conf = max(5, min(conf, 95))

    features = build_features(prob, moy, maxv, minv, conf, cote)

    ai_score = ai_predict(features)

    label = 1 if prob > 60 else 0

    st.session_state.dataset.append(features + [label])

    train_model()

    # ================= ENTRY =================

    entry_seconds = int(10 + (spread * 4))
    entry_seconds = max(8, min(90, entry_seconds))

    entry_time = (t + timedelta(seconds=entry_seconds)).strftime("%H:%M:%S")

    # ================= TIME STATS SAFE =================

    hour = t.hour

    if hour not in st.session_state.time_stats:
        st.session_state.time_stats[hour] = {"wins": 0, "total": 0}

    st.session_state.time_stats[hour]["total"] += 1

    if prob > 60:
        st.session_state.time_stats[hour]["wins"] += 1

    # ================= SIGNAL =================

    if ai_score is not None and ai_score >= 75 and prob >= 65:
        signal = "🔥 ULTRA ENTRY"

    elif prob >= 70 and spread <= 3.5:
        signal = "🟢 STRONG ENTRY"

    elif prob >= 55:
        signal = "⚡ ENTRY"

    elif spread > 6:
        signal = "❌ RISK"

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
        "entry_time": entry_time,
        "hour": hour,
        "spread": spread
    }

    st.session_state.history.append(result)

    return result

# ================= WINRATE =================

def winrate():

    if len(st.session_state.dataset) == 0:
        return 0

    data = np.array(st.session_state.dataset)

    return round(np.mean(data[:, 6]) * 100, 2)

# ================= BEST HOURS SAFE =================

def best_hours():

    stats = st.session_state.time_stats

    # 🔥 SAFE CHECK
    if not isinstance(stats, dict):
        return []

    result = []

    for h, v in stats.items():

        wins = v.get("wins", 0)
        total = v.get("total", 0)

        wr = (wins / total) * 100 if total > 0 else 0

        result.append((h, wr, total))

    return sorted(result, key=lambda x: x[1], reverse=True)

# ================= UI =================

st.title("🚀 ANDR-X AI V13 ULTRA SAFE")

hash_input = st.text_input("HASH")
time_input = st.text_input("TIME")
cote = st.number_input("COTE", value=1.5)

if st.button("RUN ANALYSIS"):
    if hash_input:
        st.session_state.last = run_prediction(hash_input, time_input, cote)

# ================= OUTPUT =================

if "last" in st.session_state:

    r = st.session_state.last

    st.markdown(f"""
<div class="box">

### {r['signal']}

PROB: {r['prob']}%  
CONF: {r['conf']}  
AI: {r['ai']}  

MOY: {r['moy']}  
MAX: {r['max']}  
MIN: {r['min']}  

SPREAD: {r['spread']}  

ENTRY: {r['entry_time']}

</div>
""", unsafe_allow_html=True)

# ================= STATS =================

st.sidebar.metric("WINRATE", f"{winrate()} %")
st.sidebar.metric("DATA", len(st.session_state.dataset))

st.subheader("📊 BEST HOURS")

for h, wr, total in best_hours()[:5]:
    st.write(f"{h}h → {round(wr,2)}% | {total}")
