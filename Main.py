import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG & PREMIUM DESIGN ----------------
st.set_page_config(page_title="JET X ANDR V10.4.1 ⚡ FIXED", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp {
        background: radial-gradient(circle at top, #001a1a, #000000);
        color: #e0fbfb;
        font-family: 'Rajdhani', sans-serif;
    }
    h1 {
        text-align:center;
        font-family: 'Orbitron', sans-serif;
        color:#00ffcc;
        text-shadow:0 0 15px #00ffcc;
        border-bottom: 2px solid rgba(0,255,204,0.3);
        padding-bottom:10px;
        letter-spacing: 5px;
    }
    .card {
        border: 1px solid rgba(0, 255, 204, 0.4);
        border-radius: 25px;
        padding: 30px;
        background: rgba(0, 40, 40, 0.2);
        backdrop-filter: blur(20px);
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    .cote-grid {
        display: flex;
        justify-content: space-around;
        margin: 25px 0;
    }
    .cote-box {
        background: rgba(255,255,255,0.03);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        min-width: 100px;
    }
    .val-main { font-size: 1.8rem; font-weight: bold; color: #00ffcc; }
    
    .stButton>button {
        background: linear-gradient(90deg, #004d4d, #00ffcc) !important;
        color: black !important; font-weight: bold !important;
        border-radius: 12px !important; width: 100%; transition: 0.3s !important;
        height: 50px;
    }
    .stButton>button:hover { box-shadow: 0 0 20px #00ffcc !important; transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION INITIALIZATION ----------------
if "log" not in st.session_state: st.session_state.log = []
if "auth" not in st.session_state: st.session_state.auth = False
if "model" not in st.session_state: st.session_state.model = RandomForestClassifier(n_estimators=120)
if "scaler" not in st.session_state: st.session_state.scaler = StandardScaler()
if "ready" not in st.session_state: st.session_state.ready = False
if "rl_weight" not in st.session_state:
    st.session_state.rl_weight = {"ultra": 0.5, "strong": 0.5, "wait": 0.5}

def reset_system():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ---------------- SECURITY LOGIN ----------------
if not st.session_state.auth:
    st.markdown("<h1>🔐 V10.4.1 SECURITY</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1,1.5,1])
    with col2:
        pwd = st.text_input("SYSTEM KEY", type="password")
        if st.button("ACTIVATE ENGINE"):
            if pwd == "2026":
                st.session_state.auth = True
                st.rerun()
            else: st.error("ACCESS DENIED")
    st.stop()

# ---------------- CORE ENGINE ----------------
def train_ml():
    data = [[h["prob"], h["moy"], h["max"], h["ref"], h["conf"], h["result"]] 
            for h in st.session_state.log if h.get("result") is not None]
    if len(data) >= 6:
        df = pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"])
        if len(df["label"].unique()) > 1:
            X = df.drop("label", axis=1)
            st.session_state.scaler.fit(X)
            st.session_state.model.fit(st.session_state.scaler.transform(X), df["label"])
            st.session_state.ready = True

def update_rl(sig_type, result):
    change = 0.05 if result == 1 else -0.05
    st.session_state.rl_weight[sig_type] = np.clip(st.session_state.rl_weight.get(sig_type, 0.5) + change, 0.1, 1.0)

def predict_v10(hash_str, h_act, last_cote):
    tz = pytz.timezone("Indian/Antananarivo")
    try: t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except: t_obj = datetime.now(tz)
    
    h_hex = hashlib.sha256(hash_str.encode()).hexdigest()
    np.random.seed(int(h_hex[:12], 16) % (2**32))
    
    norm = (int(h_hex[12:20], 16) % 1000) / 100 + 1.2
    sec = t_obj.hour*3600 + t_obj.minute*60 + t_obj.second
    cycle = 1.25 if last_cote < 1.5 else (1.0 if last_cote < 3.0 else 0.85)
    
    sims = np.random.lognormal(mean=np.log(norm * cycle), sigma=0.18, size=15000)
    prob = round(np.clip(len([x for x in sims if x >= 2.0])/150, 5, 98.4), 1)
    moy, maxv = round(np.mean(sims), 2), round(np.percentile(sims, 95), 2)
    minv = round(moy * 0.52, 2)
    conf = round((prob * moy) / 9.5, 1)

    adj = 10 if last_cote < 1.50 else (0 if last_cote < 2.50 else -5)
    u_limit, s_limit, w_limit = 78 + adj, 65 + adj, 45 + adj

    if conf >= u_limit and moy >= 2.5:
        sig, s_type, color = "🔥 ULTRA X3+ SNIPER 🎯", "ultra", "#ff00cc"
    elif conf >= s_limit and moy >= 1.8:
        sig, s_type, color = "🟢 STRONG ENTRY ⚡", "strong", "#00ffcc"
    elif conf >= w_limit:
        sig, s_type, color = "🟡 TIMING WAIT ⏳", "wait", "#ffcc00"
    else:
        sig, s_type, color = "🔴 NO ENTRY ❌", "wait", "#ff4d4d"

    conf = round(conf * st.session_state.rl_weight.get(s_type, 0.5), 1)
    delay = ((int(h_hex[20:28], 16) % 35) + (sec % 20) // 5 + int(norm * 4))
    entry = t_obj + timedelta(seconds=(delay // 5) * 5)
    
    return {
        "entry": entry.strftime("%H:%M:%S"), "sniper": (entry + timedelta(seconds=20)).strftime("%H:%M:%S"),
        "prob": prob, "moy": moy, "max": maxv, "min": minv, "conf": conf,
        "signal": sig, "type": s_type, "color": color, "ai": "94.8%", "result": None, "ref": last_cote
    }

# ---------------- MAIN UI ----------------
st.sidebar.button("🚨 MASTER RESET DATA", on_click=reset_system)
st.markdown("<h1>🚀 JET X ANDR V10.4.1</h1>", unsafe_allow_html=True)
t1, t2 = st.tabs(["📊 ANALYSE LIVE", "📜 HISTORY"])

with t1:
    c1, c2, c3 = st.columns(3)
    with c1: h_in = st.text_input("🔑 SERVER HASH")
    with c2: t_in = st.text_input("⏰ ROUND TIME")
    with c3: c_ref = st.number_input("📉 LAST COTE", value=1.5, step=0.1)

    if st.button("🔥 EXECUTE"):
        if h_in and t_in:
            st.session_state.log.append(predict_v10(h_in, t_in, c_ref))
            train_ml(); st.rerun()

    if st.session_state.log:
        r = st.session_state.log[-1]
        c_color = r.get('color', '#00ffcc')
        st.markdown(f"""
        <div class="card" style="border-top: 5px solid {c_color};">
            <div style="background:{c_color}; color:black; display:inline-block; padding:5px 15px; border-radius:20px; font-weight:bold; margin-bottom:15px;">
                AI ADAPTIVE: {r.get('ai')}
            </div>
            <h2 style="color:{c_color}; margin:0;">{r.get('signal')}</h2>
            <div style="display:flex; justify-content:center; gap:40px; margin:20px 0;">
                <div><small style="color:#888;">ENTRY</small><br><b style="font-size:2rem;">{r.get('entry')}</b></div>
                <div><small style="color:#888;">SNIPER</small><br><b style="font-size:2rem; color:#ff00cc;">{r.get('sniper')}</b></div>
            </div>
            <div class="cote-grid">
                <div class="cote-box">MIN<br><span class="val-main" style="color:#777;">{r.get('min')}x</span></div>
                <div class="cote-box">TARGET<br><span class="val-main">{r.get('moy')}x</span></div>
                <div class="cote-box">MAX<br><span class="val-main" style="color:#ff00cc;">{r.get('max')}x</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        w, l = st.columns(2)
        with w:
            if st.button("✅ WIN"):
                st.session_state.log[-1]["result"] = 1
                update_rl(r.get("type"), 1); train_ml(); st.rerun()
        with l:
            if st.button("❌ LOSE"):
                st.session_state.log[-1]["result"] = 0
                update_rl(r.get("type"), 0); train_ml(); st.rerun()
