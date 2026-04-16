import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz
import sqlite3

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# ---------------- CONFIG ----------------
st.set_page_config(page_title="JET X ANDR V9 ⚡ TRUE AI UPGRADE", layout="wide")

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
</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE (NEW AI MEMORY) ----------------
DB = "jetx_v9_ai.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prob REAL,
        moy REAL,
        max REAL,
        ref REAL,
        conf REAL,
        result INTEGER
    )
    """)
    conn.commit()
    conn.close()

init_db()

def save_history(data):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    INSERT INTO history (prob,moy,max,ref,conf,result)
    VALUES (?,?,?,?,?,?)
    """, data)
    conn.commit()
    conn.close()

def load_history():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM history", conn)
    conn.close()
    return df

# ---------------- SESSION ----------------
if "model" not in st.session_state:
    st.session_state.model = RandomForestClassifier(n_estimators=200)

if "meta_model" not in st.session_state:
    st.session_state.meta_model = LogisticRegression()

if "scaler" not in st.session_state:
    st.session_state.scaler = StandardScaler()

if "ready" not in st.session_state:
    st.session_state.ready = False

if "log" not in st.session_state:
    st.session_state.log = []

# ---------------- TRUE AI TRAIN ----------------
def train_ai():
    df = load_history()

    if len(df) < 10:
        return

    X = df[["prob","moy","max","ref","conf"]]
    y = df["result"]

    Xs = st.session_state.scaler.fit_transform(X)

    st.session_state.model.fit(Xs, y)
    st.session_state.meta_model.fit(Xs, y)

    st.session_state.ready = True

# ---------------- ENGINE (IMPROVED + STABLE ENTRY) ----------------
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

    cycle = 1.3 if last_cote < 1.6 else 1.0 if last_cote < 2.5 else 0.85

    sims = np.random.lognormal(mean=np.log(norm * cycle), sigma=0.22, size=15000)

    prob = round(len([x for x in sims if x >= 2.0]) / 15000 * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 95), 2)
    conf = round((prob * moy) / 10, 1)

    # ---------------- FIXED ENTRY TIME ----------------
    hash_time = int(h[20:28], 16)

    delay = (
        (hash_time % 50) +
        ((sec % 60)//10) +
        int(norm*2)
    )

    delay = (delay // 5) * 5
    entry = t + timedelta(seconds=delay)

    sniper = entry + timedelta(seconds=20)

    # ---------------- TRUE AI PREDICTION ----------------
    ai_score = None
    if st.session_state.ready:
        X = np.array([prob,moy,maxv,last_cote,conf]).reshape(1,-1)
        Xs = st.session_state.scaler.transform(X)

        rf_pred = st.session_state.model.predict_proba(Xs)[0][1]
        meta_pred = st.session_state.meta_model.predict_proba(Xs)[0][1]

        ai_score = round((rf_pred*0.7 + meta_pred*0.3)*100, 1)

    # ---------------- SIGNAL (RISK INTELLIGENT) ----------------
    risk = 100 - prob + (3 - moy)*10

    if risk > 70:
        signal = "❌ NO TRADE"
        decision = 0
    elif conf > 22 and prob > 65:
        signal = "🔥 GOD MODE (RARE)"
        decision = 1
    elif conf > 18:
        signal = "⚡ STRONG ENTRY"
        decision = 1
    elif prob > 50:
        signal = "✅ NORMAL ENTRY"
        decision = 1
    else:
        signal = "⏳ WAIT"
        decision = None

    return {
        "entry": entry.strftime("%H:%M:%S"),
        "sniper": sniper.strftime("%H:%M:%S"),
        "prob": prob,
        "moy": moy,
        "max": maxv,
        "conf": conf,
        "risk": round(risk,1),
        "signal": signal,
        "ai": ai_score,
        "ref": last_cote,
        "result": None,
        "decision": decision
    }

# ---------------- UI ----------------
st.title("🚀 JET X ANDR V9 ⚡ TRUE AI UPGRADE")

h = st.text_input("HASH")
t = st.text_input("HEURE")
c = st.number_input("COTE REF", value=1.5)

if st.button("RUN AI"):
    if h and t:
        r = predict(h,t,c)
        st.session_state.log.append(r)
        save_history([r["prob"],r["moy"],r["max"],r["ref"],r["conf"],0])
        train_ai()
        st.rerun()

if st.session_state.log:
    r = st.session_state.log[-1]

    st.markdown(f"""
    <div class="card">
        <h2>{r['signal']}</h2>
        <p>AI SCORE: {r['ai']}% | RISK: {r['risk']}</p>

        <h3>ENTRY: {r['entry']}</h3>
        <h4>SNIPER: {r['sniper']}</h4>

        <p>Prob: {r['prob']}% | Conf: {r['conf']}</p>
    </div>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.write("V9 TRUE AI ACTIVE")
