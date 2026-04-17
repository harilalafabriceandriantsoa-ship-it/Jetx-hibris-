import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG & PREMIUM UI ----------------
st.set_page_config(page_title="ANDR-X AI V13.2 ⚡ GOLD", layout="centered")

st.markdown("""
<style>     
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Share+Tech+Mono&display=swap');
    .stApp { background-color: #05050A; color: #00ffcc; font-family: 'Share Tech Mono', monospace; }
    h1, h2 { font-family: 'Orbitron', sans-serif; text-align: center; }
    
    .result-card {
        background: rgba(0, 20, 20, 0.8);
        border: 2px solid #00ffcc;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        margin-top: 15px;
    }
    
    .cote-grid, .time-grid {
        display: flex;
        justify-content: space-around;
        gap: 10px;
        margin: 15px 0;
    }
    
    .cote-box, .time-box {
        background: rgba(0,0,0,0.6);
        border: 1px solid rgba(0,255,204,0.3);
        padding: 12px 5px;
        border-radius: 12px;
        width: 32%;
    }
    
    .cote-box span, .time-box span { font-size: 0.65rem; color: #888; display: block; text-transform: uppercase; }
    .cote-box strong, .time-box strong { font-size: 1.1rem; font-family: 'Orbitron', sans-serif; color: #fff; display: block; }

    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: bold !important;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #004d4d, #00ffcc) !important;
        color: #000 !important; font-weight: bold !important;
        border-radius: 12px !important; height: 50px;
    }
</style>    
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "pred_log" not in st.session_state: st.session_state.pred_log = []
if "auth" not in st.session_state: st.session_state.auth = False
if "rl_score" not in st.session_state: st.session_state.rl_score = {"win": 0, "lose": 0}

# ---------------- ENGINE V13 (NO DELETIONS) ----------------
def v13_ultra_delay(t_obj, h_hex, h_int, last_cote):
    hash_time_a = int(h_hex[8:14], 16)
    hash_time_b = int(h_hex[14:20], 16)
    hash_time_c = int(h_hex[20:26], 16)
    hash_time_d = int(h_hex[26:32], 16)
    base_delay = 18 + (h_int % 25)
    layer_1, layer_2 = hash_time_a % 19, hash_time_b % 13
    layer_3, layer_4 = hash_time_c % 11, hash_time_d % 7
    t_sec = t_obj.hour * 3600 + t_obj.minute * 60 + t_obj.second
    phase_entropy = (t_sec % 90) // 3
    rl_bias = 0
    total_rl = st.session_state.rl_score["win"] + st.session_state.rl_score["lose"]
    if total_rl > 0: rl_bias = int((st.session_state.rl_score["win"] / total_rl) * 10)
    ref_bias = int(last_cote * 3) % 17
    raw_delay = base_delay + layer_1 + layer_2 + layer_3 + layer_4 + phase_entropy + rl_bias + ref_bias
    micro = ((hash_time_a % 5) - (hash_time_c % 4))
    final_delay = raw_delay + micro
    if final_delay < 12: final_delay += 18
    elif final_delay > 110: final_delay = 60 + (final_delay % 30)
    return final_delay

def run_prediction(hash_str, h_act, last_cote):
    try: t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except: t_obj = datetime.now(pytz.timezone('Indian/Antananarivo'))
    h_hex = hashlib.sha256(hash_str.encode()).hexdigest()
    h_int = int(h_hex[:10], 16)
    np.random.seed(h_int % (2**32))
    base_val = (int(h_hex[10:15], 16) % 100) / 20 + 1.25
    sims = np.random.lognormal(mean=np.log(base_val), sigma=0.38, size=15000)
    prob = round(len([s for s in sims if s >= 2.0]) / 15000 * 100, 1)
    moy = round(np.mean(sims) * (1 + (last_cote / 18)), 2)
    min_v, max_v = round(max(1.20, moy * 0.65), 2), round(moy * 1.9, 2)
    confidence = round((prob * moy) / 10, 1)
    
    total = st.session_state.rl_score["win"] + st.session_state.rl_score["lose"]
    if total > 0: confidence = round(confidence * (0.85 + (st.session_state.rl_score["win"] / total)), 1)
    
    delay = v13_ultra_delay(t_obj, h_hex, h_int, last_cote)
    e_time = t_obj + timedelta(seconds=delay)

    if confidence > 90: sig, emo, col = "ULTRA SNIPER", "🔥", "#ff00cc"
    elif confidence > 65: sig, emo, col = "STRONG BUY", "🎯", "#00ffcc"
    else: sig, emo, col = "WAITING / SKIP", "⏳", "#ffcc00"

    return {
        "h_ent": e_time.strftime("%H:%M:%S"),
        "h_early": (e_time - timedelta(seconds=2)).strftime("%H:%M:%S"),
        "h_late": (e_time + timedelta(seconds=2)).strftime("%H:%M:%S"),
        "min": min_v, "moy": moy, "max": max_v, "prob": prob, "confidence": confidence,
        "signal": sig, "emoji": emo, "color": col, "ref_raw": last_cote, "result": None
    }

# ---------------- UI ----------------
if not st.session_state.auth:
    st.markdown("<h1>⚡ ANDR-X LOGIN</h1>", unsafe_allow_html=True)
    pwd = st.text_input("🔐 ACCESS CODE", type="password")
    if st.button("ACTIVATE"):
        if pwd == "2026": st.session_state.auth = True; st.rerun()
    st.stop()

st.markdown("<h1>🚀 JET X ANDR-GOLD V13.2</h1>", unsafe_allow_html=True)
t1, t2 = st.tabs(["📊 ANALYSE", "📜 HISTORY"])

with t1:
    h_in = st.text_input("🔑 SERVER HASH")
    time_in = st.text_input("⏰ ROUND TIME (HH:MM:SS)")
    l_c = st.number_input("📉 LAST COTE", value=1.50, step=0.1)

    if st.button("🔥 EXECUTE ENGINE"):
        if h_in and time_in:
            res = run_prediction(h_in, time_in, l_c)
            st.session_state.pred_log.append(res); st.rerun()

    if st.session_state.pred_log:
        r = st.session_state.pred_log[-1]
        
        # ✅ FIX: Direct variable mapping in HTML
        st.markdown(f"""
        <div class="result-card" style="border-color: {r['color']};">
            <h2 style="color: {r['color']}; margin:0;">{r['emoji']} {r['signal']}</h2>
            <p style="color:#888; font-size:0.85rem;">PROB: {r['prob']}% | CONF: {r['confidence']}</p>
            
            <div class="cote-grid">
                <div class="cote-box"><span>Cote Min</span><strong>{r['min']}x</strong></div>
                <div class="cote-box" style="border-color:#00ffcc; background:rgba(0,255,204,0.1);">
                    <span style="color:#00ffcc;">Target Moyen</span><strong style="color:#00ffcc;">{r['moy']}x</strong>
                </div>
                <div class="cote-box"><span>Cote Max</span><strong>{r['max']}x</strong></div>
            </div>

            <div class="time-grid">
                <div class="time-box"><span>🟢 EARLY</span><strong>{r['h_early']}</strong></div>
                <div class="time-box" style="border-color:#ff00cc; transform:scale(1.05);">
                    <span style="color:#ff00cc;">⚡ MAIN ENTRY</span><strong>{r['h_ent']}</strong>
                </div>
                <div class="time-box"><span>🔵 LATE</span><strong>{r['h_late']}</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        if c1.button("✅ WIN"):
            st.session_state.pred_log[-1]["result"] = "win"
            st.session_state.rl_score["win"] += 1; st.rerun()
        if c2.button("❌ LOSE"):
            st.session_state.pred_log[-1]["result"] = "lose"
            st.session_state.rl_score["lose"] += 1; st.rerun()

with t2:
    for e in reversed(st.session_state.pred_log):
        res_t = e.get('result', 'PENDING')
        clr = "#00ffcc" if res_t=="win" else "#ff4d4d" if res_t=="lose" else "#888"
        st.write(f"Round: {e['h_ent']} | Signal: {e['signal']} | Result: {res_t}")
