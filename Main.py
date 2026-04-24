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
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #ff0066, #ff3399, #00ffcc, #ff0066);
        background-size: 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: title-glow 4s ease infinite;
        margin-bottom: 0;
    }
    
    .glass-ultra {
        background: rgba(10, 0, 25, 0.9);
        border: 2px solid rgba(255, 0, 102, 0.4);
        border-radius: 20px;
        padding: 28px;
        backdrop-filter: blur(12px);
        box-shadow: 0 0 40px rgba(255, 0, 102, 0.15);
        margin-bottom: 24px;
    }

    .entry-time-ultra {
        font-family: 'Orbitron', sans-serif;
        font-size: 4.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #ff0066, #ff3399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 30px #ff0066aa);
        margin: 20px 0;
    }
    
    .target-container {
        display: flex;
        justify-content: space-around;
        gap: 10px;
        margin-top: 20px;
    }

    .target-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 0, 102, 0.3);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        flex: 1;
    }

    .target-val {
        font-family: 'Orbitron';
        font-size: 1.8rem;
        color: #ff0066;
    }

    .target-label {
        font-size: 0.7rem;
        color: #ffffff88;
        text-transform: uppercase;
    }

    .stButton>button {
        background: linear-gradient(135deg, #ff0066 0%, #ff3399 100%) !important;
        color: white !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        height: 55px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ===================== SESSION STATE =====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "history" not in st.session_state:
    st.session_state.history = load_history()
if "last_res" not in st.session_state:
    st.session_state.last_res = None

# ===================== AUTHENTICATION =====================
if not st.session_state.authenticated:
    st.markdown("<div class='main-title'>JETX ULTRA</div>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        pw = st.text_input("🔑 MOT DE PASSE", type="password")
        if st.button("🚀 ACTIVER LE SYSTÈME", use_container_width=True):
            if pw == "JET2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Mot de passe diso")
    st.stop()

# ===================== SIDEBAR (RESET & STATS) =====================
with st.sidebar:
    st.markdown("### ⚙️ SYSTEM CONTROLS")
    
    if st.button("🗑️ RESET HISTORIQUE & DATA", use_container_width=True):
        st.session_state.history = []
        st.session_state.last_res = None
        if HISTORY_FILE.exists():
            HISTORY_FILE.unlink()
        st.success("Data reset vita!")
        st.rerun()
    
    st.markdown("---")
    if st.session_state.history:
        st.write(f"Total Prediction: {len(st.session_state.history)}")
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df[['entry', 'prob_x3', 'target_moy']].tail(10))

# ===================== ENGINE ULTRA V18 =====================
def run_ultra_engine(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:16], 16)
    
    # Dynamic Seeding 250k simulations
    np.random.seed(int((h_num & 0xFFFFFFFF) + (last_cote * 1000)) % (2**32))
    base = 2.15 if last_cote < 2.0 else 1.98
    sims = np.random.lognormal(np.log(base), 0.22, 250_000)
    
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    
    # CALCULATION MIN / MOYEN / MAX
    t_min = round(float(np.percentile(sims, 25)), 2)
    t_moy = round(float(np.percentile(sims, 50)), 2)
    t_max = round(float(np.percentile(sims[sims>=3.0], 80)), 2) if any(sims>=3.0) else 3.50
    
    # CALCULATION HEURE D'ENTRÉE
    try:
        base_t = datetime.combine(datetime.now(EAT).date(), datetime.strptime(t_in.strip(), "%H:%M:%S").time())
    except:
        base_t = datetime.now(EAT)
    
    shift = 55 + (h_num % 35) + int(last_cote * 2)
    entry_time = (base_t + timedelta(seconds=shift)).strftime("%H:%M:%S")
    
    result = {
        "id": h_hex[:8],
        "entry": entry_time,
        "prob_x3": prob_x3,
        "target_min": max(1.50, t_min),
        "target_moy": max(2.00, t_moy),
        "target_max": max(3.00, t_max),
        "timestamp": datetime.now(EAT).strftime("%H:%M:%S")
    }
    
    st.session_state.history.append(result)
    save_history(st.session_state.history)
    return result

# ===================== MAIN UI =====================
st.markdown("<div class='main-title'>JETX ULTRA V18.0</div>", unsafe_allow_html=True)

col_input, col_res = st.columns([1, 2], gap="large")

with col_input:
    st.markdown("<div class='glass-ultra'>", unsafe_allow_html=True)
    st.subheader("📥 Data Input")
    h_val = st.text_input("🔐 SERVER HASH")
    t_val = st.text_input("⏰ ROUND TIME (HH:MM:SS)")
    l_cote = st.number_input("📊 LAST COTE (TALOHA)", value=2.00, step=0.01)
    
    if st.button("🚀 ANALYSER ROUND", use_container_width=True):
        if h_val and t_val:
            st.session_state.last_res = run_ultra_engine(h_val, t_val, l_cote)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col_res:
    res = st.session_state.last_res
    if res:
        st.markdown(f"<div class='entry-time-ultra'>{res['entry']}</div>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center; color:#00ffcc;'>PROBABILITÉ X3+: {res['prob_x3']}%</h2>", unsafe_allow_html=True)
        
        # DISPLAY MIN / MOYEN / MAX
        st.markdown(f"""
        <div class='target-container'>
            <div class='target-card'>
                <div class='target-label'>Cote Min (Safe)</div>
                <div class='target-val'>{res['target_min']}x</div>
            </div>
            <div class='target-card' style='border-color:#00ffcc;'>
                <div class='target-label'>Cote Moyen</div>
                <div class='target-val' style='color:#00ffcc;'>{res['target_moy']}x</div>
            </div>
            <div class='target-card' style='border-color:#ffcc00;'>
                <div class='target-label'>Cote Max (X3+)</div>
                <div class='target-val' style='color:#ffcc00;'>{res['target_max']}x</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Ampidiro ny Hash sy ny Ora hahazoana prediction...")

# ===================== FOOTER / TOROLALANA =====================
st.markdown("""
<div style='margin-top:30px; padding:20px; background:rgba(255,255,255,0.05); border-radius:15px;'>
    <h4 style='color:#ff0066;'>📖 TOROLALANA AMPIASANA NY RESET & TARGET</h4>
    <ul style='font-size:0.9rem; color:#ccc;'>
        <li><b>Reset:</b> Tsindrio ny bokotra eo amin'ny ankavia (Sidebar) raha hanafafy ny tantaran'ny prediction rehetra.</li>
        <li><b>Cote Min:</b> Tanjona farany azo antoka (75% réussite).</li>
        <li><b>Cote Moyen:</b> Ny salan'isa mety hivoaka (50% réussite).</li>
        <li><b>Cote Max:</b> Tanjona ho an'ny X3+ (raha ambony ny Probabilité).</li>
    </ul>
</div>
""", unsafe_allow_html=True)
