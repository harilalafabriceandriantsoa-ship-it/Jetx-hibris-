import streamlit as st
import numpy as np
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time

from sklearn.ensemble import RandomForestClassifier

# ==========================================
# 💎 UI (TSY OVAINA)
# ==========================================
st.set_page_config(page_title="JETX ANDR V14 STABLE", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');

    .stApp {
        background-color: #020205;
        background-image: 
            radial-gradient(circle at 20% 30%, #051919 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, #1a051a 0%, transparent 50%);
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }

    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(90deg, #00ffcc, #ff00cc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }

    .glass-card {
        background: rgba(10, 10, 20, 0.7);
        border: 1px solid rgba(0, 255, 204, 0.3);
        border-radius: 20px;
        padding: 25px;
        backdrop-filter: blur(15px);
        margin-bottom: 20px;
    }

    .stButton>button {
        background: linear-gradient(135deg, #00ffcc 0%, #0088ff 100%) !important;
        color: #000 !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        height: 55px !important;
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 SESSION
# ==========================================
if "history" not in st.session_state:
    st.session_state.history = []

if "ml_model" not in st.session_state:
    st.session_state.ml_model = RandomForestClassifier(n_estimators=120)

if "ml_ready" not in st.session_state:
    st.session_state.ml_ready = False

# ==========================================
# ⏱️ TIME
# ==========================================
def get_time():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

# ==========================================
# 🧠 AI TRAIN
# ==========================================
def train_ai():
    data = []
    for h in st.session_state.history:
        if "result" in h:
            data.append([
                h["x3_prob"],
                h["conf"],
                h["moy"],
                h["spread"],
                1 if h["result"] == "win" else 0
            ])

    if len(data) < 6:
        return

    df = pd.DataFrame(data, columns=["prob","conf","moy","spread","label"])
    X = df[["prob","conf","moy","spread"]]
    y = df["label"]

    model = RandomForestClassifier(n_estimators=150, max_depth=6)
    model.fit(X, y)

    st.session_state.ml_model = model
    st.session_state.ml_ready = True

# ==========================================
# 🤖 AI PREDICT
# ==========================================
def ai_predict(features):
    if not st.session_state.ml_ready:
        return None
    try:
        X = np.array(features).reshape(1, -1)
        return round(st.session_state.ml_model.predict_proba(X)[0][1] * 100, 1)
    except:
        return None

# ==========================================
# ⏰ ENTRY TIME ENGINE
# ==========================================
def entry_calc(hash_val, spread, t_in):
    now = get_time()

    try:
        t_obj = datetime.strptime(t_in.strip(), "%H:%M:%S").time()
        base_time = datetime.combine(now.date(), t_obj)
    except:
        base_time = now

    hash_shift = (int(hash_val[:6], 16) % 6) - 3

    base_delay = 18
    final_seconds = int(base_delay + spread + hash_shift)

    final_seconds = max(20, min(45, final_seconds))

    base_time = base_time.replace(microsecond=0)

    return (base_time + timedelta(seconds=final_seconds)).strftime("%H:%M:%S")

# ==========================================
# 🚀 ENGINE CORE
# ==========================================
def run_engine(h_in, t_in, c_ref, last_cote):

    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:16], 16)

    np.random.seed(h_num & 0xffffffff)

    # FIX LAST COTE
    if last_cote > 6:
        last_cote = 4.0
    elif last_cote > 4:
        last_cote = (last_cote + 4) / 2

    base = (h_num % 1000) / 100 + 1.2

    sims = np.random.lognormal(np.log(base), 0.35, 12000)

    prob = round(np.mean(sims >= 3.0) * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 95), 2)
    minv = round(np.percentile(sims, 5), 2)

    spread = maxv - minv

    conf = round((prob * 0.6 + moy * 20), 1)
    conf = max(20, min(99, conf))

    ai = ai_predict([prob, conf, moy, spread])

    strength = prob * 0.6 + (ai or 0) * 0.4

    entry = entry_calc(h_hex, spread, t_in)

    if strength > 70:
        signal = "💎 ULTRA BUY"
    elif strength > 55:
        signal = "🟢 STRONG BUY"
    elif strength > 40:
        signal = "⚡ SCALP"
    else:
        signal = "⚠️ SKIP"

    res = {
        "entry": entry,
        "signal": signal,
        "x3_prob": prob,
        "conf": conf,
        "moy": moy,
        "max": maxv,
        "min": minv,
        "spread": spread,
        "last_cote_used": last_cote
    }

    st.session_state.history.append(res)

    if len(st.session_state.history) > 20:
        st.session_state.history.pop(0)

    train_ai()
    return res

# ==========================================
# 🖥️ UI
# ==========================================
st.markdown("<h1 class='main-title'>JETX ANDR V14 STABLE</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1,2])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    h_in = st.text_input("HASH")
    t_in = st.text_input("TIME (HH:MM:SS)")
    c_ref = st.number_input("COTE REF", value=2.2)
    last_cote = st.number_input("LAST COTE", value=2.0)

    if st.button("RUN"):
        if h_in and len(t_in) == 8:
            st.session_state.last = run_engine(h_in, t_in, c_ref, last_cote)

    st.markdown("</div>", unsafe_allow_html=True)

    # RESET DATA (TSY VOAFAFA ANY LALINA)
    if st.sidebar.button("RESET DATA"):
        st.session_state.history = []
        if "last" in st.session_state:
            del st.session_state.last
        st.rerun()

with col2:
    if "last" in st.session_state:
        r = st.session_state.last

        st.markdown(f"""
        <div class="glass-card">
        <h2>{r['signal']}</h2>

        PROB: {r['x3_prob']}% | CONF: {r['conf']}

        <h1>{r['entry']}</h1>

        MIN: {r['min']} | MOY: {r['moy']} | MAX: {r['max']}

        <small>LAST COTE USED: {r['last_cote_used']}</small>
        </div>
        """, unsafe_allow_html=True)

st.markdown("### HISTORY")
if st.session_state.history:
    st.table(pd.DataFrame(st.session_state.history)[::-1])
