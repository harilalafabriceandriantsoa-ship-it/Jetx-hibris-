import streamlit as st
import numpy as np
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import pytz
import json
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
        st.warning(f"Sauvegarde: {e}")

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

# ===================== CSS ULTRA PUISSANT =====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    
    .stApp {
        background: radial-gradient(ellipse at 50% 0%, #1a0033 0%, #000008 60%, #001a1a 100%);
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-image:
            radial-gradient(2px 2px at 20% 30%, #ff006688, transparent),
            radial-gradient(1px 1px at 80% 10%, #00ffcc44, transparent),
            radial-gradient(1.5px 1.5px at 50% 60%, #ff006633, transparent);
        background-size: 500px 500px, 400px 400px, 300px 300px;
        animation: stars-move 60s linear infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes stars-move {
        from { background-position: 0 0, 0 0, 0 0; }
        to { background-position: 500px 500px, -400px 400px, 300px -300px; }
    }
    
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 4rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #ff0066, #ff3399, #00ffcc, #ff0066);
        background-size: 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: title-glow 4s ease infinite;
        margin-bottom: 0;
    }
    
    @keyframes title-glow {
        0%, 100% { background-position: 0%; filter: drop-shadow(0 0 20px #ff006688); }
        50% { background-position: 100%; filter: drop-shadow(0 0 40px #00ffccaa); }
    }
    
    .glass-ultra {
        background: rgba(10, 0, 25, 0.9);
        border: 2px solid rgba(255, 0, 102, 0.4);
        border-radius: 20px;
        padding: 28px;
        backdrop-filter: blur(12px);
        margin-bottom: 24px;
    }
    
    .entry-time-ultra {
        font-family: 'Orbitron', sans-serif;
        font-size: 5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #ff0066, #ff3399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 40px #ff0066aa);
        animation: entry-pulse 2.5s ease-in-out infinite;
    }

    @keyframes entry-pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }

    .signal-ultra { color: #ff0066; font-family: 'Orbitron'; font-size: 1.8rem; text-align: center; }
    
    .target-box-max {
        background: linear-gradient(135deg, rgba(255, 51, 102, 0.25), rgba(200, 0, 60, 0.1));
        border: 2px solid rgba(255, 51, 102, 0.6);
        border-radius: 16px; padding: 20px; text-align: center;
    }

    .stButton>button {
        background: linear-gradient(135deg, #ff0066 0%, #ff3399 100%) !important;
        color: white !important; font-weight: 900 !important;
        border-radius: 14px !important; height: 60px !important;
    }
</style>
""", unsafe_allow_html=True)

# ===================== AUTHENTICATION =====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "history" not in st.session_state:
    st.session_state.history = load_history()
if "last_res" not in st.session_state:
    st.session_state.last_res = None

if not st.session_state.authenticated:
    st.markdown("<div class='main-title'>JETX ULTRA</div>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        pw = st.text_input("🔑 MOT DE PASSE", type="password", placeholder="JET2026")
        if st.button("🚀 ACTIVER", use_container_width=True):
            if pw == "JET2026":
                st.session_state.authenticated = True
                st.rerun()
    st.stop()

# ===================== ENGINE ULTRA V18 =====================
def run_ultra_engine(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:16], 16)
    
    # Dynamic seed based on hash + last_cote
    np.random.seed(int((h_num & 0xFFFFFFFF) + (last_cote * 1000)) % (2**32))
    
    # 250,000 Simulations
    base = 2.10 if last_cote < 2.0 else 1.95
    sims = np.random.lognormal(np.log(base), 0.22, 250_000)
    
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    target_min = round(float(np.percentile(sims, 30)), 2)
    target_max = round(float(np.percentile(sims[sims>=3.0], 85)), 2) if any(sims>=3.0) else 3.50
    
    # Entry Time Calculation
    try:
        base_t = datetime.combine(datetime.now(EAT).date(), datetime.strptime(t_in.strip(), "%H:%M:%S").time())
    except:
        base_t = datetime.now(EAT)
    
    shift = 50 + (h_num % 40) + int(last_cote * 2)
    entry_time = (base_t + timedelta(seconds=shift)).strftime("%H:%M:%S")
    
    result = {
        "id": h_hex[:8], "entry": entry_time, "prob_x3": prob_x3,
        "target_min": target_min, "target_max": target_max,
        "signal": "🔥 STRONG X3+" if prob_x3 > 35 else "⚠️ MODERATE",
        "status": "PENDING"
    }
    st.session_state.history.append(result)
    save_history(st.session_state.history)
    return result

# ===================== MAIN UI =====================
st.markdown("<div class='main-title'>JETX ULTRA V18.0</div>", unsafe_allow_html=True)

col_in, col_res = st.columns([1, 2.2], gap="large")

with col_in:
    st.markdown("<div class='glass-ultra'>", unsafe_allow_html=True)
    h_val = st.text_input("🔐 SERVER HASH")
    t_val = st.text_input("⏰ ROUND TIME (HH:MM:SS)")
    l_cote = st.number_input("📊 LAST COTE (TALOHA)", value=2.00, step=0.01)
    
    if st.button("🚀 ANALYSER X3+", use_container_width=True):
        if h_val and t_val:
            st.session_state.last_res = run_ultra_engine(h_val, t_val, l_cote)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col_res:
    res = st.session_state.last_res
    if res:
        st.markdown(f"<div class='entry-time-ultra'>{res['entry']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='signal-ultra'>{res['signal']}</div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("PROB X3+", f"{res['prob_x3']}%")
        c2.metric("TARGET SAFE", f"{res['target_min']}x")
        c3.metric("TARGET MAX", f"{res['target_max']}x")
    else:
        st.info("Miandry data analyse avy any aminao...")

# ===================== FANAZAVANA SECTION =====================
st.markdown("""
<div style='margin-top:40px; padding:24px; background:rgba(255,0,102,0.08); border:1px solid rgba(255,0,102,0.3); border-radius:14px; max-width:800px; margin:auto;'>
    <h3 style='color:#ff0066; text-align:center;'>📖 TOROLALANA V18.0</h3>
    <p style='line-height:1.8;'>
    1. <b>Hash:</b> Alao ao amin'ny Provably Fair an'ny casino.<br>
    2. <b>Time:</b> Ny ora nivoahan'ilay round teo (HH:MM:SS).<br>
    3. <b>Last Cote:</b> Ny cote nivoaka tamin'ilay round teo (ohatra: 1.87).<br><br>
    <b>Fanamarihana:</b> Ny <i>Entry Time</i> mipoitra eo amin'ny mavokely lehibe no fotoana tokony hidiranao milalao.
    </p>
</div>
""", unsafe_allow_html=True) 
