import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG & PREMIUM DESIGN ----------------
st.set_page_config(page_title="JET X ANDR V6 ⚡ GOD MODE", layout="wide")

st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top, #001a1a, #000000);
        color: #00ffcc;
        font-family: 'Courier New', monospace;
    }
    h1 {
        text-align: center; color: #00ffcc;
        text-shadow: 0 0 10px #00ffcc, 0 0 20px #00ffcc;
        letter-spacing: 4px; border-bottom: 2px solid #00ffcc;
        padding-bottom: 10px;
    }
    .prediction-card {
        background: rgba(0, 255, 204, 0.05);
        border: 2px solid #00ffcc;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 0 30px rgba(0, 255, 204, 0.2);
        margin-top: 10px;
        text-align: center;
    }
    .cote-container {
        display: flex;
        justify-content: space-around;
        margin-top: 20px;
        padding: 15px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
    }
    .cote-item { text-align: center; }
    .cote-label { font-size: 12px; color: #aaa; }
    .cote-val { font-size: 22px; font-weight: bold; color: #00ffcc; }

    .stButton>button {
        width: 100%; background: linear-gradient(90deg, #004e4e, #00ffcc);
        color: black; font-weight: bold; border: none;
        height: 50px; border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "pred_log" not in st.session_state:
    st.session_state.pred_log = []

if "auth" not in st.session_state:
    st.session_state.auth = False

if "ml_model" not in st.session_state:
    st.session_state.ml_model = RandomForestClassifier(n_estimators=150)

if "ml_ready" not in st.session_state:
    st.session_state.ml_ready = False

# ---------------- LOGIN ----------------
if not st.session_state.auth:
    st.markdown("<h1>🔐 SECURITY ACCESS</h1>", unsafe_allow_html=True)
    pwd = st.text_input("ENTER PASSWORD", type="password")
    if st.button("ACTIVATE"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("ACCESS DENIED")
    st.stop()

# ---------------- ML TRAIN ----------------
def train_ai():
    history = st.session_state.pred_log
    data = [
        [h["prob"], h["moy"], h["max"], float(h["ref"]), h["confidence"], h["result"]]
        for h in history if h.get("result") is not None
    ]

    if len(data) < 5:
        return

    df = pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"])

    if len(df["label"].unique()) < 2:
        return

    scaler = StandardScaler()
    X = scaler.fit_transform(df.drop("label", axis=1))
    y = df["label"]

    model = RandomForestClassifier(n_estimators=150)
    model.fit(X, y)

    st.session_state.scaler = scaler
    st.session_state.ml_model = model
    st.session_state.ml_ready = True

# ---------------- ENGINE ----------------
def run_prediction(hash_str, h_act, last_cote):

    tz = pytz.timezone('Indian/Antananarivo')

    try:
        t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except:
        t_obj = datetime.now(tz)

    # 🔥 HASH ENGINE
    full_hash = hashlib.sha256((hash_str + h_act).encode()).hexdigest()
    seed = int(full_hash[:12], 16) % (2**32)
    np.random.seed(seed)

    hash_norm = (int(full_hash[10:18], 16) % 1000) / 100 + 1.2
    t_sec = t_obj.hour*3600 + t_obj.minute*60 + t_obj.second

    # 🔥 TIME FACTOR
    time_factor = (t_sec % 600) / 600

    # 🔥 CYCLE LOGIC
    cycle = 1.2 if last_cote < 1.5 else 1.05 if last_cote < 2.5 else 0.9

    ref_val = 2.2 + (time_factor * 0.25)

    base = hash_norm * ref_val * cycle

    # 🔥 SIMULATION
    sims = np.random.lognormal(mean=np.log(base), sigma=0.25, size=20000)

    prob = round(len([s for s in sims if s >= 2.0]) / 20000 * 100, 1)

    moy = round(np.mean(sims) * 1.05, 2)
    maxv = round(np.percentile(sims, 95) * 1.25, 2)
    minv = round(max(1.2, moy * 0.5), 2)

    conf = round((prob * moy) / 12, 1)

    # 🔥 FIXED ENTRY TIME (NO RANDOM JITTER ANYMORE)
    # 👉 stable + second-level precision (hash-based deterministic)
    h_seed = int(full_hash[18:26], 16)

    base_delay = (h_seed % 45) + 20
    micro_shift = (h_seed % 10)

    delay_seconds = base_delay + micro_shift

    entry_time = t_obj + timedelta(seconds=delay_seconds)

    # 🔥 SNIPER TIME (EXACT)
    sniper_time = entry_time + timedelta(seconds=12)

    window_start = sniper_time - timedelta(seconds=2)
    window_end = sniper_time + timedelta(seconds=2)

    # 🔥 SIGNAL
    if prob < 40 or moy < 1.8:
        signal, emoji = "❌ SKIP", "❌"
    elif conf > 18:
        signal, emoji = "🔥 GOD MODE", "⚡🎯"
    else:
        signal, emoji = "🎯 BUY", "🎯"

    return {
        "h_act": h_act,
        "h_ent": entry_time.strftime("%H:%M:%S"),
        "sniper": sniper_time.strftime("%H:%M:%S"),
        "window": f"{window_start.strftime('%H:%M:%S')} - {window_end.strftime('%H:%M:%S')}",
        "prob": prob,
        "moy": moy,
        "max": maxv,
        "min": minv,
        "confidence": conf,
        "signal": signal,
        "emoji": emoji,
        "ref": round(ref_val, 2),
        "result": None
    }

# ---------------- UI ----------------
st.markdown("<h1>🚀 JET X ANDR V6 ⚡ GOD MODE</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 ANALYSE", "📜 HISTORY", "📖 GUIDE"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        h_in = st.text_input("HASH")

    with c2:
        t_in = st.text_input("TIME (HH:MM:SS)")

    with c3:
        last_c = st.number_input("LAST COTE", value=1.5)

    if st.button("RUN"):
        if h_in and t_in:
            res = run_prediction(h_in, t_in, last_c)
            st.session_state.pred_log.append(res)
            st.rerun()

    if st.session_state.pred_log:
        r = st.session_state.pred_log[-1]

        st.markdown(f"""
        <div class="prediction-card">

        <h2>{r['emoji']} {r['signal']}</h2>

        <p><b>ENTRY:</b> {r['h_ent']}</p>
        <p><b>SNIPER:</b> {r['sniper']}</p>
        <p><b>WINDOW:</b> {r['window']}</p>

        <hr>

        <div class="cote-container">
            <div class="cote-item">MIN<br>{r['min']}x</div>
            <div class="cote-item">MOY<br>{r['moy']}x</div>
            <div class="cote-item">MAX<br>{r['max']}x</div>
        </div>

        <p>Prob: {r['prob']}% | Conf: {r['confidence']}</p>

        </div>
        """, unsafe_allow_html=True)

with tab2:
    if st.session_state.pred_log:
        st.dataframe(pd.DataFrame(st.session_state.pred_log[::-1]))

with tab3:
    st.markdown("""
### 📖 GUIDE
- ENTRY = fotoana hidirana
- SNIPER = peak cashout
- WINDOW = 2 sec precision zone
- GOD MODE = confidence > 18
""")

st.sidebar.button("RESET", on_click=lambda: st.session_state.update(pred_log=[]))
