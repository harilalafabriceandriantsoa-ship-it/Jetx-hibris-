import streamlit as st
import numpy as np
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import pytz
import json
import os
from pathlib import Path

# ===================== PERSISTENCE SYSTEM =====================
try:
    BASE_DIR = Path(__file__).parent
except:
    BASE_DIR = Path.cwd()

DATA_DIR = BASE_DIR / "jetx_data_v18"
DATA_DIR.mkdir(exist_ok=True, parents=True)
HISTORY_FILE = DATA_DIR / "history_v18.json"

def save_history(history):
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.warning(f"Sauvegarde error: {e}")

def load_history():
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return []

# ===================== CONFIG =====================
st.set_page_config(
    page_title="JETX ULTRA V18.0 X3+", 
    layout="wide",
    initial_sidebar_state="expanded"
)

EAT = pytz.timezone("Indian/Antananarivo")

# ===================== CSS ULTRA STYLE =====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    
    .stApp {
        background: radial-gradient(ellipse at 50% 0%, #1a0033 0%, #000008 60%, #001a1a 100%);
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }
    
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #ff0066, #ff3399, #00ffcc, #ff0066);
        background-size: 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    
    .glass-ultra {
        background: rgba(10, 0, 25, 0.9);
        border: 2px solid rgba(255, 0, 102, 0.4);
        border-radius: 20px;
        padding: 25px;
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
    }
    
    .glass-result {
        background: rgba(5, 0, 15, 0.95);
        border: 3px solid rgba(255, 0, 102, 0.6);
        border-radius: 20px;
        padding: 30px;
        backdrop-filter: blur(16px);
        box-shadow: 0 0 50px rgba(255, 0, 102, 0.2);
    }
    
    .entry-time-ultra {
        font-family: 'Orbitron', sans-serif;
        font-size: 4.5rem;
        font-weight: 900;
        text-align: center;
        color: #ff0066;
        text-shadow: 0 0 30px #ff0066;
        margin: 20px 0;
    }
    
    .x3-prob-mega {
        font-size: 5rem;
        font-weight: 900;
        font-family: 'Orbitron', sans-serif;
        text-align: center;
        color: #00ffcc;
        text-shadow: 0 0 20px #00ffcc44;
    }

    .target-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .target-val { font-size: 2.2rem; font-weight: 900; font-family: 'Orbitron'; color: #ff0066; }

    .stButton>button {
        font-weight: 900 !important;
        border-radius: 12px !important;
        height: 55px !important;
        transition: all 0.3s ease !important;
    }
    
    /* Custom button colors */
    div.stButton > button:first-child { background: linear-gradient(135deg, #ff0066, #ff3399); border: none; color: white; }
    .btn-win > div > button { background: #00ffcc !important; color: #000 !important; }
    .btn-loss > div > button { background: #ff4b4b !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ===================== AUTHENTICATION =====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<div class='main-title'>JETX ULTRA</div>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        pw = st.text_input("PASSWORD", type="password")
        if st.button("ACTIVATE SYSTEM", use_container_width=True):
            if pw == "JET2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Access Denied")
    st.stop()

# ===================== DATA INITIALIZATION =====================
if "history" not in st.session_state:
    st.session_state.history = load_history()
if "last_res" not in st.session_state:
    st.session_state.last_res = None

# ===================== SIDEBAR STATS =====================
with st.sidebar:
    st.header("📊 PERFORMANCE")
    if st.session_state.history:
        total = len(st.session_state.history)
        wins = sum(1 for h in st.session_state.history if h.get('status') == 'WIN ✅')
        wr = round((wins/total)*100, 1) if total > 0 else 0
        st.metric("WIN RATE", f"{wr}%")
        st.write(f"Total Rounds: {total}")
        st.write(f"Total Wins: {wins}")
    
    st.markdown("---")
    if st.button("🗑️ CLEAR ALL DATA"):
        st.session_state.history = []
        if HISTORY_FILE.exists(): os.remove(HISTORY_FILE)
        st.rerun()

# ===================== ENGINE 250K =====================
def run_ultra_engine(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:16], 16)
    
    # Seeding dynamique
    seed_val = int((h_num & 0xFFFFFFFF) + (last_cote * 1000))
    np.random.seed(seed_val % (2**32))
    
    # 250,000 Simulations
    sigma = 0.23 - (last_cote * 0.004)
    sims = np.random.lognormal(np.log(2.15), max(0.14, sigma), 250_000)
    
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    t_min = round(float(np.percentile(sims, 30)), 2)
    t_moy = round(float(np.percentile(sims, 55)), 2)
    
    sims_x3 = sims[sims >= 3.0]
    t_max = round(float(np.percentile(sims_x3, 80)), 2) if len(sims_x3) > 0 else 3.80

    try:
        base_t = datetime.strptime(t_in.strip(), "%H:%M:%S")
        shift = 42 + (h_num % 15) # Hash-based shift
        entry_t = (base_t + timedelta(seconds=shift)).strftime("%H:%M:%S")
    except:
        entry_t = datetime.now(EAT).strftime("%H:%M:%S")

    res = {
        "id": h_hex[:8],
        "entry": entry_t,
        "prob": prob_x3,
        "min": max(2.0, t_min),
        "moy": max(2.6, t_moy),
        "max": max(3.1, t_max),
        "signal": "💎 ULTRA X3+" if prob_x3 > 45 else "🔥 STRONG X3+",
        "status": "PENDING"
    }
    st.session_state.history.append(res)
    save_history(st.session_state.history)
    return res

# ===================== UI MAIN =====================
st.markdown("<div class='main-title'>JETX ULTRA V18.0</div>", unsafe_allow_html=True)

col_in, col_res = st.columns([1, 2], gap="large")

with col_in:
    st.markdown("<div class='glass-ultra'>", unsafe_allow_html=True)
    st.subheader("📥 INPUT DATA")
    h_val = st.text_input("SERVER HASH")
    t_val = st.text_input("ROUND TIME (HH:MM:SS)")
    l_cote = st.number_input("LAST COTE", value=2.00, step=0.01)
    
    if st.button("🚀 START ANALYSE", use_container_width=True):
        if h_val and t_val:
            st.session_state.last_res = run_ultra_engine(h_val, t_val, l_cote)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col_res:
    r = st.session_state.last_res
    if r:
        st.markdown("<div class='glass-result'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center; color:#ff0066;'>{r['signal']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-time-ultra'>{r['entry']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='x3-prob-mega'>{r['prob']}%</div>", unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='target-box'>MIN<br><span class='target-val'>{r['min']}x</span></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='target-box'>MOYEN<br><span class='target-val'>{r['moy']}x</span></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='target-box'>MAX<br><span class='target-val'>{r['max']}x</span></div>", unsafe_allow_html=True)
        
        # --- WIN / LOSS BUTTONS ---
        st.markdown("<br>", unsafe_allow_html=True)
        cw, cl = st.columns(2)
        with cw:
            if st.button("🎯 WIN", use_container_width=True, key="win_btn", help="X3+ hit successfully"):
                for h in st.session_state.history:
                    if h['id'] == r['id']: h['status'] = 'WIN ✅'
                save_history(st.session_state.history)
                st.rerun()
        with cl:
            if st.button("❌ LOSS", use_container_width=True, key="loss_btn", help="Crash before target"):
                for h in st.session_state.history:
                    if h['id'] == r['id']: h['status'] = 'LOSS ❌'
                save_history(st.session_state.history)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Historique Table
if st.session_state.history:
    st.markdown("### 🕒 LOGS")
    df = pd.DataFrame(st.session_state.history[::-1])
    cols = ['entry', 'prob', 'min', 'moy', 'max', 'status']
    st.dataframe(df[cols], use_container_width=True, hide_index=True)
