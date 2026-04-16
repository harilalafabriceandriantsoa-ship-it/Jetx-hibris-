import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG & ULTRA STYLE ----------------
st.set_page_config(page_title="JET X ANDR V9 ⚡ CYBER-PREDICT", layout="wide")

# CSS DESIGN "PREMIUM CYBERPUNK"
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');

    .stApp {
        background: radial-gradient(circle at center, #001212 0%, #000000 100%);
        color: #e0fbfb;
        font-family: 'Rajdhani', sans-serif;
    }

    /* Titre Stylé */
    .glitch-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        text-transform: uppercase;
        color: #00ffcc;
        text-shadow: 0 0 10px #00ffcc, 0 0 20px #00ffcc;
        margin-bottom: 20px;
        border-bottom: 1px solid rgba(0, 255, 204, 0.3);
        padding-bottom: 15px;
    }

    /* Card System */
    .main-card {
        background: rgba(0, 20, 20, 0.6);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 255, 204, 0.3);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 0 40px rgba(0, 0, 0, 0.5);
        text-align: center;
        transition: 0.4s ease;
    }
    
    .signal-box {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
        background: rgba(0, 0, 0, 0.3);
        border-left: 5px solid #00ffcc;
    }

    /* Time Blocks */
    .time-container {
        display: flex;
        justify-content: space-around;
        margin: 20px 0;
    }
    .time-item {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 15px;
        width: 45%;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .label-small { color: #888; font-size: 0.8rem; text-transform: uppercase; }
    .time-val { font-size: 1.6rem; font-weight: 700; color: #fff; }

    /* Cotes Grid */
    .cote-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 10px;
        margin: 20px 0;
    }
    .cote-box {
        background: linear-gradient(145deg, rgba(0,255,204,0.1), rgba(0,0,0,0.4));
        padding: 15px;
        border-radius: 12px;
        border-top: 1px solid rgba(0,255,204,0.2);
    }
    .val-main { font-size: 1.8rem; font-weight: 700; color: #00ffcc; }

    /* AI Badge */
    .ai-badge {
        display: inline-block;
        padding: 5px 15px;
        background: #ff00cc;
        color: white;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        box-shadow: 0 0 15px #ff00cc;
        margin-bottom: 10px;
    }

    /* Input Styling */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: rgba(0, 255, 204, 0.05) !important;
        color: #00ffcc !important;
        border: 1px solid rgba(0, 255, 204, 0.2) !important;
        border-radius: 10px !important;
    }

    /* Button Styling */
    .stButton>button {
        background: linear-gradient(90deg, #008080, #00ffcc) !important;
        color: black !important;
        font-weight: 700 !important;
        border: none !important;
        padding: 15px 30px !important;
        border-radius: 12px !important;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: 0.3s !important;
    }
    .stButton>button:hover {
        box-shadow: 0 0 25px #00ffcc !important;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# ---------------- ENGINE & LOGIC (FIXED) ----------------
if "log" not in st.session_state: st.session_state.log = []
if "model" not in st.session_state: st.session_state.model = RandomForestClassifier(n_estimators=150)
if "scaler" not in st.session_state: st.session_state.scaler = StandardScaler()
if "ready" not in st.session_state: st.session_state.ready = False

def train():
    data = [[h["prob"], h["moy"], h["max"], h["ref"], h["conf"], h["result"]] for h in st.session_state.log if h.get("result") is not None]
    if len(data) >= 6:
        df = pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"])
        if len(df["label"].unique()) > 1:
            Xs = st.session_state.scaler.fit_transform(df.drop("label", axis=1))
            st.session_state.model.fit(Xs, df["label"])
            st.session_state.ready = True

def predict(hash_str, h_act, last_cote):
    tz = pytz.timezone("Indian/Antananarivo")
    try: t = datetime.strptime(h_act, "%H:%M:%S")
    except: t = datetime.now(tz)
    
    h = hashlib.sha256(hash_str.encode()).hexdigest()
    seed = int(h[:12], 16)
    np.random.seed(seed % (2**32))
    
    norm = (int(h[12:20], 16) % 1000) / 100 + 1.2
    sec = t.hour*3600 + t.minute*60 + t.second
    
    base = norm * (1.25 if last_cote < 1.8 else 0.95)
    sims = np.random.lognormal(mean=np.log(base), sigma=0.22, size=15000)
    
    prob = round(np.clip(len([x for x in sims if x >= 2.0])/150, 5, 98.2), 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 95), 2)
    minv = round(moy * 0.52, 2)
    conf = round(np.clip((prob * moy) / 11, 5, 95), 1)
    
    # Timing Fix
    delay = ((int(h[20:28], 16) % 50) + ((sec % 60)//10) + int(norm * 2))
    delay = (delay // 5) * 5
    entry = t + timedelta(seconds=delay)
    sniper = entry + timedelta(seconds=18)
    
    # AI Score
    ai = "WAITING DATA"
    if st.session_state.ready:
        try:
            feat = st.session_state.scaler.transform(np.array([[prob, moy, maxv, last_cote, conf]]))
            ai = f"{round(st.session_state.model.predict_proba(feat)[0][1]*100, 1)}%"
        except: ai = "CALCULATING"

    # Signals
    if conf >= 78: sig, color, icon = "ULTRA SNIPER", "#ff00cc", "🎯"
    elif conf >= 60: sig, color, icon = "STRONG ENTRY", "#00ffcc", "⚡"
    elif conf >= 40: sig, color, icon = "TIMING WAIT", "#ffcc00", "⏳"
    else: sig, color, icon = "NO ENTRY", "#ff4d4d", "❌"

    return {
        "entry": entry.strftime("%H:%M:%S"), "sniper": sniper.strftime("%H:%M:%S"),
        "window": f"{ (sniper-timedelta(seconds=2)).strftime('%H:%M:%S') } - { (sniper+timedelta(seconds=2)).strftime('%H:%M:%S') }",
        "prob": prob, "moy": moy, "max": maxv, "min": minv, "conf": conf,
        "signal": sig, "color": color, "icon": icon, "ai": ai, "ref": last_cote, "result": None
    }

# ---------------- UI RENDER ----------------
st.markdown('<div class="glitch-title">JET X ANDR V9</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<p style="color:#00ffcc; text-transform:uppercase; letter-spacing:2px; font-weight:bold;">🛰️ System Input</p>', unsafe_allow_html=True)
    hash_in = st.text_input("SERVER HASH")
    time_in = st.text_input("LAST ROUND TIME")
    cote_in = st.number_input("LAST COTE", value=1.5, step=0.1)
    
    if st.button("ACTIVATE PREDICTION"):
        if hash_in and time_in:
            r = predict(hash_in, time_in, cote_in)
            st.session_state.log.append(r)
            train()
            st.rerun()

with col2:
    if st.session_state.log:
        r = st.session_state.log[-1]
        st.markdown(f"""
        <div class="main-card" style="border-top: 4px solid {r['color']};">
            <div class="ai-badge">AI ACCURACY: {r['ai']}</div>
            
            <div class="signal-box" style="color:{r['color']}; border-color:{r['color']};">
                {r['icon']} {r['signal']}
            </div>

            <div class="time-container">
                <div class="time-item">
                    <div class="label-small">Entry Time</div>
                    <div class="time-val" style="color:#00ffcc;">{r['entry']}</div>
                </div>
                <div class="time-item">
                    <div class="label-small">Sniper Peak</div>
                    <div class="time-val" style="color:#ff00cc;">{r['sniper']}</div>
                </div>
            </div>
            
            <p style="color:#888;">WINDOW: <span style="color:#fff;">{r['window']}</span></p>

            <div class="cote-grid">
                <div class="cote-box">
                    <div class="label-small">Min Safe</div>
                    <div class="val-main" style="color:#888;">{r['min']}x</div>
                </div>
                <div class="cote-box" style="background:rgba(0,255,204,0.15);">
                    <div class="label-small">Target</div>
                    <div class="val-main">{r['moy']}x</div>
                </div>
                <div class="cote-box">
                    <div class="label-small">Max Risk</div>
                    <div class="val-main" style="color:#ff00cc;">{r['max']}x</div>
                </div>
            </div>

            <div style="display:flex; justify-content:space-between; margin-top:15px; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;">
                <span style="color:#666;">PROBABILITY: <b style="color:#00ffcc;">{r['prob']}%</b></span>
                <span style="color:#666;">CONFIDENCE: <b style="color:#00ffcc;">{r['conf']}</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Result buttons
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ MARK WIN"):
                st.session_state.log[-1]["result"] = 1
                train(); st.rerun()
        with c2:
            if st.button("❌ MARK LOSE"):
                st.session_state.log[-1]["result"] = 0
                train(); st.rerun()

# Sidebar for history
with st.sidebar:
    st.title("📊 History")
    if st.session_state.log:
        for i, entry in enumerate(reversed(st.session_state.log)):
            res_icon = "⚪" if entry['result'] is None else ("✅" if entry['result']==1 else "❌")
            st.write(f"{res_icon} {entry['entry']} | {entry['moy']}x")
