import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG ----------------
st.set_page_config(page_title="JET X ANDR V10 ⚡ RL ADAPTIVE ENGINE", layout="wide")

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
}
.cotes {
    display:flex;
    justify-content:space-around;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "log" not in st.session_state:
    st.session_state.log = []

if "auth" not in st.session_state:
    st.session_state.auth = False

if "model" not in st.session_state:
    st.session_state.model = RandomForestClassifier(n_estimators=120)

if "scaler" not in st.session_state:
    st.session_state.scaler = StandardScaler()

if "ready" not in st.session_state:
    st.session_state.ready = False

# ---------------- RL MEMORY ----------------
if "rl_weight" not in st.session_state:
    st.session_state.rl_weight = {
        "ultra": 0.5,
        "strong": 0.5,
        "wait": 0.5
    }

# ---------------- LOGIN ----------------
if not st.session_state.auth:
    st.title("🔐 V10 RL LOGIN")
    pwd = st.text_input("PASSWORD", type="password")

    if st.button("ENTER"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# ---------------- TRAIN ML ----------------
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

    st.session_state.scaler.fit(X)
    Xs = st.session_state.scaler.transform(X)

    st.session_state.model.fit(Xs, y)
    st.session_state.ready = True

# ---------------- RL UPDATE ----------------
def update_rl(signal_type, result):
    if result == 1:
        st.session_state.rl_weight[signal_type] += 0.05
    else:
        st.session_state.rl_weight[signal_type] -= 0.05

    # clamp 0–1
    st.session_state.rl_weight[signal_type] = max(0.1, min(1.0, st.session_state.rl_weight[signal_type]))

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

    cycle = 1.2 if last_cote < 1.6 else 1.0 if last_cote < 2.5 else 0.9

    sims = np.random.lognormal(mean=np.log(norm * cycle), sigma=0.20, size=12000)

    prob = round(len([x for x in sims if x >= 2.0]) / 12000 * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 95), 2)
    minv = round(moy * 0.55, 2)
    conf = round((prob * moy) / 10, 1)

    # ---------------- STABLE ENTRY (NO DRIFT) ----------------
    base_delay = (
        (int(h[20:28], 16) % 30) +
        (sec % 20) // 5 +
        int(norm * 3)
    )

    locked_delay = (base_delay // 5) * 5
    entry_time = t + timedelta(seconds=locked_delay)
    sniper_time = entry_time + timedelta(seconds=20)

    # ---------------- RL ADAPTIVE SIGNAL ----------------
    if conf >= 78 and moy >= 2.5:
        sig = "🔥 ULTRA X3+ SNIPER 🎯"
        sig_type = "ultra"

    elif conf >= 65 and moy >= 1.8:
        sig = "🟢 STRONG ENTRY ⚡"
        sig_type = "strong"

    elif conf >= 45:
        sig = "🟡 TIMING WAIT ⏳"
        sig_type = "wait"

    else:
        sig = "🔴 NO ENTRY ❌"
        sig_type = "wait"

    # apply RL weight (adaptive boost/reduce)
    weight = st.session_state.rl_weight[sig_type]
    conf = round(conf * weight, 1)

    # ---------------- SAFE ML ----------------
    ai_score = "N/A"
    if st.session_state.ready:
        try:
            X = st.session_state.scaler.transform(
                np.array([prob, moy, maxv, last_cote, conf]).reshape(1, -1)
            )
            ai_score = f"{round(st.session_state.model.predict_proba(X)[0][1]*100,1)}%"
        except:
            ai_score = "SAFE"

    return {
        "entry": entry_time.strftime("%H:%M:%S"),
        "sniper": sniper_time.strftime("%H:%M:%S"),
        "prob": prob,
        "moy": moy,
        "max": maxv,
        "min": minv,
        "conf": conf,
        "signal": sig,
        "type": sig_type,
        "ai": ai_score,
        "ref": last_cote,
        "result": None
    }

# ---------------- UI ----------------
st.markdown("<h1>🚀 JET X ANDR V10 ⚡ RL ADAPTIVE ENGINE</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 LIVE", "📜 HISTORY", "📖 GUIDE"])

with tab1:
    c1,c2,c3 = st.columns(3)

    with c1:
        h = st.text_input("HASH")

    with c2:
        t = st.text_input("HEURE (HH:MM:SS)")

    with c3:
        c = st.number_input("COTE REF", value=1.5)

    if st.button("RUN V10 ENGINE"):
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

        <div class="cotes">
        <div>MIN<br>{r['min']}x</div>
        <div>MOY<br>{r['moy']}x</div>
        <div>MAX<br>{r['max']}x</div>
        </div>

        <p>Prob: {r['prob']}% | Conf: {r['conf']} | TYPE: {r['type']}</p>
        </div>
        """, unsafe_allow_html=True)

        col1,col2 = st.columns(2)

        with col1:
            if st.button("WIN"):
                st.session_state.log[-1]["result"]=1
                update_rl(r["type"], 1)
                train()
                st.rerun()

        with col2:
            if st.button("LOSE"):
                st.session_state.log[-1]["result"]=0
                update_rl(r["type"], 0)
                train()
                st.rerun()

with tab2:
    st.dataframe(pd.DataFrame(st.session_state.log[::-1]))

with tab3:
    st.markdown("""
### 📖 V10 RL ADAPTIVE ENGINE
✔ WIN/LOSE learning (reinforcement)  
✔ Adaptive signal strength  
✔ Entry time stable (no drift)  
✔ Self-adjusting confidence weights  
✔ Hybrid ML + RL system  
""")icon = "⚪" if entry['result'] is None else ("✅" if entry['result']==1 else "❌")
            st.write(f"{res_icon} {entry['entry']} | {entry['moy']}x")
