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
    text-shadow:0 0 10px #00ffcc;
    border-bottom:2px solid #00ffcc;
    padding-bottom:10px;
}
.card {
    border:2px solid #00ffcc;
    border-radius:15px;
    padding:20px;
    background:rgba(0,255,204,0.05);
    box-shadow:0 0 20px rgba(0,255,204,0.2);
}
.cotes {
    display:flex;
    justify-content:space-around;
    margin-top:10px;
}
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
    st.title("🔐 JET X ANDR V8 LOGIN")
    pwd = st.text_input("PASSWORD", type="password")

    if st.button("ENTER"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("ACCESS DENIED")
    st.stop()

# ---------------- ML TRAIN ----------------
def train():
    data = []
    for h in st.session_state.log:
        if h.get("result") is not None:
            data.append([
                h["prob"], h["moy"], h["max"], h["ref"], h["conf"], h["result"]
            ])

    if len(data) < 6:
        return

    df = pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"])
    X = df.drop("label", axis=1)
    y = df["label"]

    Xs = st.session_state.scaler.fit_transform(X)
    st.session_state.model.fit(Xs, y)
    st.session_state.ready = True

# ---------------- ENGINE ----------------
def predict(hash_str, h_act, last_cote):

    tz = pytz.timezone("Indian/Antananarivo")

    try:
        t = datetime.strptime(h_act, "%H:%M:%S")
    except:
        t = datetime.now(tz)

    h = hashlib.sha256(hash_str.encode()).hexdigest()

    seed = int(h[:12], 16)
    np.random.seed(seed % (2**32))

    norm = (int(h[12:20], 16) % 1000) / 100 + 1.2

    sec = t.hour*3600 + t.minute*60 + t.second

    # ---------------- RISK INTELLIGENCE ----------------
    risk = 1 + (last_cote - 1.5) * 0.35
    risk = max(0.6, min(risk, 1.8))

    cycle = 1.2 if last_cote < 1.6 else 1.0 if last_cote < 2.5 else 0.9

    base = norm * cycle / risk   # 🔥 risk affects engine

    sims = np.random.lognormal(mean=np.log(base), sigma=0.20, size=12000)

    prob = round(len([x for x in sims if x >= 2.0]) / 12000 * 100, 1)

    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 95), 2)
    minv = round(moy * 0.55, 2)

    conf = round(((prob * moy) / 10) / risk, 1)

    # ---------------- ENTRY ENGINE ----------------
    hash_time = int(h[20:28], 16)

    base_delay = (
        hash_time % 60 +
        (sec % 30) // 5 +
        int(norm * 4)
    )

    locked_delay = round(base_delay / 5) * 5

    entry = t + timedelta(seconds=locked_delay)
    sniper = entry + timedelta(seconds=20)

    win_start = (sniper - timedelta(seconds=2)).strftime("%H:%M:%S")
    win_end = (sniper + timedelta(seconds=2)).strftime("%H:%M:%S")

    # ---------------- SIGNAL LOGIC (RISK AWARE) ----------------
    if prob < (45 * risk) or moy < 1.8:
        signal = "❌ SKIP"
        god_mode = False

    elif conf > (35 * risk) and prob > (75 * risk) and moy > (2.4 * risk):
        signal = "🚀 ULTRA GOD MODE"
        god_mode = True

    elif conf > (28 * risk) and prob > (68 * risk) and moy > (2.1 * risk):
        signal = "🔥 GOD MODE"
        god_mode = True

    elif prob > (60 * risk):
        signal = "✅ BUY"
        god_mode = False

    else:
        signal = "⏳ WAIT"
        god_mode = False

    # ---------------- AI ----------------
    ai = "N/A"
    if st.session_state.ready:
        try:
            X = st.session_state.scaler.transform(
                np.array([prob, moy, maxv, last_cote, conf]).reshape(1,-1)
            )
            ai = f"{round(st.session_state.model.predict_proba(X)[0][1]*100,1)}%"
        except:
            ai = "ERROR"

    return {
        "entry": entry.strftime("%H:%M:%S"),
        "sniper": sniper.strftime("%H:%M:%S"),
        "window": f"{win_start} - {win_end}",
        "prob": prob,
        "moy": moy,
        "max": maxv,
        "min": minv,
        "conf": conf,
        "signal": signal,
        "god_mode": god_mode,
        "ai": ai,
        "ref": round(last_cote,2),
        "risk": round(risk,2),
        "result": None
    }

# ---------------- UI ----------------
st.markdown("<h1>🚀 JET X ANDR V8 ⚡ RISK INTELLIGENCE</h1>", unsafe_allow_html=True)

h = st.text_input("HASH")
t = st.text_input("HEURE (HH:MM:SS)")
c = st.number_input("COTE REF", value=1.5)

if st.button("RUN RISK AI"):
    if h and t:
        r = predict(h,t,c)
        st.session_state.log.append(r)
        train()
        st.rerun()

if st.session_state.log:
    r = st.session_state.log[-1]

    st.markdown(f"""
    <div class="card">

    <h2>{r['signal']}</h2>
    <p>AI: {r['ai']} | RISK: {r['risk']}</p>

    {"<h3>🔥 GOD MODE ACTIVE</h3>" if r.get("god_mode", False) else ""}

    <h3>ENTRY: {r['entry']}</h3>
    <h4>SNIPER: {r['sniper']}</h4>
    <small>{r['window']}</small>

    <div class="cotes">
        <div>MIN<br>{r['min']}x</div>
        <div>MOY<br>{r['moy']}x</div>
        <div>MAX<br>{r['max']}x</div>
    </div>

    <p>Prob: {r['prob']}% | Conf: {r['conf']}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("WIN"):
            st.session_state.log[-1]["result"] = 1
            train()
            st.rerun()

    with col2:
        if st.button("LOSE"):
            st.session_state.log[-1]["result"] = 0
            train()
            st.rerun()

st.sidebar.write("JET X ANDR V8 ACTIVE ⚡ RISK INTELLIGENCE")
