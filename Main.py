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

st.markdown("""
<style>     
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Share+Tech+Mono&display=swap');
    .stApp { background-color: #05050A; color: #00ffcc; font-family: 'Share Tech Mono', monospace; }
    h1, h2 { font-family: 'Orbitron', sans-serif; text-align: center; color: #00ffcc; }
    .stTextInput>div>div>input, .stNumberInput>div>div>input { background-color: #fff !important; color: #000 !important; font-weight: bold; }
    .stButton>button { background: linear-gradient(90deg, #004d4d, #00ffcc) !important; color: #000 !important; font-weight: bold; border-radius: 12px; height: 45px; width: 100%; }
</style>    
""", unsafe_allow_html=True)

# ---------------- SESSION MANAGEMENT ----------------
if "pred_log" not in st.session_state: st.session_state.pred_log = []
if "auth" not in st.session_state: st.session_state.auth = False
if "ml_model" not in st.session_state: st.session_state.ml_model = RandomForestClassifier(n_estimators=150)
if "rl_score" not in st.session_state: st.session_state.rl_score = {"win": 0, "lose": 0}

# ---------------- V13 ULTRA ENGINE ----------------
def v13_ultra_delay(t_obj, h_hex, h_int, last_cote):
    h_a, h_b = int(h_hex[8:14], 16), int(h_hex[14:20], 16)
    h_c, h_d = int(h_hex[20:26], 16), int(h_hex[26:32], 16)
    base = 18 + (h_int % 25)
    layers = (h_a % 19) + (h_b % 13) + (h_c % 11) + (h_d % 7)
    t_sec = t_obj.hour * 3600 + t_obj.minute * 60 + t_obj.second
    entropy = (t_sec % 90) // 3
    rl_bias = 0
    total = st.session_state.rl_score["win"] + st.session_state.rl_score["lose"]
    if total > 0: rl_bias = int((st.session_state.rl_score["win"] / total) * 10)
    final = base + layers + entropy + rl_bias + (int(last_cote * 3) % 17)
    res = final + ((h_a % 5) - (h_c % 4))
    return max(12, min(110, res))

def run_prediction(hash_str, h_act, last_cote):
    try: t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except: t_obj = datetime.now()
    h_hex = hashlib.sha256(hash_str.encode()).hexdigest()
    h_int = int(h_hex[:10], 16)
    np.random.seed(h_int % (2**32))
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
    return {"h_ent": e_time.strftime("%H:%M:%S"), "h_early": (e_time - timedelta(seconds=2)).strftime("%H:%M:%S"), "h_late": (e_time + timedelta(seconds=2)).strftime("%H:%M:%S"), "min": min_v, "moy": moy, "max": max_v, "prob": prob, "conf": conf, "signal": sig, "emoji": emo, "color": col, "ref": last_cote}

# ---------------- LOGIN ----------------
if not st.session_state.auth:
    st.markdown("<h1>⚡ LOGIN</h1>", unsafe_allow_html=True)
    if st.text_input("CODE", type="password") == "2026":
        if st.button("ACTIVATE"): st.session_state.auth = True; st.rerun()
    st.stop()

# ---------------- MAIN ----------------
st.markdown("<h1>🚀 JET X GOLD V13.2</h1>", unsafe_allow_html=True)
h_in = st.text_input("🔑 HASH")
t_in = st.text_input("⏰ TIME (HH:MM:SS)")
l_c = st.number_input("📉 LAST COTE", value=1.50)

if st.button("🔥 EXECUTE"):
    if h_in and t_in:
        st.session_state.pred_log.append(run_prediction(h_in, t_in, l_c))

if st.session_state.pred_log:
    r = st.session_state.pred_log[-1]
    # ✅ FANAMBOARANA: Nampiana 'f' eo alohan'ny hira ary 'unsafe_allow_html=True'
    st.markdown(f"""
    <div style="border: 2px solid {r['color']}; border-radius: 20px; padding: 20px; background: rgba(0, 20, 20, 0.8); text-align: center; margin-top: 15px;">
        <h2 style="color: {r['color']}; margin:0;">{r['emoji']} {r['signal']}</h2>
        <p style="color:#888;">PROB: {r['prob']}% | CONF: {r['conf']}</p>
        <div style="display: flex; justify-content: space-around; gap: 8px; margin: 15px 0;">
            <div style="background: rgba(0,0,0,0.5); border: 1px solid rgba(0,255,204,0.3); padding: 10px 5px; border-radius: 12px; width: 32%;">
                <span style="font-size: 0.6rem; color: #888; display: block;">COTE MIN</span><strong style="font-size: 1.1rem; color: #fff;">{r['min']}x</strong>
            </div>
            <div style="background: rgba(0,255,204,0.1); border: 1px solid #00ffcc; padding: 10px 5px; border-radius: 12px; width: 32%;">
                <span style="font-size: 0.6rem; color: #00ffcc; display: block;">TARGET MOYEN</span><strong style="font-size: 1.1rem; color: #00ffcc;">{r['moy']}x</strong>
            </div>
            <div style="background: rgba(0,0,0,0.5); border: 1px solid rgba(0,255,204,0.3); padding: 10px 5px; border-radius: 12px; width: 32%;">
                <span style="font-size: 0.6rem; color: #888; display: block;">COTE MAX</span><strong style="font-size: 1.1rem; color: #fff;">{r['max']}x</strong>
            </div>
        </div>
        <div style="display: flex; justify-content: space-around; gap: 6px; margin-top: 20px;">
            <div style="background: #001111; border: 1px solid rgba(0,255,204,0.4); padding: 8px 2px; border-radius: 8px; width: 32%;">
                <span style="font-size: 0.65rem; color: #888; display: block;">🟢 EARLY</span><strong style="color:#fff;">{r['h_early']}</strong>
            </div>
            <div style="background: #001111; border: 1px solid #ff00cc; padding: 8px 2px; border-radius: 8px; width: 32%; transform: scale(1.05);">
                <span style="font-size: 0.65rem; color: #ff00cc; display: block;">⚡ MAIN ENTRY</span><strong style="color:#fff;">{r['h_ent']}</strong>
            </div>
            <div style="background: #001111; border: 1px solid rgba(0,255,204,0.4); padding: 8px 2px; border-radius: 8px; width: 32%;">
                <span style="font-size: 0.65rem; color: #888; display: block;">🔵 LATE</span><strong style="color:#fff;">{r['h_late']}</strong>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    if col1.button("✅ WIN"): st.session_state.rl_score["win"] += 1; st.rerun()
    if col2.button("❌ LOSE"): st.session_state.rl_score["lose"] += 1; st.rerun()
