import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG ----------------
st.set_page_config(page_title="JET X ANDR V7 ⚡ GOD MODE", layout="wide")

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
.btn>button {
    width:100%;
    background:linear-gradient(90deg,#004e4e,#00ffcc);
    color:black;
    font-weight:bold;
    height:45px;
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
    st.title("🔐 JET X ANDR V7 LOGIN")
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

# ---------------- ENGINE (STABLE EXACT SECOND LOCK) ----------------
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

    cycle = 1.2 if last_cote < 1.6 else 1.0 if last_cote < 2.5 else 0.9

    base = norm * cycle

    sims = np.random.lognormal(mean=np.log(base), sigma=0.20, size=12000)

    prob = round(len([x for x in sims if x >= 2.0]) / 12000 * 100, 1)

    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 95), 2)
    minv = round(moy * 0.55, 2)

    conf = round((prob * moy) / 10, 1)

    # ---------------- EXACT SECOND LOCK SYSTEM ----------------
    hash_time = int(h[20:28], 16)

    # STEP 1: base delay deterministic
    base_delay = (
        hash_time % 60 +
        (sec % 30) // 5 +
        int(norm * 4)
    )

    # STEP 2: LOCK to 5-second grid (IMPORTANT)
    locked_delay = round(base_delay / 5) * 5

    entry = t + timedelta(seconds=locked_delay)

    sniper = entry + timedelta(seconds=20)

    win_start = (sniper - timedelta(seconds=2)).strftime("%H:%M:%S")
    win_end = (sniper + timedelta(seconds=2)).strftime("%H:%M:%S")

    # SIGNAL
if prob < 45 or moy < 1.8:
    signal = "❌ SKIP"
    god_mode = False
elif conf > 22 and prob > 65 and moy > 2.5:
    signal = "🔥 TO GOD MODE 🚀⚡"
    god_mode = True
elif conf > 20:
    signal = "🔥 GOD MODE"
    god_mode = True
elif prob > 60:
    signal = "✅ BUY"
    god_mode = False
else:
    signal = "⏳ WAIT"
    god_mode = False
    # AI
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
        "ai": ai,
        "ref": round(last_cote,2),
        "result": None
    }

# ---------------- UI ----------------
st.markdown("<h1>🚀 JET X ANDR V7 ⚡ GOD MODE</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 LIVE", "📜 HISTORY", "📖 GUIDE"])

with tab1:
    c1,c2,c3 = st.columns(3)

    with c1:
        h = st.text_input("HASH")

    with c2:
        t = st.text_input("HEURE (HH:MM:SS)")

    with c3:
        c = st.number_input("COTE", value=1.5)

    if st.button("RUN GOD MODE"):
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
        <p>AI: {r['ai']}</p>

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

        col1,col2 = st.columns(2)
        with col1:
            if st.button("WIN"):
                st.session_state.log[-1]["result"]=1
                train(); st.rerun()
        with col2:
            if st.button("LOSE"):
                st.session_state.log[-1]["result"]=0
                train(); st.rerun()

with tab2:
    st.dataframe(pd.DataFrame(st.session_state.log[::-1]))

with tab3:
    st.markdown("""
### 📖 V7 GOD MODE
✔ ENTRY locked (5-sec grid)  
✔ SNIPER stable  
✔ ML WIN/LOSE learning  
✔ No randomness drift  
✔ deterministic engine  
""")

st.sidebar.write("JET X ANDR V7 ACTIVE")
