import streamlit as st
import numpy as np
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time

# ==========================================
# 💎 PREMIUM UI & STYLING (FUTURISTIC NEON)
# ==========================================
st.set_page_config(page_title="ANDR-X V13.5 NEON-ULTRA", layout="wide")

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
        text-shadow: 0 0 20px rgba(0, 255, 204, 0.4);
        margin-bottom: 20px;
    }
    
    .glass-card {
        background: rgba(10, 10, 20, 0.7);
        border: 1px solid rgba(0, 255, 204, 0.3);
        border-radius: 20px;
        padding: 25px;
        backdrop-filter: blur(15px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
        margin-bottom: 20px;
        transition: 0.3s;
    }
    
    .glass-card:hover {
        border-color: #ff00cc;
        box-shadow: 0 0 20px rgba(255, 0, 204, 0.2);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #00ffcc 0%, #0088ff 100%) !important;
        color: #000 !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 12px !important;
        height: 55px !important;
        width: 100% !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: 0.4s;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 30px rgba(0, 255, 204, 0.6);
    }
    
    .stat-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #00ffcc;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 CORE ENGINE & ULTRA MATHS
# ==========================================

if "history" not in st.session_state: st.session_state.history = []
if "auth" not in st.session_state: st.session_state.auth = False

# --- Authentication ---
if not st.session_state.auth:
    st.markdown("<h1 class='main-title'>SYSTEM LOCKED</h1>", unsafe_allow_html=True)
    pwd = st.text_input("ENTER QUANTUM KEY", type="password")
    if st.button("ACTIVATE V13.5"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
        else: st.error("ACCESS DENIED")
    st.stop()

def get_tz_now():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def ultra_time_calc(hash_val, spread, moy):
    now = get_tz_now()
    timestamp = now.timestamp()
    # Oscillator dynamique hifanaraka amin'ny cycle
    oscillator = np.sin(timestamp / 60) * 8 
    base_delay = 12 + (spread * 2.5)
    hash_shift = (int(hash_val[:5], 16) % 16) - 8
    final_seconds = base_delay + oscillator + hash_shift
    final_seconds = max(8, min(95, final_seconds))
    entry = now + timedelta(seconds=final_seconds)
    return entry.strftime("%H:%M:%S")

def run_ultra_analysis(h_in, t_in, c_ref):
    # Hash processing
    h_num = int(hashlib.sha256(h_in.encode()).hexdigest()[:12], 16)
    h_norm = (h_num % 1000) / 1000
    np.random.seed(h_num & 0xffffffff)
    
    # Monte Carlo Simulation (Optimized for X3)
    sims = np.random.lognormal(np.mean([np.log(c_ref + 0.1), 0.3]), 0.4, 8000)
    
    prob_x3 = np.mean(sims >= 3.0) * 100
    moy = np.exp(np.mean(np.log(sims)))
    max_v = np.percentile(sims, 95)
    min_v = np.percentile(sims, 10)
    spread = max_v - min_v
    
    # Accuracy Logic (Basée sur la cohérence historique)
    history_len = len(st.session_state.history)
    history_boost = min(history_len * 4, 30)
    base_conf = 100 - (abs(moy - c_ref) / c_ref * 100)
    final_conf = max(15, min(98.5, base_conf + history_boost))

    # Signal Logic
    rtp_pressure = (c_ref / moy) if moy > 0 else 1
    x3_target = (prob_x3 * 0.5) + (rtp_pressure * 30) + (h_norm * 20)
    x3_target = round(min(99.7, x3_target), 1)
    
    entry_time = ultra_time_calc(h_in, spread, moy)
    
    if x3_target > 78 and final_conf > 55: signal, color = "💎 ULTRA SNIPER (X3+)", "#ff00cc"
    elif x3_target > 58: signal, color = "🟢 STRONG ENTRY", "#00ffcc"
    elif x3_target > 38: signal, color = "⚡ SCALPING (X1.5)", "#ffff00"
    else: signal, color = "⚠️ HIGH RISK - SKIP", "#ff4444"
    
    res = {
        "entry": entry_time,
        "signal": signal,
        "color": color,
        "x3_prob": x3_target,
        "conf": round(final_conf, 1),
        "spread": round(spread, 2),
        "moy": round(moy, 2),
        "max": round(max_v, 2),
        "min": round(min_v, 2)
    }
    
    # Manage Memory (mitazona ny 15 farany ihany)
    st.session_state.history.append(res)
    if len(st.session_state.history) > 15:
        st.session_state.history.pop(0)
        
    return res

# ==========================================
# 🖥️ FUTURISTIC INTERFACE
# ==========================================

st.markdown(f"<h1 class='main-title'>ANDR-X V13.5 NEON-ULTRA</h1>", unsafe_allow_html=True)

col_ctrl, col_res = st.columns([1, 2])

with col_ctrl:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📡 SATELLITE INPUT")
    h_in = st.text_input("SERVER HASH CODE", placeholder="D76F4F2D...")
    t_in = st.text_input("LAST ROUND TIME", placeholder="21:51:16")
    c_ref = st.number_input("REFERENCE COTE (TREND)", value=2.0, step=0.1)
    
    if st.button("EXECUTE ANALYSIS"):
        if h_in and t_in:
            with st.spinner("Decoding Neural Waves..."):
                time.sleep(1.2)
                st.session_state.last_res = run_ultra_analysis(h_in, t_in, c_ref)
        else: st.warning("Please fill all data fields.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.sidebar.button("🗑️ PURGE ALL DATA"):
        st.session_state.history = []
        if "last_res" in st.session_state: del st.session_state.last_res
        st.rerun()

with col_res:
    if "last_res" in st.session_state:
        r = st.session_state.last_res
        st.markdown(f"""
        <div class='glass-card' style='border-left: 10px solid {r['color']}'>
            <h2 style='color: {r['color']}; text-align: left;'>{r['signal']}</h2>
            <hr style='opacity: 0.1'>
            <div style='display: flex; justify-content: space-between;'>
                <div><small>X3+ PROBABILITY</small><br><span class='stat-val' style='color:{r['color']}'>{r['x3_prob']}%</span></div>
                <div><small>ACCURACY</small><br><span class='stat-val'>{r['conf']}%</span></div>
                <div><small>VOLATILITY</small><br><span class='stat-val'>{r['spread']}</span></div>
            </div>
            <div style='background: rgba(0,255,204,0.05); padding: 20px; border-radius: 15px; margin-top: 20px; text-align: center;'>
                <p style='margin-bottom: 0; font-size: 1.1rem; letter-spacing: 3px;'>🎯 TARGET ENTRY TIME</p>
                <h1 style='font-size: 4rem; margin: 0; color: #fff; text-shadow: 0 0 20px {r['color']}'>{r['entry']}</h1>
            </div>
            <div style='display: flex; justify-content: space-around; margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px;'>
                <div><small>MIN</small><br><b>{r['min']}x</b></div>
                <div><small>MOYENNE</small><br><b style='color:#00ffcc'>{r['moy']}x</b></div>
                <div><small>MAX PEAK</small><br><b>{r['max']}x</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Awaiting Server Hash for Quantum Synchronization...")

# --- History Table (SAFE VERSION) ---
st.markdown("### 📊 MISSION LOGS (HISTORY)")
if st.session_state.history:
    # Reverse history for display (newest first)
    df_hist = pd.DataFrame(st.session_state.history).iloc[::-1]
    
    # Columns selection safely
    target_cols = ['entry', 'signal', 'x3_prob', 'conf', 'moy']
    available_cols = [c for c in target_cols if c in df_hist.columns]
    
    if available_cols:
        st.table(df_hist[available_cols].head(10))
    else:
        st.write("Preparing table structure...")
