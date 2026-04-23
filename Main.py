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
    
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 4rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #ff0066, #ff3399, #00ffcc, #ff0066);
        background-size: 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    
    .subtitle {
        text-align: center;
        color: #ff006699;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.85rem;
        letter-spacing: 0.5em;
        margin-bottom: 2rem;
    }
    
    .glass-ultra {
        background: rgba(10, 0, 25, 0.9);
        border: 2px solid rgba(255, 0, 102, 0.4);
        border-radius: 20px;
        padding: 28px;
        backdrop-filter: blur(12px);
        margin-bottom: 24px;
    }
    
    .glass-result {
        background: rgba(5, 0, 15, 0.95);
        border: 3px solid rgba(255, 0, 102, 0.6);
        border-radius: 20px;
        padding: 32px;
        backdrop-filter: blur(16px);
    }
    
    .entry-time-ultra {
        font-family: 'Orbitron', sans-serif;
        font-size: 5rem;
        font-weight: 900;
        text-align: center;
        color: #ff0066;
        text-shadow: 0 0 30px #ff0066;
        margin: 24px 0;
    }
    
    .x3-prob-mega {
        font-size: 5.5rem;
        font-weight: 900;
        font-family: 'Orbitron', sans-serif;
        text-align: center;
        color: #ff0066;
    }

    .target-box-min { background: rgba(0, 255, 204, 0.1); border: 2px solid #00ffcc; border-radius: 16px; padding: 20px; text-align: center; }
    .target-box-moy { background: rgba(255, 215, 0, 0.1); border: 2px solid #ffd700; border-radius: 16px; padding: 20px; text-align: center; }
    .target-box-max { background: rgba(255, 51, 102, 0.1); border: 2px solid #ff3366; border-radius: 16px; padding: 20px; text-align: center; }
    
    .target-value { font-size: 2.5rem; font-weight: 900; font-family: 'Orbitron'; }
    .accuracy-badge { font-size: 0.8rem; color: #00ff88; }

    .stButton>button {
        background: linear-gradient(135deg, #ff0066 0%, #ff3399 100%) !important;
        color: white !important;
        font-weight: 900 !important;
        border-radius: 14px !important;
        height: 60px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ===================== AUTHENTICATION =====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<div class='main-title'>JETX ULTRA</div>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        pw = st.text_input("🔑 PASSWORD", type="password")
        if st.button("🚀 ACTIVER LE SYSTÈME", use_container_width=True):
            if pw == "JET2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect")
    st.stop()

# ===================== ENGINE 250K =====================
def run_ultra_engine(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:16], 16)
    
    seed_val = int((h_num & 0xFFFFFFFF) + (last_cote * 1000))
    np.random.seed(seed_val % (2**32))
    
    # Simulation Logic
    sigma = 0.22 - (last_cote * 0.005)
    sims = np.random.lognormal(np.log(2.1), max(0.15, sigma), 250_000)
    
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    target_min = round(float(np.percentile(sims, 30)), 2)
    target_moy = round(float(np.percentile(sims, 50)), 2)
    
    sims_x3 = sims[sims >= 3.0]
    target_max = round(float(np.percentile(sims_x3, 85)), 2) if len(sims_x3) > 0 else 3.50

    try:
        base_t = datetime.strptime(t_in.strip(), "%H:%M:%S")
        shift = 45 + (h_num % 40)
        entry_t = (base_t + timedelta(seconds=shift)).strftime("%H:%M:%S")
    except:
        entry_t = datetime.now(EAT).strftime("%H:%M:%S")

    res = {
        "id": h_hex[:8],
        "entry": entry_t,
        "prob_x3": prob_x3,
        "target_min": max(2.0, target_min),
        "target_moy": max(2.5, target_moy),
        "target_max": max(3.0, target_max),
        "signal": "💎 ULTRA X3+" if prob_x3 > 45 else "🔥 STRONG X3+",
        "status": "PENDING"
    }
    st.session_state.history.append(res)
    save_history(st.session_state.history)
    return res

# ===================== UI MAIN =====================
if "history" not in st.session_state: st.session_state.history = load_history()
if "last_res" not in st.session_state: st.session_state.last_res = None

st.markdown("<div class='main-title'>JETX ULTRA V18.0</div>", unsafe_allow_html=True)

col_input, col_result = st.columns([1, 2.2], gap="large")

with col_input:
    st.markdown("<div class='glass-ultra'>", unsafe_allow_html=True)
    h_val = st.text_input("🔑 SERVER HASH")
    t_val = st.text_input("⌚ ROUND TIME (HH:MM:SS)")
    l_cote = st.number_input("📊 LAST COTE", value=2.0, step=0.01)
    
    if st.button("🚀 ANALYSE ULTRA", use_container_width=True):
        if h_val and t_val:
            st.session_state.last_res = run_ultra_engine(h_val, t_val, l_cote)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col_result:
    r = st.session_state.last_res
    if r:
        st.markdown("<div class='glass-result'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center; color:#ff0066;'>{r['signal']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-time-ultra'>{r['entry']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='x3-prob-mega'>{r['prob_x3']}%</div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='target-box-min'>MIN<br><span class='target-value'>{r['target_min']}x</span></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='target-box-moy'>MOYEN<br><span class='target-value'>{r['target_moy']}x</span></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='target-box-max'>MAX<br><span class='target-value'>{r['target_max']}x</span></div>", unsafe_allow_html=True)
        
        if st.button("✅ CONFIRMER WIN", use_container_width=True):
            for h in st.session_state.history:
                if h['id'] == r['id']: h['status'] = 'WIN ✅'
            save_history(st.session_state.history)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Historique
if st.session_state.history:
    st.markdown("### 🕒 HISTORIQUE")
    st.dataframe(pd.DataFrame(st.session_state.history[::-1]), use_container_width=True)
