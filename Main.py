import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG & PREMIUM UI ----------------
st.set_page_config(page_title="ANDR-X AI V3 ⚡ TERMINAL", layout="centered")

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
        background: rgba(0, 20, 20, 0.6);
        border: 1px solid #00ffcc;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 0 20px rgba(0,255,204,0.15);
        margin-top: 15px;
        margin-bottom: 15px;
        text-align: center;
        backdrop-filter: blur(5px);
    }
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
    .time-box span { font-size: 0.8rem; color: #888; display: block; margin-bottom: 5px;}
    .time-box strong { font-size: 1.2rem; font-family: 'Orbitron', sans-serif;}
    
    .stButton>button {
        background: linear-gradient(90deg, #004d4d, #00ffcc) !important;
        color: #000 !important; 
        font-weight: bold !important; 
        font-family: 'Orbitron', sans-serif;
        border-radius: 8px !important; 
        border: none !important;
        transition: 0.3s !important;
        height: 50px;
        letter-spacing: 1px;
    }
    .stButton>button:hover { 
        box-shadow: 0 0 20px #00ffcc !important; 
        transform: translateY(-2px); 
    }
    
    /* Input styling */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: rgba(0, 255, 204, 0.05) !important;
        color: #fff !important;
        border: 1px solid rgba(0,255,204,0.3) !important;
        border-radius: 8px !important;
        font-family: 'Share Tech Mono', monospace !important;
    }
    .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
        border-color: #00ffcc !important;
        box-shadow: 0 0 10px rgba(0,255,204,0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "pred_log" not in st.session_state: st.session_state.pred_log = []
if "auth" not in st.session_state: st.session_state.auth = False
if "ml_model" not in st.session_state: st.session_state.ml_model = RandomForestClassifier(n_estimators=120)
if "ml_ready" not in st.session_state: st.session_state.ml_ready = False

# 🧠 RL MEMORY
if "rl_score" not in st.session_state:
    st.session_state.rl_score = {"win": 0, "lose": 0}

# ---------------- RESET FUNCTION ----------------
def reset_history():
    st.session_state.pred_log = []
    st.session_state.rl_score = {"win": 0, "lose": 0}

# ---------------- V4 ULTRA SYNC ----------------
def ultra_sync_delay(t_obj, raw_delay):
    server_tick = 6
    t_seconds = t_obj.hour*3600 + t_obj.minute*60 + t_obj.second
    phase = t_seconds % server_tick

    aligned = raw_delay - phase

    if phase >= 4:
        aligned -= 1
    elif phase <= 1:
        aligned += 1

    if aligned < 12:
        aligned += server_tick * 2

    return aligned

# ---------------- DOUBLE ENTRY ----------------
def compute_entry_window(t_obj, final_delay):
    base_time = t_obj + timedelta(seconds=final_delay)
    early = base_time - timedelta(seconds=2)
    late = base_time + timedelta(seconds=2)

    return {
        "entry_main": base_time.strftime("%H:%M:%S"),
        "entry_early": early.strftime("%H:%M:%S"),
        "entry_late": late.strftime("%H:%M:%S")
    }

# ---------------- LOGIN ----------------
if not st.session_state.auth:
    st.markdown("<h1>⚡ ANDR-X AI V3 TERMINAL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888;'>SECURE ACCESS REQUIRED</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("🔐 SECURITY CODE", type="password")
        if st.button("ACTIVATE SYSTEM"):
            if pwd == "2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ ACCESS DENIED")
    st.stop()

# ---------------- AI TRAIN ----------------
def build_dataset(history):
    data = []
    for h in history:
        if all(k in h for k in ["prob", "moy", "max", "ref", "confidence", "result"]):
            if h["result"] is not None:
                data.append([
                    h["prob"], h["moy"], h["max"], float(h["ref"]), h["confidence"],
                    1 if h["result"] == "win" else 0
                ])

    if len(data) < 5: return None
    return pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"])

def train_ai():
    df = build_dataset(st.session_state.pred_log)
    if df is None: return

    try:
        X = df.drop("label", axis=1)
        y = df["label"]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = RandomForestClassifier(n_estimators=150)
        model.fit(X_scaled, y)

        st.session_state.ml_model = model
        st.session_state.scaler = scaler
        st.session_state.ml_ready = True
    except:
        pass

def ai_predict(features):
    if not st.session_state.ml_ready or "scaler" not in st.session_state:
        return "LEARNING..."
    
    try:
        X = np.array(features).reshape(1, -1)
        X = st.session_state.scaler.transform(X)
        return f"{round(st.session_state.ml_model.predict_proba(X)[0][1] * 100, 1)}%"
    except:
        return "ERROR"

# ---------------- RL UPDATE ----------------
def update_rl(result):
    if result == "win":
        st.session_state.rl_score["win"] += 1
    elif result == "lose":
        st.session_state.rl_score["lose"] += 1

# ---------------- ENGINE ----------------
def run_prediction(hash_str, h_act, last_cote):
    try:
        t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except:
        tz_mg = pytz.timezone('Indian/Antananarivo')
        t_obj = datetime.now(tz_mg)

    seed_global = int(hashlib.sha256((hash_str + h_act).encode()).hexdigest(), 16) % (2**32)
    np.random.seed(seed_global)

    hash_hex = hashlib.sha256(hash_str.encode()).hexdigest()
    hash_int = int(hash_hex[:8], 16) % 1000
    hash_norm = (hash_int / 100) + 1.1

    t_seconds = t_obj.hour*3600 + t_obj.minute*60 + t_obj.second
    time_factor = (t_seconds % 300) / 300

    if last_cote < 1.5: cycle = 0.8
    elif last_cote < 1.8: cycle = 1.0
    elif last_cote <= 2.5: cycle = 1.3
    elif last_cote <= 3: cycle = 1.1
    else: cycle = 0.7

    ref_val = 2.1 if hash_norm < 2 else 2.2 if hash_norm < 3 else 2.3
    ref_val += time_factor * 0.2

    base = hash_norm * ref_val * cycle * (1 + time_factor)
    sigma = 0.25 + (hash_norm / 10)

    sims = np.random.lognormal(mean=np.log(base), sigma=sigma, size=15000)
    success = [s for s in sims if s >= 3.0]
    prob = round(len(success)/15000 * 100, 1)

    log_sims = np.log(sims + 1)
    moy_raw = np.exp(np.mean(log_sims))
    max_raw = np.exp(np.percentile(log_sims, 95))

    moy = round(moy_raw / 1.4, 2)
    maxv = round(max_raw / 1.2, 2)
    confidence = round((prob * moy)/10, 1)

    # RL influence
    total = st.session_state.rl_score["win"] + st.session_state.rl_score["lose"]
    if total > 0:
        winrate = st.session_state.rl_score["win"] / total
        confidence = round(confidence * (0.8 + winrate), 1)

    # --- HEURE V4 ULTRA SYNC ---
    hash_time = int(hash_hex[8:16], 16)
    hash_time2 = int(hash_hex[16:24], 16)
    hash_time3 = int(hash_hex[24:32], 16)

    layer1 = hash_time % 18
    layer2 = hash_time2 % 10
    layer3 = hash_time3 % 6

    if last_cote < 1.5: dynamic_boost = 8
    elif last_cote < 2.5: dynamic_boost = 5
    else: dynamic_boost = 2

    micro = int((hash_norm % 1) * 6)
    raw_delay = 18 + layer1 + layer2 + layer3 + dynamic_boost + micro
    final_delay = ultra_sync_delay(t_obj, raw_delay)

    # DOUBLE ENTRY
    entry_window = compute_entry_window(t_obj, final_delay)

    h_ent = entry_window["entry_main"]
    h_early = entry_window["entry_early"]
    h_late = entry_window["entry_late"]

    if last_cote > 3: signal, emoji, color = "SKIP ZONE", "❌", "#ff4d4d"
    elif prob < 40 or moy < 2.3: signal, emoji, color = "SKIP ZONE", "❌", "#ff4d4d"
    elif prob < 55: signal, emoji, color = "TIMING WAIT", "⏳", "#ffcc00"
    elif confidence > 12: signal, emoji, color = "STRONG BUY", "🔥", "#ff00cc"
    else: signal, emoji, color = "NORMAL BUY", "🎯", "#00ffcc"

    features = [prob, moy, maxv, ref_val, confidence]
    ai_score = ai_predict(features)

    return {
        "h_act": h_act, "h_ent": h_ent, "h_early": h_early, "h_late": h_late,
        "hash": hash_str[:10]+"...", "ref": round(ref_val,2),
        "prob": prob, "moy": moy, "max": maxv, "confidence": confidence,
        "signal": signal, "emoji": emoji, "color": color, "ai_score": ai_score, "result": None
    }

# ---------------- UI SIDEBAR ----------------
with st.sidebar:
    st.markdown("### ⚙️ SYSTEM CONTROL")
    st.markdown(f"**RL WINS:** {st.session_state.rl_score['win']} | **LOSSES:** {st.session_state.rl_score['lose']}")
    if st.button("🗑️ RESET HISTORIQUE"):
        reset_history()
        st.rerun()

# ---------------- UI MAIN ----------------
st.markdown("<h1>🚀 ANDR-X AI V3 ⚡ TERMINAL</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 ANALYSE EN DIRECT", "📜 HISTORIQUE DES SESSIONS"])

with tab1:
    col_h, col_t, col_c = st.columns(3)
    with col_h: hash_in = st.text_input("🔑 HASH SERVEUR")
    with col_t: h_in = st.text_input("⏰ HEURE (HH:MM:SS)")
    with col_c: last_cote = st.number_input("📉 CÔTE PRÉCÉDENTE", value=1.5, step=0.1)

    if st.button("🚀 EXECUTER L'ANALYSE"):
        if hash_in and h_in:
            res = run_prediction(hash_in, h_in, last_cote)
            st.session_state.pred_log.append(res)
            train_ai()
            st.rerun()

    if st.session_state.pred_log:
        r = st.session_state.pred_log[-1]
        
        st.markdown(f"""
        <div class="result-card" style="border-color: {r.get('color')};">
            <h2 style="color: {r.get('color')}; margin-bottom: 5px;">{r.get('emoji')} {r.get('signal')}</h2>
            <div style="font-size: 0.9rem; color: #888; margin-bottom: 20px;">
                PROB: <strong style="color:#fff;">{r.get('prob')}%</strong> | 
                CONF: <strong style="color:#fff;">{r.get('confidence')}</strong> | 
                AI ML: <strong style="color:#fff;">{r.get('ai_score')}</strong>
            </div>
            
            <div class="time-grid">
                <div class="time-box">
                    <span>🟢 EARLY</span>
                    <strong style="color:#00ffcc;">{r.get('h_early')}</strong>
                </div>
                <div class="time-box" style="transform: scale(1.1); border-color:#ff00cc; box-shadow: 0 0 10px rgba(255,0,204,0.3);">
                    <span style="color:#ff00cc;">⚡ MAIN ENTRY</span>
                    <strong style="color:#ff00cc;">{r.get('h_ent')}</strong>
                </div>
                <div class="time-box">
                    <span>🔵 LATE</span>
                    <strong style="color:#0088ff;">{r.get('h_late')}</strong>
                </div>
            </div>
            <p style="margin-top: 15px; color: #555; font-size: 0.8rem;">TARGET MOY: {r.get('moy')}x</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ WIN / VALIDER"):
                st.session_state.pred_log[-1]["result"] = "win"
                update_rl("win")
                train_ai()
                st.rerun()
        with col2:
            if st.button("❌ LOSE / PERTE"):
                st.session_state.pred_log[-1]["result"] = "lose"
                update_rl("lose")
                train_ai()
                st.rerun()

with tab2:
    if not st.session_state.pred_log:
        st.info("Ny Historique dia mbola foana. Manaova analyse aloha.")
    else:
        for i, entry in enumerate(reversed(st.session_state.pred_log)):
            if entry['result'] is None:
                statut = "⚪ EN ATTENTE"
                border = "#888"
            elif entry['result'] == "win":
                statut = "✅ WIN"
                border = "#00ffcc"
            else:
                statut = "❌ LOSE"
                border = "#ff4d4d"
                
            st.markdown(f"""
            <div style="border-left: 4px solid {border}; background: rgba(255,255,255,0.02); padding: 10px 15px; border-radius: 5px; margin-bottom: 10px;">
                <div style="display:flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size:1.1rem;">{entry['h_ent']}</strong> 
                        <span style="color:#888; font-size:0.8rem; margin-left:10px;">| {entry['emoji']} {entry['signal']}</span>
                    </div>
                    <strong style="color:{border};">{statut}</strong>
                </div>
                <div style="font-size:0.8rem; color:#666; margin-top:5px;">
                    Target: {entry['moy']}x | Conf: {entry['confidence']} | Ref: {entry['ref']}
                </div>
            </div>
            """, unsafe_allow_html=True)
