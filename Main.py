import streamlit as st
import numpy as np
import pandas as pd
import hashlib
from datetime import datetime, timedelta
import pytz

from sklearn.ensemble import RandomForestClassifier

# ================= CONFIG =================

st.set_page_config(page_title="ANDR-X AI V13 ULTRA", layout="centered")

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
    st.session_state.model = RandomForestClassifier(n_estimators=300)

if "trained" not in st.session_state:
    st.session_state.trained = False

# ================= TIME =================

def get_time(h):
    try:
        return datetime.strptime(h, "%H:%M:%S")
    except:
        tz = pytz.timezone("Indian/Antananarivo")
        return datetime.now(tz)

# ================= HASH =================

def hash_val(x):
    h = hashlib.sha256(x.encode()).hexdigest()
    return int(h[:10], 16) / 0xFFFFFFFFFF

# ================= FEATURES =================

def build_features(prob, moy, maxv, minv, conf, cote_ref):

    spread = maxv - minv
    stability = 1 / (1 + spread)
    risk = spread * cote_ref
    momentum = (prob * 0.4) + (conf * 0.6)

    score = (moy * 2) + momentum + (stability * 20) - risk

    return [prob, moy, maxv, minv, conf, cote_ref, score]

# ================= ENTRY ENGINE =================

def entry_engine(entropy, volatility, cote_ref):

    delay = int(
        8 +
        (entropy * 35) +
        (volatility * 20) +
        (cote_ref * 3)
    )

    return max(5, min(delay, 75))

# ================= TRAIN MODEL =================

def train_model():

    if len(st.session_state.dataset) < 30:
        return

    data = np.array(st.session_state.dataset)

    X = data[:, :7]
    y = data[:, 7]

    y = np.array([int(v) for v in y])

    if len(np.unique(y)) < 2:
        return

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=10,
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

# ================= CORE ENGINE =================

def run_prediction(hash_input, time_input, cote_ref):

    t = get_time(time_input)

    h = hash_val(hash_input)

    hash_hex = hashlib.sha256(hash_input.encode()).hexdigest()

    seed = int(hash_hex[:12], 16)

    entropy = (seed % 1000) / 1000

    np.random.seed(seed)

    # ================= SIMULATION =================

    sims1 = np.random.lognormal(np.log(1.2 + entropy), 0.35, 8000)
    sims2 = np.random.gamma(2.2, 1.1 + entropy, 8000)

    sims = (sims1 * 0.6) + (sims2 * 0.4)

    prob = np.mean(sims >= 2.5) * 100
    prob = round(max(3, min(prob, 92)), 1)

    moy = np.mean(sims)
    maxv = np.percentile(sims, 95)
    minv = np.percentile(sims, 10)

    spread = maxv - minv
    volatility = spread / (moy + 0.001)

    conf = (prob * 0.55) + (moy * 10) - (volatility * 25)
    conf = round(max(5, min(conf, 99)), 1)

    # ================= FEATURES =================

    features = build_features(prob, moy, maxv, minv, conf, cote_ref)

    ai_score = ai_predict(features)

    label = 1 if (prob > 60 and volatility < 0.8) else 0

    st.session_state.dataset.append(features + [label])

    train_model()

    # ================= ENTRY TIME =================

    entry_seconds = entry_engine(entropy, volatility, cote_ref)

    entry_time = (t + timedelta(seconds=entry_seconds)).strftime("%H:%M:%S")

    # ================= TIME STATS =================

    hour = t.hour

    if hour not in st.session_state.time_stats:
        st.session_state.time_stats[hour] = {"wins": 0, "total": 0}

    st.session_state.time_stats[hour]["total"] += 1

    if prob > 60:
        st.session_state.time_stats[hour]["wins"] += 1

    # ================= SIGNAL =================

    trend = moy - minv

    if prob < 45 or volatility > 1.0:
        signal = "❌ SKIP (HIGH RISK)"

    elif conf >= 80 and prob >= 65 and trend > 0.8:
        signal = "🔥 ULTRA X3+ ZONE"

    elif conf >= 65 and prob >= 55:
        signal = "🟢 STRONG ENTRY"

    elif conf >= 45:
        signal = "🟡 WAIT CONFIRMATION"

    else:
        signal = "❌ NO ENTRY"

    result = {
        "prob": prob,
        "moy": round(moy, 2),
        "max": round(maxv, 2),
        "min": round(minv, 2),
        "conf": conf,
        "ai": ai_score,
        "signal": signal,
        "entry_time": entry_time,
        "volatility": round(volatility, 2),
        "ref": cote_ref
    }

    st.session_state.history.append(result)

    return result

# ================= WINRATE =================

def winrate():

    if len(st.session_state.dataset) == 0:
        return 0

    data = np.array(st.session_state.dataset)

    wins = np.sum(data[:, 7] == 1)

    return round((wins / len(data)) * 100, 2)

# ================= BEST HOURS =================

def best_hours():

    stats = st.session_state.time_stats

    result = []

    for h, v in stats.items():
        wr = (v["wins"] / v["total"]) * 100 if v["total"] > 0 else 0
        result.append((h, wr, v["total"]))

    return sorted(result, key=lambda x: x[1], reverse=True)

# ================= UI =================

st.title("🚀 ANDR-X AI V13 ULTRA FINAL")

hash_input = st.text_input("🔑 HASH")
time_input = st.text_input("⏰ TIME (HH:MM:SS)")
cote_ref = st.number_input("📉 COTE REF", value=2.0)

if st.button("RUN ANALYSIS"):
    if hash_input:
        st.session_state["last"] = run_prediction(hash_input, time_input, cote_ref)

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

⚡ VOL: {r['volatility']}  
📌 REF: {r['ref']}  
⏰ ENTRY: {r['entry_time']}
""")

# ================= STATS =================

st.sidebar.metric("WINRATE", f"{winrate()} %")
st.sidebar.metric("DATA", len(st.session_state.dataset))

# ================= TIME ANALYSIS =================

st.subheader("📊 TIME PERFORMANCE")

for h, v in sorted(st.session_state.time_stats.items()):
    wr = (v["wins"] / v["total"]) * 100 if v["total"] else 0
    st.write(f"{h}h → {round(wr,2)}% ({v['total']})")

# ================= BEST HOURS =================

st.subheader("🔥 BEST HOURS")

for h, wr, total in best_hours()[:5]:
    st.write(f"⏰ {h}h → {round(wr,2)}% | {total}")
