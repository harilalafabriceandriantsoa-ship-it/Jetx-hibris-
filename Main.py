import streamlit as st
import numpy as np
import hashlib
from datetime import datetime
import pytz
from sklearn.ensemble import RandomForestClassifier

# ================= CONFIG =================

st.set_page_config(page_title="COSMOS X ANALYTIC", layout="centered")

st.markdown("""
<style>
.stApp { background:#000; color:#00ffcc; font-family: monospace; }
h1 { text-align:center; color:#00ffcc; }
.box { padding:15px; border:1px solid #00ffcc; border-radius:10px; }
</style>
""", unsafe_allow_html=True)

# ================= SESSION =================

if "data" not in st.session_state:
    st.session_state.data = []

if "model" not in st.session_state:
    st.session_state.model = RandomForestClassifier(n_estimators=150)

if "trained" not in st.session_state:
    st.session_state.trained = False

# ================= TIME =================

def now():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

# ================= HASH =================

def hash_val(x):
    h = hashlib.sha256(x.encode()).hexdigest()
    return int(h[:10], 16) / 0xFFFFFFFFFF

# ================= FEATURES =================

def features(prob, avg, maxv, minv, conf):
    spread = maxv - minv
    stability = 1 / (1 + spread)
    score = (avg * 2) + prob + (conf * 0.5) + (stability * 10)
    return [prob, avg, maxv, minv, conf, score]

# ================= AI TRAIN =================

def train():
    if len(st.session_state.data) < 20:
        return

    data = np.array(st.session_state.data)

    X = data[:, :5]
    y = data[:, 5]

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X, y)

    st.session_state.model = model
    st.session_state.trained = True

# ================= AI PREDICT =================

def ai_predict(x):
    if not st.session_state.trained:
        return None
    return st.session_state.model.predict_proba([x])[0][1] * 100

# ================= ENGINE =================

def run(hash_input, cote_ref):

    h = hash_val(hash_input)

    # simulation (statistical only)
    sims = np.random.lognormal(mean=np.log(1 + h), sigma=0.4, size=5000)

    prob = np.mean(sims >= 2.5) * 100
    prob = round(prob, 2)

    avg = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 95), 2)
    minv = round(np.percentile(sims, 10), 2)

    conf = round(prob * (avg / 3), 2)

    feat = features(prob, avg, maxv, minv, conf)

    label = 1 if prob > 60 else 0

    st.session_state.data.append(feat + [label])

    train()

    ai_score = ai_predict(feat)

    spread = maxv - minv

    # ================= SIGNAL =================

    if spread > 6:
        sig = "❌ HIGH RISK"

    elif prob < 45:
        sig = "⏳ WEAK"

    elif ai_score and ai_score > 70:
        sig = "⚡ STRONG ZONE"

    elif prob > 60:
        sig = "🟢 GOOD ZONE"

    else:
        sig = "🟡 WAIT"

    return {
        "prob": prob,
        "avg": avg,
        "max": maxv,
        "min": minv,
        "conf": conf,
        "ai": ai_score,
        "signal": sig
    }

# ================= UI =================

st.title("🚀 COSMOS X ANALYTIC ENGINE")

h = st.text_input("HASH INPUT")
c = st.number_input("COTE REF", value=2.0)

if st.button("RUN ANALYSIS"):
    if h:
        st.session_state.res = run(h, c)

if "res" in st.session_state:
    r = st.session_state.res

    st.markdown(f"""
    <div class="box">
        <h2>{r['signal']}</h2>
        <p>PROB: {r['prob']}%</p>
        <p>AVG: {r['avg']}</p>
        <p>MAX: {r['max']}</p>
        <p>MIN: {r['min']}</p>
        <p>CONF: {r['conf']}</p>
        <p>AI: {r['ai']}</p>
    </div>
    """, unsafe_allow_html=True)
