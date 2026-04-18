import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pytz

from sklearn.ensemble import RandomForestClassifier

# ================= CONFIG =================

st.set_page_config(page_title="ANDR-X AI V13 ULTRA FIX", layout="centered")

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

# ================= AI PREDICT =================

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

    # ================= ENTRY TIME =================

    entry_seconds = int(10 + (spread * 4) + abs(maxv - moy) * 3 + (prob * 0.2))
    entry_seconds = max(8, min(90, entry_seconds))

    entry_time = (t + timedelta(seconds=entry_seconds)).strftime("%H:%M:%S")

    # ================= TIME STATS =================

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

    elif prob >= 55 and conf >= 60:
        signal = "⚡ MODERATE ENTRY"

    elif spread > 6:
        signal = "❌ HIGH RISK"

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
        "spread": spread   # ✅ FIX IMPORTANT (NO KEY ERROR)
    }

    st.session_state.history.append(result)

    return result

# ================= WINRATE =================

def winrate():

    if len(st.session_state.dataset) == 0:
        return 0

    data = np.array(st.session_state.dataset)

    return round(np.mean(data[:, 6]) * 100, 2)

# ================= BEST HOURS =================

def best_hours():

    stats = st.session_state.time_stats

    result = []

    for h, v in stats.items():
        wr = (v["wins"] / v["total"]) * 100 if v["total"] else 0
        result.append((h, wr, v["total"]))

    return sorted(result, key=lambda x: x[1], reverse=True)

# ================= UI =================

st.title("🚀 ANDR-X AI V13 ULTRA FIXED")

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
