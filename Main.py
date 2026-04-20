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
st.set_page_config(page_title="ANDR-X V13.5 PRO-SYNC", layout="wide")

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
    
    .stat-val { font-size: 1.8rem; font-weight: 700; color: #00ffcc; }
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

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


# ==========================================
# 🔐 LOGIN
# ==========================================
if not st.session_state.authenticated:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    password = st.text_input("Password", type="password")

    if st.button("LOGIN"):
        if password == "2026":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Wrong password")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# ==========================================
# TIME
# ==========================================
def get_tz_now():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))


# ==========================================
# AI TRAINING (stable)
# ==========================================
def train_real_ai():
    data = []
    for h in st.session_state.history:
        if "result" in h:
            label = 1 if h["result"] == "win" else 0
            data.append([h["x3_prob"], h["conf"], h["moy"], h["spread"], label])

    if len(data) < 6:
        return

    df = pd.DataFrame(data, columns=["prob","conf","moy","spread","label"])
    X = df[["prob","conf","moy","spread"]]
    y = df["label"]

    model = RandomForestClassifier(n_estimators=150, max_depth=6)
    model.fit(X, y)

    st.session_state.ml_model = model
    st.session_state.ml_ready = True


def ai_predict(prob, conf, moy, spread):
    if not st.session_state.ml_ready:
        return None
    try:
        X = np.array([[prob, conf, moy, spread]])
        return round(st.session_state.ml_model.predict_proba(X)[0][1] * 100, 1)
    except:
        return None


# ==========================================
# ENTRY TIME
# ==========================================
def hyper_time_calc(hash_val, spread, t_in, strength):
    now = get_tz_now()
    try:
        t_obj = datetime.strptime(t_in.strip(), "%H:%M:%S").time()
        base_time = datetime.combine(now.date(), t_obj)
    except:
        base_time = now

    hash_shift = (int(hash_val[:6], 16) % 12) - 4

    base_delay = 18 if strength > 70 else 22 if strength > 50 else 28

    final_seconds = int(base_delay + (spread * 1.1) + hash_shift)

    # 🛡️ STABILITY FIX
    final_seconds = max(15, min(60, final_seconds))

    return (base_time + timedelta(seconds=final_seconds)).strftime("%H:%M:%S")


# ==========================================
# MAIN ENGINE (STABLE VERSION)
# ==========================================
def run_ultra_analysis(h_in, t_in, c_ref, last_cote):

    h_num = int(hashlib.sha256(h_in.encode()).hexdigest()[:16], 16)
    h_norm = (h_num % 1000) / 1000
    np.random.seed(h_num & 0xffffffff)

    # 🛡️ FIX LAST COTE SPIKE (IMPORTANT)
    if last_cote > 6:
        last_cote = 4.0
    elif last_cote > 4:
        last_cote = (last_cote + 4) / 2

    variance_scale = 0.25 + (h_norm * 0.15)

    base_mean = np.log((c_ref + last_cote) / 2 + 0.05)

    sims = np.random.lognormal(base_mean, variance_scale, 12000)

    prob_x3_real = np.mean(sims >= 3.0) * 100

    # 🛡️ STABILITY CLAMP
    prob_x3_real = np.clip(prob_x3_real, 5, 90)

    moy = np.exp(np.mean(np.log(sims)))
    max_v = np.percentile(sims, 98)
    min_v = np.percentile(sims, 5)

    spread = max_v - min_v

    conf = (prob_x3_real * 0.7) + ((moy / c_ref) * 30)
    conf = max(20, min(99, conf))

    ai_score = ai_predict(prob_x3_real, conf, moy, spread)

    final_strength = (prob_x3_real * 0.6 + (ai_score or 50) * 0.4)

    entry_time = hyper_time_calc(h_in, spread, t_in, final_strength)

    # 🚨 STRONG FILTER (REDUCE LOSS)
    if prob_x3_real < 45 or conf < 50 or moy < 1.6:
        signal = "⚠️ SKIP (SAFE MODE)"
        color = "#ff4444"
    elif final_strength > 70:
        signal = "💎 ULTRA BUY"
        color = "#ff00cc"
    elif final_strength > 55:
        signal = "🟢 BUY"
        color = "#00ffcc"
    else:
        signal = "⚡ SCALP"
        color = "#ffff00"

    res = {
        "entry": entry_time,
        "signal": signal,
        "color": color,
        "x3_prob": round(prob_x3_real, 1),
        "conf": round(conf, 1),
        "spread": round(spread, 2),
        "moy": round(moy, 2),
        "max": round(max_v, 2),
        "min": round(min_v, 2),
        "ai_score": ai_score,
        "last_cote_used": last_cote
    }

    st.session_state.history.append(res)

    if len(st.session_state.history) > 20:
        st.session_state.history.pop(0)

    train_real_ai()
    return res


# ==========================================
# UI
# ==========================================
st.markdown("<h1 class='main-title'>JETX ANDR V14 STABLE AI</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1,2])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    h_in = st.text_input("HASH")
    t_in = st.text_input("TIME (HH:MM:SS)")
    c_ref = st.number_input("COTE REF", value=2.2)
    last_cote = st.number_input("LAST COTE", value=2.0)

    if st.button("RUN AI"):
        if h_in and len(t_in) == 8:
            st.session_state.last_res = run_ultra_analysis(h_in, t_in, c_ref, last_cote)

    st.markdown("</div>", unsafe_allow_html=True)

    if st.sidebar.button("RESET DATA"):
        st.session_state.history = []
        st.rerun()

with col2:
    if "last_res" in st.session_state:
        r = st.session_state.last_res

        st.markdown(f"""
        <div class="glass-card" style="border-left: 8px solid {r['color']}">
        <h2 style="color:{r['color']}">{r['signal']}</h2>

        <div style="display:flex; justify-content:space-between;">
        <div>PROB<br><b>{r['x3_prob']}%</b></div>
        <div>CONF<br><b>{r['conf']}%</b></div>
        <div>VOL<br><b>{r['spread']}</b></div>
        </div>

        <h1 style="text-align:center;">{r['entry']}</h1>

        <div style="display:flex; justify-content:space-around;">
        <div>MIN<br><b>{r['min']}x</b></div>
        <div>MOY<br><b>{r['moy']}x</b></div>
        <div>MAX<br><b>{r['max']}x</b></div>
        </div>

        <small>LAST COTE USED: {r['last_cote_used']}</small>

        </div>
        """, unsafe_allow_html=True)

st.markdown("### HISTORY")
if st.session_state.history:
    st.table(pd.DataFrame(st.session_state.history)[::-1])
