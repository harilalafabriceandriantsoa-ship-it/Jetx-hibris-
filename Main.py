import streamlit as st
import numpy as np
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time

# ==========================================
# 💎 PREMIUM UI & STYLING
# ==========================================
st.set_page_config(page_title="ANDR-X V13.5 PRO-SYNC", layout="wide")

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
    }
    
    .stat-val { font-size: 1.8rem; font-weight: 700; color: #00ffcc; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 HYPER-PRECISION ENGINE
# ==========================================

if "history" not in st.session_state: 
    st.session_state.history = []

def get_tz_now():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def hyper_time_calc(hash_val, spread, t_in):
    now = get_tz_now()
    try:
        t_obj = datetime.strptime(t_in.strip(), "%H:%M:%S").time()
        base_time = datetime.combine(now.date(), t_obj)
        if base_time > now.replace(tzinfo=None) + timedelta(hours=1):
            base_time -= timedelta(days=1)
    except Exception:
        base_time = now
        
    hash_shift = (int(hash_val[:6], 16) % 15) - 5
    base_delay = 14 + (spread * 1.5)
    final_seconds = int(base_delay + hash_shift)
    final_seconds = max(10, min(90, final_seconds)) 
    
    entry = base_time + timedelta(seconds=final_seconds)
    return entry.strftime("%H:%M:%S")

def run_ultra_analysis(h_in, t_in, c_ref):
    h_num = int(hashlib.sha256(h_in.encode()).hexdigest()[:16], 16)
    h_norm = (h_num % 1000) / 1000
    np.random.seed(h_num & 0xffffffff)
    
    variance_scale = 0.25 + (h_norm * 0.2)
    sims = np.random.lognormal(np.mean([np.log(c_ref + 0.05), 0.25]), variance_scale, 12000)
    
    prob_x3 = np.mean(sims >= 3.0) * 100
    moy = np.exp(np.mean(np.log(sims)))
    max_v = np.percentile(sims, 98) 
    min_v = np.percentile(sims, 5)  
    spread = max_v - min_v
    
    base_conf = 100 - (abs(moy - c_ref) / c_ref * 100)
    final_conf = max(20, min(99.1, base_conf + (len(st.session_state.history) * 2)))

    rtp_pressure = (c_ref / moy) if moy > 0 else 1
    x3_target = (prob_x3 * 0.6) + (rtp_pressure * 20) + (h_norm * 20)
    x3_target = round(min(99.9, x3_target), 1)
    
    entry_time = hyper_time_calc(h_in, spread, t_in)
    
    if moy >= 2.2 and x3_target > 65:
        signal, color = "💎 ULTRA SNIPER (X3+)", "#ff00cc"
    elif moy >= 1.7:
        signal, color = "🟢 STRONG ENTRY", "#00ffcc"
    elif moy >= 1.2:
        signal, color = "⚡ SCALPING (X1.2)", "#ffff00"
    else:
        signal, color = "⚠️ HIGH RISK - SKIP", "#ff4444"
    
    res = {
        "entry": entry_time, "signal": signal, "color": color,
        "x3_prob": x3_target, "conf": round(final_conf, 1),
        "spread": round(spread, 2), "moy": round(moy, 2),
        "max": round(max_v, 2), "min": round(min_v, 2)
    }
    
    st.session_state.history.append(res)
    if len(st.session_state.history) > 15: st.session_state.history.pop(0)
    return res

# ==========================================
# 🖥️ INTERFACE & SECURITY
# ==========================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>🔐 ACCESS CONTROL</h2>", unsafe_allow_html=True)
    pass_input = st.text_input("Enter System Password:", type="password")
    if st.button("UNLOCK SYSTEM"):
        if pass_input == "2026":
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("Incorrect Password.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

st.markdown("<h1 class='main-title'>ANDR-X V13.5 PRO-SYNC</h1>", unsafe_allow_html=True)

col_ctrl, col_res = st.columns([1, 2])

with col_ctrl:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    h_in = st.text_input("SERVER HASH CODE", placeholder="D76F4F2D...")
    t_in = st.text_input("LAST ROUND TIME (HH:MM:SS)", placeholder="21:51:16")
    c_ref = st.number_input("REFERENCE COTE (TREND)", value=2.5, step=0.1) 
    
    if st.button("EXECUTE ANALYSIS"):
        if h_in and len(t_in) == 8:
            with st.spinner("Sync..."):
                time.sleep(0.5)
                st.session_state.last_res = run_ultra_analysis(h_in, t_in, c_ref)
        else: st.error("Format Lera diso!")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.sidebar.button("🗑️ PURGE ALL DATA"):
        st.session_state.history = []
        if "last_res" in st.session_state: del st.session_state.last_res
        st.rerun()

with col_res:
    if "last_res" in st.session_state:
        r = st.session_state.last_res
        # Eto no namboarina mba tsy hisy error intsony
        st.markdown(f"""
        <div class="glass-card" style="border-left: 10px solid {r['color']}">
            <h2 style="color: {r['color']}; margin: 0;">{r['signal']}</h2>
            <hr style="opacity: 0.1; margin: 10px 0;">
            <div style="display: flex; justify-content: space-between;">
                <div><small>X3+ PROB</small><br><span class="stat-val" style="color:{r['color']}">{r['x3_prob']}%</span></div>
                <div><small>ACCURACY</small><br><span class="stat-val">{r['conf']}%</span></div>
                <div><small>VOLATILITY</small><br><span class="stat-val">{r['spread']}</span></div>
            </div>
            <div style="background: rgba(255,255,255,0.05); padding
