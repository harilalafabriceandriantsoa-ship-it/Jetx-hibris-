import streamlit as st 
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG & PREMIUM DESIGN ----------------
st.set_page_config(page_title="JET X ANDR V10.5 ⚡ PRO ADAPTIVE", layout="wide")

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
if "rl_weight" not in st.session_state:
    st.session_state.rl_weight = {"ultra": 0.4, "strong": 0.5, "wait": 0.6}

# ---------------- MASTER RESET FUNCTION ----------------
def reset_system():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ---------------- SECURITY LOGIN ----------------
if not st.session_state.auth:
    st.markdown("<h1>🔐 V10.5 SECURITY</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1,1.5,1])
    with col2:
        pwd = st.text_input("SYSTEM KEY", type="password")
        if st.button("ACTIVATE ENGINE"):
            if pwd == "2026":
                st.session_state.auth = True
                st.rerun()
            else: st.error("ACCESS DENIED")
    st.stop()

# ---------------- CORE ENGINE V10.5 PRO ----------------
def predict_v10_5(hash_str, h_act, last_cote):
    tz = pytz.timezone("Indian/Antananarivo")
    try: t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except: t_obj = datetime.now(tz)
    
    # 1. HASH DECODING & ENTROPY
    h_hex = hashlib.sha256(hash_str.encode()).hexdigest()
    hash_val = int(h_hex[:12], 16)
    np.random.seed(hash_val % (2**32))
    
    # 2. DYNAMIC POWER BASED ON REF
    base_power = 1.0 if last_cote < 1.5 else 1.25
    norm = ((hash_val % 1000) / 1000) + base_power
    
    # 3. SIMULATION WITH ADAPTIVE SIGMA
    sigma_adj = 0.25 if last_cote < 1.5 else 0.18
    sims = np.random.lognormal(mean=np.log(norm), sigma=sigma_adj, size=15000)
    
    prob = round(np.clip(len([x for x in sims if x >= 2.0])/150, 2, 99), 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 95), 2)
    minv = round(moy * 0.52, 2)

    # 4. CONFIDENCE (HASH + PROBABILITY)
    hash_stability = (hash_val % 100)
    conf = round((prob * 0.6) + (hash_stability * 0.4), 1)

    # 5. STRICT ADAPTIVE SIGNAL LOGIC
    adj = 15 if last_cote < 1.50 else (5 if last_cote < 2.50 else -5)
    
    u_limit = 80 + adj
    s_limit = 68 + adj
    w_limit = 48 + adj

    if conf >= u_limit and moy >= 2.8:
        sig, s_type, color = "🔥 ULTRA X3+ SNIPER 🎯", "ultra", "#ff00cc"
    elif conf >= s_limit and moy >= 1.9:
        sig, s_type, color = "🟢 STRONG ENTRY ⚡", "strong", "#00ffcc"
    elif conf >= w_limit:
        sig, s_type, color = "🟡 TIMING WAIT ⏳", "wait", "#ffcc00"
    else:
        sig, s_type, color = "🔴 NO ENTRY ❌", "wait", "#ff4d4d"

    # 6. TIMING & DELAY (ULTRA PRECISION BOOSTED)

    sec = t_obj.hour*3600 + t_obj.minute*60 + t_obj.second

    h1 = int(h_hex[20:25], 16)
    h2 = int(h_hex[25:30], 16)
    h3 = int(h_hex[30:35], 16)

    base_delay = (
        (h1 % 25) +
        (h2 % 12) +
        (sec % 20) +
        int(norm * 4)
    )

    micro_adj = (h3 % 7)

    raw_delay = base_delay + micro_adj

    locked = (raw_delay // 5) * 5

    stability = ((sec % 10) // 2) * 2

    final_delay = locked + stability

    entry = t_obj + timedelta(seconds=final_delay)

    return {
        "entry": entry.strftime("%H:%M:%S"), 
        "sniper": (entry + timedelta(seconds=20)).strftime("%H:%M:%S"),
        "prob": prob, "moy": moy, "max": maxv, "min": minv, "conf": conf,
        "signal": sig, "type": s_type, "color": color, "ref": last_cote, "result": None
    }

# ---------------- MAIN UI ----------------
st.sidebar.button("🚨 MASTER RESET DATA", on_click=reset_system)
st.markdown("<h1>🚀 JET X ANDR V10.5 PRO</h1>", unsafe_allow_html=True)

t1, t2 = st.tabs(["📊 ANALYSE LIVE", "📜 HISTORY"])

with t1:
    c1, c2, c3 = st.columns(3)
    with c1: h_in = st.text_input("🔑 SERVER HASH")
    with c2: t_in = st.text_input("⏰ ROUND TIME (HH:MM:SS)")
    with c3: c_ref = st.number_input("📉 LAST COTE (REF)", value=1.5, step=0.01)

    if st.button("🔥 EXECUTE PRO ENGINE"):
        if h_in and t_in:
            st.session_state.log.append(predict_v10_5(h_in, t_in, c_ref))
            st.rerun()

    if st.session_state.log:
        r = st.session_state.log[-1]
        st.markdown(f"""
        <div class="card" style="border-top: 10px solid {r['color']};">
            <h2 style="color:{r['color']}; margin:0; font-family:Orbitron;">{r['signal']}</h2>
            <div style="display:flex; justify-content:center; gap:50px; margin:20px 0;">
                <div><small style="color:#888;">ENTRY</small><br><b style="font-size:2.2rem;">{r['entry']}</b></div>
                <div><small style="color:#888;">SNIPER</small><br><b style="font-size:2.2rem; color:#ff00cc;">{r['sniper']}</b></div>
            </div>
            <div class="cote-grid">
                <div class="cote-box">MIN<br><span class="val-main" style="color:#777;">{r['min']}x</span></div>
                <div class="cote-box" style="background:rgba(0,255,204,0.1);">TARGET<br><span class="val-main">{r['moy']}x</span></div>
                <div class="cote-box">MAX<br><span class="val-main" style="color:#ff00cc;">{r['max']}x</span></div>
            </div>
            <p style="font-size:0.9rem; color:#555;">PROB: {r['prob']}% | CONF: {r['conf']} | REF: {r['ref']}</p>
        </div>
        """, unsafe_allow_html=True)

        w, l = st.columns(2)
        with w:
            if st.button("✅ WIN"): st.session_state.log[-1]["result"] = 1
        with l:
            if st.button("❌ LOSE"): st.session_state.log[-1]["result"] = 0

with t2:
    if st.session_state.log:
        for entry in reversed(st.session_state.log):
            icon = "⚪" if entry['result'] is None else ("✅" if entry['result']==1 else "❌")
            st.markdown(f"**{icon} {entry['entry']}** | Target: `{entry['moy']}x` | Conf: `{entry['conf']}` | Ref: `{entry['ref']}`")
