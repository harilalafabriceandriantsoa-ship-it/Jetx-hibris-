import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG ----------------
st.set_page_config(page_title="JET X ANDR V8 ⚡ RISK INTELLIGENCE", layout="wide")

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #001a1a, #000000);
    color: #00ffcc;
    font-family: monospace;
}
h1 {
    text-align:center;
    color:#00ffcc;
    border-bottom:2px solid #00ffcc;
    padding-bottom:10px;
}
.card {
    border:2px solid #00ffcc;
    border-radius:15px;
    padding:20px;
    background:rgba(0,255,204,0.05);
}
.cotes {display:flex; justify-content:space-around;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "log" not in st.session_state:
    st.session_state.log = []

if "auth" not in st.session_state:
    st.session_state.auth = False

if "model" not in st.session_state:
    st.session_state.model = RandomForestClassifier(n_estimators=150)

if "scaler" not in st.session_state:
    st.session_state.scaler = StandardScaler()

if "ready" not in st.session_state:
    st.session_state.ready = False

# ---------------- LOGIN ----------------
if not st.session_state.auth:
    st.title("JET X ANDR V8 LOGIN")
    pwd = st.text_input("PASSWORD", type="password")

    if st.button("ENTER"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# ---------------- ML ----------------
def train():
    data = []
    for h in st.session_state.log:
        if h.get("result") is not None:
            data.append([h["prob"], h["moy"], h["max"], h["ref"], h["conf"], h["result"]])

    if len(data) < 6:
        return

    df = pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"])
    X = st.session_state.scaler.fit_transform(df.drop("label", axis=1))
    y = df["label"]

    st.session_state.model.fit(X, y)
    st.session_state.ready = True

# ---------------- ENGINE (FIXED ENTRY + RISK CONTROL) ----------------
def predict(hash_str, h_act, last_cote):

    tz = pytz.timezone("Indian/Antananarivo")

    try:
        t = datetime.strptime(h_act, "%H:%M:%S")
    except:
        t = datetime.now(tz)

    h = hashlib.sha256(hash_str.encode()).hexdigest()

    seed = int(h[:12], 16) % (2**32)
    np.random.seed(seed)

    norm = (int(h[12:20], 16) % 1000) / 100 + 1.1
    sec = t.hour*3600 + t.minute*60 + t.second

    # ---------------- REF-BASED RISK CONTROL ----------------
    if last_cote < 1.5:
        risk_level = 0.25
    elif last_cote < 2.2:
        risk_level = 0.45
    elif last_cote < 3.0:
        risk_level = 0.65
    else:
        risk_level = 0.85

    cycle = 1.2 - risk_level

    sims = np.random.lognormal(mean=np.log(norm * cycle), sigma=0.22, size=12000)

    prob = round(len([x for x in sims if x >= 2.0]) / 12000 * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 95), 2)
    minv = round(moy * 0.55, 2)

    conf = round((prob * moy) / 10, 1)

    # ---------------- 🔒 FIXED ENTRY TIME (NO MORE NOISE) ----------------
    hash_time = int(h[20:28], 16)

    base_delay = (hash_time % 60) + (sec % 30)//10 + int(norm*3)

    # LOCK SYSTEM (IMPORTANT FIX)
    locked = (base_delay // 5) * 5

    entry = t + timedelta(seconds=locked)
    sniper = entry + timedelta(seconds=18)

    # ---------------- RISK-BASED SIGNAL (NO MORE GOD MODE FOR EVERYTHING) ----------------
    risk_score = round(risk_level * 100, 1)

    if prob < 40 or moy < 1.7:
        signal = "❌ NO TRADE"
    elif risk_level > 0.8:
        signal = "🔥 HIGH RISK GOD MODE"
    elif conf > 20 and prob > 60:
        signal = "⚡ STRONG ENTRY"
    elif prob > 50:
        signal = "✅ NORMAL ENTRY"
    else:
        signal = "⏳ WAIT"

    ai = "N/A"
    if st.session_state.ready:
        try:
            X = st.session_state.scaler.transform(np.array([prob,moy,maxv,last_cote,conf]).reshape(1,-1))
            ai = f"{round(st.session_state.model.predict_proba(X)[0][1]*100,1)}%"
        except:
            ai = "ERR"

    return {
        "entry": entry.strftime("%H:%M:%S"),
        "sniper": sniper.strftime("%H:%M:%S"),
        "prob": prob,
        "moy": moy,
        "max": maxv,
        "min": minv,
        "conf": conf,
        "risk": risk_score,
        "signal": signal,
        "ai": ai,
        "ref": last_cote,
        "result": None,
        "god_mode": "GOD" in signal
    }

# ---------------- UI ----------------
st.title("🚀 JET X ANDR V8 ⚡ RISK INTELLIGENCE")

h = st.text_input("HASH")
t = st.text_input("HEURE")
c = st.number_input("COTE REF", value=1.5)

if st.button("RUN"):
    if h and t:
        r = predict(h,t,c)
        st.session_state.log.append(r)
        st.rerun()

if st.session_state.log:
    r = st.session_state.log[-1]

    st.markdown(f"""
    <div class="card">
        <h2>{r['signal']}</h2>
        <p>AI: {r['ai']} | RISK: {r['risk']}%</p>

        <h3>ENTRY: {r['entry']}</h3>
        <h4>SNIPER: {r['sniper']}</h4>

        <div class="cotes">
            <div>MIN<br>{r['min']}x</div>
            <div>MOY<br>{r['moy']}x</div>
            <div>MAX<br>{r['max']}x</div>
        </div>

        <p>Prob: {r['prob']}% | Conf: {r['conf']}</p>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.write("V8 ACTIVE")
