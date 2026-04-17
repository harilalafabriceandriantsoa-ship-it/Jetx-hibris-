import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG & PREMIUM UI ----------------
st.set_page_config(page_title="ANDR-X AI V12.6 ⚡ GOLD TERMINAL", layout="centered")

st.markdown("""
<style>     
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Share+Tech+Mono&display=swap');
        
    .stApp {    
        background-color: #05050A;    
        background-image: radial-gradient(circle at 50% 0%, #002222 0%, #05050A 70%);    
        color: #00ffcc;    
        font-family: 'Share Tech Mono', monospace;    
    }    
    h1, h2, h3 {    
        font-family: 'Orbitron', sans-serif;    
        color: #00ffcc;    
        text-shadow: 0 0 15px rgba(0,255,204,0.5);    
        text-align: center;    
        letter-spacing: 2px;    
    }    
    .result-card {    
        background: rgba(0, 20, 20, 0.7);    
        border: 2px solid #00ffcc;    
        border-radius: 20px;    
        padding: 25px;    
        box-shadow: 0 0 30px rgba(0,255,204,0.2);    
        margin-top: 15px;    
        text-align: center;    
        backdrop-filter: blur(10px);    
    }    
    .time-grid {    
        display: flex;    
        justify-content: space-around;    
        margin-top: 20px;    
        gap: 8px;    
    }    
    .time-box {    
        background: #001111;    
        border: 1px solid rgba(0,255,204,0.4);    
        padding: 10px 5px;    
        border-radius: 8px;    
        text-align: center;    
        width: 32%;    
    }    
    .time-box span { font-size: 0.7rem; color: #888; display: block;}    
    .time-box strong { font-size: 1rem; font-family: 'Orbitron', sans-serif; color: #fff;}    

    .stTextInput>div>div>input, .stNumberInput>div>div>input {    
        background-color: #ffffff !important;    
        color: #000000 !important;    
        font-weight: bold !important;    
        border: 2px solid #00ffcc !important;    
        border-radius: 10px !important;    
    }    
    .stButton>button {    
        background: linear-gradient(90deg, #004d4d, #00ffcc) !important;    
        color: #000 !important; font-weight: bold !important;    
        font-family: 'Orbitron', sans-serif;    
        border-radius: 12px !important; width: 100%; height: 50px;    
    }
</style>    
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "pred_log" not in st.session_state: st.session_state.pred_log = []
if "auth" not in st.session_state: st.session_state.auth = False
if "ml_model" not in st.session_state: st.session_state.ml_model = RandomForestClassifier(n_estimators=150)
if "rl_score" not in st.session_state: st.session_state.rl_score = {"win": 0, "lose": 0}

# ---------------- FUNCTIONS ----------------
def reset_history():
    st.session_state.pred_log = []
    st.session_state.rl_score = {"win": 0, "lose": 0}
    st.rerun()

def train_ai():
    data = []
    for h in st.session_state.pred_log:
        if h.get("result") is not None:
            data.append([
                h["prob"], h["moy"], h["max"],
                float(h["ref_raw"]),
                h["confidence"],
                1 if h["result"] == "win" else 0
            ])

    if len(data) >= 5:
        try:
            df = pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"])
            X, y = df.drop("label", axis=1), df["label"]
            st.session_state.ml_model.fit(X, y)
        except:
            pass

# ---------------- V13 ENGINE ----------------
def v13_ultra_delay(t_obj, h_hex, h_int, last_cote):
    h_a, h_b = int(h_hex[8:14], 16), int(h_hex[14:20], 16)
    h_c, h_d = int(h_hex[20:26], 16), int(h_hex[26:32], 16)

    base = 18 + (h_int % 25)
    layers = (h_a % 19) + (h_b % 13) + (h_c % 11) + (h_d % 7)

    t_sec = t_obj.hour * 3600 + t_obj.minute * 60 + t_obj.second
    entropy = (t_sec % 90) // 3

    rl_bias = 0
    total = st.session_state.rl_score["win"] + st.session_state.rl_score["lose"]
    if total > 0:
        rl_bias = int((st.session_state.rl_score["win"] / total) * 10)

    final = base + layers + entropy + rl_bias + (int(last_cote * 3) % 17)
    res = final + ((h_a % 5) - (h_c % 4))

    return max(12, min(110, res))

# ---------------- MAIN ENGINE ----------------
def run_prediction(hash_str, h_act, last_cote):
    try:
        t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except:
        t_obj = datetime.now(pytz.timezone('Indian/Antananarivo'))

    h_hex = hashlib.sha256(hash_str.encode()).hexdigest()
    h_int = int(h_hex[:10], 16)
    np.random.seed(h_int % (2**32))

    base_val = (int(h_hex[10:15], 16) % 100) / 20 + 1.25
    sims = np.random.lognormal(mean=np.log(base_val), sigma=0.38, size=15000)

    prob = round(len([s for s in sims if s >= 2.0]) / 15000 * 100, 1)
    moy = round(np.mean(sims) * (1 + (last_cote / 18)), 2)

    conf = round((prob * moy) / 10, 1)

    delay = v13_ultra_delay(t_obj, h_hex, h_int, last_cote)
    e_time = t_obj + timedelta(seconds=delay)

    # ---------------- COTE ADAPTIVE ENGINE (NEW FIX) ----------------
    volatility = np.std(sims)
    momentum = np.log1p(prob) / 10
    hash_boost = (h_int % 7) * 0.01

    base_min = moy * (0.55 + (volatility % 0.10))
    base_max = moy * (1.60 + momentum)

    min_cote = round(max(1.10, base_min + hash_boost), 2)
    moy_cote = round(moy, 2)
    max_cote = round(base_max + hash_boost, 2)

    if conf > 90:
        sig, emo, col = "ULTRA SNIPER", "🔥", "#ff00cc"
    elif conf > 65:
        sig, emo, col = "STRONG BUY", "🎯", "#00ffcc"
    else:
        sig, emo, col = "WAITING / SKIP", "⏳", "#ffcc00"

    return {
        "h_ent": e_time.strftime("%H:%M:%S"),
        "h_early": (e_time - timedelta(seconds=2)).strftime("%H:%M:%S"),
        "h_late": (e_time + timedelta(seconds=2)).strftime("%H:%M:%S"),

        # FIXED COTE SYSTEM
        "min": min_cote,
        "moy": moy_cote,
        "max": max_cote,

        "prob": prob,
        "confidence": conf,
        "signal": sig,
        "emoji": emo,
        "color": col,
        "ref_raw": last_cote,
        "result": None
    }

# ---------------- UI ----------------
if not st.session_state.auth:
    st.markdown("<h1>⚡ ANDR-X LOGIN</h1>", unsafe_allow_html=True)
    if st.text_input("🔐 ACCESS CODE", type="password") == "2026":
        if st.button("ACTIVATE"):
            st.session_state.auth = True
            st.rerun()
    st.stop()

st.markdown("<h1>🚀 JET X ANDR-GOLD V12.6</h1>", unsafe_allow_html=True)

t1, t2 = st.tabs(["📊 ANALYSE", "📜 HISTORY"])

with t1:
    h_in = st.text_input("🔑 SERVER HASH")
    t_in = st.text_input("⏰ ROUND TIME (HH:MM:SS)")
    l_c = st.number_input("📉 LAST COTE", value=1.50)

    if st.button("🔥 EXECUTE ENGINE"):
        if h_in and t_in:
            st.session_state.pred_log.append(run_prediction(h_in, t_in, l_c))
            train_ai()
            st.rerun()

    if st.session_state.pred_log:
        r = st.session_state.pred_log[-1]

        st.markdown(f"""
        <div class="result-card" style="border-color: {r['color']};">
            <h2 style="color: {r['color']}; margin:0;">{r['emoji']} {r['signal']}</h2>
            <p style="color:#888;">PROB: {r['prob']}% | CONFIDENCE: {r['confidence']}</p>
            <div class="time-grid">
                <div class="time-box"><span>ENTRY</span><strong>{r['h_ent']}</strong></div>
                <div class="time-box"><span>EARLY</span><strong>{r['h_early']}</strong></div>
                <div class="time-box"><span>LATE</span><strong>{r['h_late']}</strong></div>
            </div>
            <div class="time-grid">
                <div class="time-box"><span>MIN</span><strong>{r['min']}</strong></div>
                <div class="time-box"><span>MOY</span><strong>{r['moy']}</strong></div>
                <div class="time-box"><span>MAX</span><strong>{r['max']}</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with t2:
    for e in reversed(st.session_state.pred_log):
        st.write(e)

with st.sidebar:
    st.markdown("### ⚙️ SYSTEM")
    st.write(f"WINS: {st.session_state.rl_score['win']} | LOSS: {st.session_state.rl_score['lose']}")
    if st.button("🗑️ RESET SESSION"):
        reset_history()
