import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG & PREMIUM UI ----------------
st.set_page_config(page_title="ANDR-X AI V12.5.1 ⚡ GOLD TERMINAL", layout="centered")

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
    
    .cote-grid {
        display: flex;
        justify-content: space-around;
        margin: 20px 0;
    }
    .cote-box {
        background: rgba(0,0,0,0.4);
        border: 1px solid rgba(0,255,204,0.3);
        padding: 15px;
        border-radius: 12px;
        width: 30%;
    }
    .cote-box span { font-size: 0.7rem; color: #888; display: block; margin-bottom: 5px; text-transform: uppercase;}
    .cote-box strong { font-size: 1.4rem; font-family: 'Orbitron', sans-serif; color: #fff;}
    
    .time-grid {
        display: flex;
        justify-content: space-around;
        margin-top: 20px;
    }
    .time-box {
        background: #001111;
        border: 1px solid rgba(0,255,204,0.4);
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        width: 30%;
    }
    .time-box span { font-size: 0.7rem; color: #888; display: block;}
    .time-box strong { font-size: 1.1rem; font-family: 'Orbitron', sans-serif;}

    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: 2px solid #00ffcc !important;
        border-radius: 10px !important;
        font-size: 1.1rem !important;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #004d4d, #00ffcc) !important;
        color: #000 !important; font-weight: bold !important;
        font-family: 'Orbitron', sans-serif;
        border-radius: 12px !important; width: 100%; height: 50px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "pred_log" not in st.session_state: st.session_state.pred_log = []
if "auth" not in st.session_state: st.session_state.auth = False
if "ml_model" not in st.session_state: st.session_state.ml_model = RandomForestClassifier(n_estimators=150)
if "ml_ready" not in st.session_state: st.session_state.ml_ready = False
if "rl_score" not in st.session_state: st.session_state.rl_score = {"win": 0, "lose": 0}

# ---------------- CORE LOGIC ----------------
def reset_history():
    st.session_state.pred_log = []
    st.session_state.rl_score = {"win": 0, "lose": 0}
    st.rerun()

def ultra_sync_delay(t_obj, raw_delay):
    server_tick = 6
    t_seconds = t_obj.hour*3600 + t_obj.minute*60 + t_obj.second
    phase = t_seconds % server_tick
    aligned = raw_delay - phase
    if phase >= 4: aligned -= 1
    elif phase <= 1: aligned += 1
    if aligned < 12: aligned += server_tick * 2
    return aligned

def compute_entry_window(t_obj, final_delay):
    base_time = t_obj + timedelta(seconds=final_delay)
    return {
        "main": base_time.strftime("%H:%M:%S"),
        "early": (base_time - timedelta(seconds=2)).strftime("%H:%M:%S"),
        "late": (base_time + timedelta(seconds=2)).strftime("%H:%M:%S")
    }

# ---------------- AI ENGINE ----------------
def train_ai():
    data = []
    for h in st.session_state.pred_log:
        if h.get("result") is not None and "prob" in h:
            data.append([h["prob"], h["moy"], h["max"], float(h["ref_raw"]), h["confidence"], 1 if h["result"] == "win" else 0])
    if len(data) >= 5:
        try:
            df = pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"])
            X = df.drop("label", axis=1)
            y = df["label"]
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            model = RandomForestClassifier(n_estimators=150)
            model.fit(X_scaled, y)
            st.session_state.ml_model, st.session_state.scaler, st.session_state.ml_ready = model, scaler, True
        except: pass

def run_prediction(hash_str, h_act, last_cote):
    try: t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except: t_obj = datetime.now(pytz.timezone('Indian/Antananarivo'))

    hash_hex = hashlib.sha256(hash_str.encode()).hexdigest()
    hash_int = int(hash_hex[:10], 16)
    np.random.seed(hash_int % (2**32))

    threshold_adj = 15 if last_cote < 1.5 else -5 if last_cote > 2.5 else 5
    base_val = (int(hash_hex[10:15], 16) % 100) / 20 + 1.2
    sims = np.random.lognormal(mean=np.log(base_val), sigma=0.35, size=15000)
    
    prob = round(len([s for s in sims if s >= 2.0])/15000 * 100, 1)
    moy = round(np.mean(sims) * (1 + (last_cote/20)), 2)
    min_v, max_v = round(moy * 0.7, 2), round(moy * 1.8, 2)
    confidence = round((prob * moy) / 10, 1)
    
    total = st.session_state.rl_score["win"] + st.session_state.rl_score["lose"]
    if total > 0: confidence = round(confidence * (0.8 + (st.session_state.rl_score["win"]/total)), 1)

    final_delay = ultra_sync_delay(t_obj, 20 + (hash_int % 15))
    times = compute_entry_window(t_obj, final_delay)

    if confidence > (85 + threshold_adj): sig, emo, col = "ULTRA SNIPER", "🔥", "#ff00cc"
    elif confidence > (70 + threshold_adj): sig, emo, col = "STRONG BUY", "🎯", "#00ffcc"
    else: sig, emo, col = "WAITING / SKIP", "⏳", "#ffcc00"

    return {
        "h_ent": times["main"], "h_early": times["early"], "h_late": times["late"],
        "min": min_v, "moy": moy, "max": max_v, "prob": prob, "confidence": confidence,
        "signal": sig, "emoji": emo, "color": col, "ref_raw": last_cote, "result": None
    }

# ---------------- LOGIN ----------------
if not st.session_state.auth:
    st.markdown("<h1>⚡ ANDR-X V12.5 LOGIN</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("🔐 ACCESS CODE", type="password")
        if st.button("ACTIVATE TERMINAL"):
            if pwd == "2026": st.session_state.auth = True; st.rerun()
    st.stop()

# ---------------- UI MAIN ----------------
with st.sidebar:
    st.markdown("### ⚙️ SYSTEM")
    st.write(f"WINS: {st.session_state.rl_score['win']} | LOSS: {st.session_state.rl_score['lose']}")
    if st.button("🗑️ RESET SESSION"): reset_history()

st.markdown("<h1>🚀 JET X ANDR-GOLD V12.5</h1>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📊 LIVE ANALYSE", "📜 HISTORY"])

with tab1:
    hash_in = st.text_input("🔑 SERVER HASH")
    h_in = st.text_input("⏰ ROUND TIME (HH:MM:SS)")
    l_cote = st.number_input("📉 LAST COTE (REFERENCE)", value=1.50, step=0.1)

    if st.button("🔥 EXECUTE GOLD ENGINE"):
        if hash_in and h_in:
            res = run_prediction(hash_in, h_in, l_cote)
            st.session_state.pred_log.append(res)
            train_ai()
            st.rerun()

    if st.session_state.pred_log:
        r = st.session_state.pred_log[-1]
        # FIKAMBANANA SAFE (Using .get to avoid KeyError)
        m_val = r.get('min', '0.00')
        mo_val = r.get('moy', '0.00')
        mx_val = r.get('max', '0.00')
        
        st.markdown(f"""
        <div class="result-card" style="border-color: {r.get('color','#00ffcc')};">
            <h2 style="color: {r.get('color','#00ffcc')}; margin:0;">{r.get('emoji','')} {r.get('signal','--')}</h2>
            <p style="color:#888; font-size:0.8rem;">PROB: {r.get('prob',0)}% | CONFIDENCE: {r.get('confidence',0)}</p>
            <div class="cote-grid">
                <div class="cote-box"><span>Cote Min</span><strong>{m_val}x</strong></div>
                <div class="cote-box" style="border-color:#00ffcc; background:rgba(0,255,204,0.1);">
                    <span style="color:#00ffcc;">Target Moyen</span><strong style="color:#00ffcc;">{mo_val}x</strong>
                </div>
                <div class="cote-box"><span>Cote Max</span><strong style="color:#ff00cc;">{mx_val}x</strong></div>
            </div>
            <div class="time-grid">
                <div class="time-box"><span>🟢 EARLY</span><strong style="color:#00ffcc;">{r.get('h_early','--')}</strong></div>
                <div class="time-box" style="border-color:#ff00cc; transform:scale(1.1);">
                    <span style="color:#ff00cc;">⚡ MAIN ENTRY</span><strong style="color:#ff00cc;">{r.get('h_ent','--')}</strong>
                </div>
                <div class="time-box"><span>🔵 LATE</span><strong style="color:#0088ff;">{r.get('h_late','--')}</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ WIN"):
                st.session_state.pred_log[-1]["result"] = "win"
                st.session_state.rl_score["win"] += 1
                train_ai(); st.rerun()
        with c2:
            if st.button("❌ LOSE"):
                st.session_state.pred_log[-1]["result"] = "lose"
                st.session_state.rl_score["lose"] += 1
                train_ai(); st.rerun()

with tab2:
    for e in reversed(st.session_state.pred_log):
        res_txt = e.get('result', 'PENDING')
        color = "#00ffcc" if res_txt=="win" else "#ff4d4d" if res_txt=="lose" else "#888"
        st.markdown(f"""
        <div style="border-left: 4px solid {color}; background:rgba(255,255,255,0.02); padding:10px; margin-bottom:5px; border-radius:5px;">
            <strong style="color:#fff;">{e.get('h_ent','--')}</strong> | {e.get('signal','--')} | Target: {e.get('moy','0')}x 
            <span style="float:right; color:{color};">{res_txt}</span>
        </div>
        """, unsafe_allow_html=True)
