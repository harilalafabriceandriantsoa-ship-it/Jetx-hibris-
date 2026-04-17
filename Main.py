import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG & PREMIUM UI ----------------

st.set_page_config(page_title="ANDR-X AI V13.2 ⚡ GOLD TERMINAL", layout="centered")

# CSS ho an'ny endrika futuristic sy ny fametrahana ny takelaka
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
    
    /* Input Style */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {    
        background-color: #ffffff !important;    
        color: #000000 !important;    
        font-weight: bold !important;    
        border: 2px solid #00ffcc !important;    
        border-radius: 10px !important;    
    }    
        
    /* Button Style */
    .stButton>button {    
        background: linear-gradient(90deg, #004d4d, #00ffcc) !important;    
        color: #000 !important; font-weight: bold !important;    
        font-family: 'Orbitron', sans-serif;    
        border-radius: 12px !important; width: 100%; height: 45px;    
    }
</style>    
""", unsafe_allow_html=True)

# ---------------- SESSION MANAGEMENT ----------------

if "pred_log" not in st.session_state: st.session_state.pred_log = []
if "auth" not in st.session_state: st.session_state.auth = False
if "ml_model" not in st.session_state: st.session_state.ml_model = RandomForestClassifier(n_estimators=150)
if "ml_ready" not in st.session_state: st.session_state.ml_ready = False
if "rl_score" not in st.session_state: st.session_state.rl_score = {"win": 0, "lose": 0}

# ---------------- FUNCTIONS ----------------

def reset_history():
    st.session_state.pred_log = []
    st.session_state.rl_score = {"win": 0, "lose": 0}
    st.rerun()

def train_ai():
    data = []
    for h in st.session_state.pred_log:
        if h.get("result") is not None and "prob" in h:
            data.append([h["prob"], h["moy"], h["max"], float(h["ref_raw"]), h["confidence"], 1 if h["result"] == "win" else 0])

    if len(data) >= 5:
        try:
            df = pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"])
            X = df.drop("label", axis=1); y = df["label"]
            scaler = StandardScaler()
            X_s = scaler.fit_transform(X)
            model = RandomForestClassifier(n_estimators=150)
            model.fit(X_s, y)
            st.session_state.ml_model, st.session_state.scaler, st.session_state.ml_ready = model, scaler, True
        except: pass

# ---------------- V13 ULTRA ENGINE ----------------

def v13_ultra_delay(t_obj, h_hex, h_int, last_cote):
    # Fikajiana ny elanelam-potoana amin'ny alalan'ny hash entropy
    h_a = int(h_hex[8:14], 16)
    h_b = int(h_hex[14:20], 16)
    h_c = int(h_hex[20:26], 16)
    h_d = int(h_hex[26:32], 16)

    base = 18 + (h_int % 25)
    layers = (h_a % 19) + (h_b % 13) + (h_c % 11) + (h_d % 7)
    
    t_sec = t_obj.hour * 3600 + t_obj.minute * 60 + t_obj.second
    entropy = (t_sec % 90) // 3

    rl_bias = 0
    total = st.session_state.rl_score["win"] + st.session_state.rl_score["lose"]
    if total > 0: rl_bias = int((st.session_state.rl_score["win"] / total) * 10)

    final = base + layers + entropy + rl_bias + (int(last_cote * 3) % 17)
    micro = (h_a % 5) - (h_c % 4)
    
    res = final + micro
    if res < 12: res += 18
    elif res > 110: res = 60 + (res % 30)
    return res

def run_prediction(hash_str, h_act, last_cote):
    try: t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except: t_obj = datetime.now(pytz.timezone('Indian/Antananarivo'))

    h_hex = hashlib.sha256(hash_str.encode()).hexdigest()
    h_int = int(h_hex[:10], 16)
    np.random.seed(h_int % (2**32))

    # Simulation Monte Carlo kely
    base_val = (int(h_hex[10:15], 16) % 100) / 20 + 1.25
    sims = np.random.lognormal(mean=np.log(base_val), sigma=0.38, size=15000)

    prob = round(len([s for s in sims if s >= 2.0]) / 15000 * 100, 1)
    moy = round(np.mean(sims) * (1 + (last_cote / 18)), 2)
    min_v, max_v = round(max(1.20, moy * 0.65), 2), round(moy * 1.9, 2)
    conf = round((prob * moy) / 10, 1)

    delay = v13_ultra_delay(t_obj, h_hex, h_int, last_cote)
    e_time = t_obj + timedelta(seconds=delay)

    if conf > 90: sig, emo, col = "ULTRA SNIPER", "🔥", "#ff00cc"
    elif conf > 65: sig, emo, col = "STRONG BUY", "🎯", "#00ffcc"
    else: sig, emo, col = "WAITING / SKIP", "⏳", "#ffcc00"

    return {
        "h_ent": e_time.strftime("%H:%M:%S"),
        "h_early": (e_time - timedelta(seconds=2)).strftime("%H:%M:%S"),
        "h_late": (e_time + timedelta(seconds=2)).strftime("%H:%M:%S"),
        "min": min_v, "moy": moy, "max": max_v, "prob": prob, "confidence": conf,
        "signal": sig, "emoji": emo, "color": col, "ref_raw": last_cote, "result": None
    }

# ---------------- LOGIN INTERFACE ----------------

if not st.session_state.auth:
    st.markdown("<h1>⚡ ANDR-X LOGIN</h1>", unsafe_allow_html=True)
    pwd = st.text_input("🔐 ACCESS CODE", type="password")
    if st.button("ACTIVATE"):
        if pwd == "2026": st.session_state.auth = True; st.rerun()
    st.stop()

# ---------------- MAIN APP ----------------

st.markdown("<h1>🚀 JET X ANDR-GOLD V13.2</h1>", unsafe_allow_html=True)
t1, t2 = st.tabs(["📊 ANALYSE", "📜 HISTORY"])

with t1:
    h_in = st.text_input("🔑 SERVER HASH")
    time_in = st.text_input("⏰ ROUND TIME (HH:MM:SS)")
    l_c = st.number_input("📉 LAST COTE", value=1.50, step=0.1)

    if st.button("🔥 EXECUTE ENGINE"):
        if h_in and time_in:
            res = run_prediction(h_in, time_in, l_c)
            st.session_state.pred_log.append(res); train_ai(); st.rerun()

    if st.session_state.pred_log:
        r = st.session_state.pred_log[-1]
        
        # UI DISPLAY FIX (Ity no mampiseho an'ilay takelaka miloko)
        st.markdown(f"""
        <div style="border: 2px solid {r['color']}; border-radius: 20px; padding: 20px; background: rgba(0, 20, 20, 0.8); text-align: center; margin-top: 15px;">
            <h2 style="color: {r['color']}; margin:0; font-family: 'Orbitron', sans-serif;">{r['emoji']} {r['signal']}</h2>
            <p style="color:#888; font-size:0.85rem; margin-bottom: 10px;">PROB: {r['prob']}% | CONF: {r['confidence']}</p>
            
            <div style="display: flex; justify-content: space-around; gap: 8px; margin: 15px 0;">
                <div style="background: rgba(0,0,0,0.5); border: 1px solid rgba(0,255,204,0.3); padding: 10px 5px; border-radius: 12px; width: 32%;">
                    <span style="font-size: 0.6rem; color: #888; display: block; text-transform: uppercase;">Cote Min</span>
                    <strong style="font-size: 1.1rem; color: #fff; font-family: 'Orbitron';">{r['min']}x</strong>
                </div>
                <div style="background: rgba(0,255,204,0.1); border: 1px solid #00ffcc; padding: 10px 5px; border-radius: 12px; width: 32%;">
                    <span style="font-size: 0.6rem; color: #00ffcc; display: block; text-transform: uppercase;">Target Moyen</span>
                    <strong style="font-size: 1.1rem; color: #00ffcc; font-family: 'Orbitron';">{r['moy']}x</strong>
                </div>
                <div style="background: rgba(0,0,0,0.5); border: 1px solid rgba(0,255,204,0.3); padding: 10px 5px; border-radius: 12px; width: 32%;">
                    <span style="font-size: 0.6rem; color: #888; display: block; text-transform: uppercase;">Cote Max</span>
                    <strong style="font-size: 1.1rem; color: #fff; font-family: 'Orbitron';">{r['max']}x</strong>
                </div>
            </div>

            <div style="display: flex; justify-content: space-around; gap: 6px; margin-top: 20px;">
                <div style="background: #001111; border: 1px solid rgba(0,255,204,0.4); padding: 8px 2px; border-radius: 8px; width: 32%;">
                    <span style="font-size: 0.65rem; color: #888; display: block;">🟢 EARLY</span>
                    <strong style="font-size: 0.95rem; font-family: 'Orbitron'; color:#fff;">{r['h_early']}</strong>
                </div>
                <div style="background: #001111; border: 1px solid #ff00cc; padding: 8px 2px; border-radius: 8px; width: 32%; transform: scale(1.05);">
                    <span style="font-size: 0.65rem; color: #ff00cc; display: block;">⚡ MAIN ENTRY</span>
                    <strong style="font-size: 0.95rem; font-family: 'Orbitron'; color:#fff;">{r['h_ent']}</strong>
                </div>
                <div style="background: #001111; border: 1px solid rgba(0,255,204,0.4); padding: 8px 2px; border-radius: 8px; width: 32%;">
                    <span style="font-size: 0.65rem; color: #888; display: block;">🔵 LATE</span>
                    <strong style="font-size: 0.95rem; font-family: 'Orbitron'; color:#fff;">{r['h_late']}</strong>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        if c1.button("✅ WIN"):
            st.session_state.pred_log[-1]["result"] = "win"
            st.session_state.rl_score["win"] += 1; train_ai(); st.rerun()
        if c2.button("❌ LOSE"):
            st.session_state.pred_log[-1]["result"] = "lose"
            st.session_state.rl_score["lose"] += 1; train_ai(); st.rerun()

with t2:
    st.markdown("### 📜 RECENT ACTIVITY")
    for e in reversed(st.session_state.pred_log):
        res = e.get('result', 'PENDING')
        st.write(f"Round: {e['h_ent']} | Signal: {e['signal']} | Result: {res}")

with st.sidebar:
    st.markdown("### ⚙️ SYSTEM")
    st.write(f"WINS: {st.session_state.rl_score['win']}")
    st.write(f"LOSS: {st.session_state.rl_score['lose']}")
    if st.button("🗑️ RESET SESSION"): reset_history()
