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
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data_storage"
DATA_DIR.mkdir(exist_ok=True, parents=True)

HISTORY_FILE = DATA_DIR / "history.json"

def save_history(history):
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except:
        pass

def load_history():
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
    except:
        return []
    return []

# ===================== CONFIG & STYLE =====================
st.set_page_config(page_title="JETX X3+ LASER V16.1", layout="wide")
EAT = pytz.timezone("Indian/Antananarivo")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;700&display=swap');
    .stApp { background: #000008; color: #e0fbfc; font-family: 'Rajdhani', sans-serif; }
    .main-title {
        font-family: 'Orbitron'; font-size: 3rem; text-align: center;
        background: linear-gradient(90deg, #ff0066, #00ffcc);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .glass-card {
        background: rgba(20, 0, 40, 0.8);
        border: 1px solid #ff0066;
        border-radius: 15px; padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(255, 0, 102, 0.2);
    }
    .entry-time {
        font-family: 'Orbitron'; font-size: 4rem; color: #ff0066;
        text-align: center; text-shadow: 0 0 30px #ff0066;
    }
    .metric-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ===================== AUTHENTICATION =====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<div style='margin-top:100px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='main-title'>X3+ LASER LOGIN</div>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        pw = st.text_input("PASSWORD", type="password", placeholder="Entrez le code d'accès...")
        if st.button("ACTIVATE SYSTEM", use_container_width=True):
            if pw == "JET2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect")
    st.stop()

# ===================== DATA INITIALIZATION =====================
if "history" not in st.session_state:
    st.session_state.history = load_history()

if "last_res" not in st.session_state:
    st.session_state.last_res = None

# SIDEBAR SETTINGS
with st.sidebar:
    st.header("⚙️ SYSTEM TOOLS")
    if st.button("🗑️ RESET ALL DATA"):
        st.session_state.history = []
        if HISTORY_FILE.exists():
            os.remove(HISTORY_FILE)
        st.session_state.last_res = None
        st.success("Toutes les données ont été effacées.")
        st.rerun()
    st.markdown("---")
    st.caption("JETX LASER V16.1 PRO")

# ===================== ENGINE =====================
def run_x3_engine(h_in, t_in, l_cote):
    # Hash to Number
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:16], 16)
    
    # Dynamic Seeding using Hash + Last Cote
    seed_val = int((h_num & 0xFFFFFFFF) * (l_cote * 100))
    np.random.seed(seed_val % (2**32))
    
    # Simulation Logic (Lognormal Distribution)
    # Rehefa ambany ny l_cote, dia mampitombo kely ny volatility ny engine
    volatility = 0.2 + (0.05 if l_cote < 1.5 else 0)
    sims = np.random.lognormal(np.log(2.2), volatility, 100_000)
    
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    
    # Target calculations
    c_min = round(float(np.percentile(sims, 35)), 2)
    c_avg = round(float(np.mean(sims)), 2)
    c_max = round(float(np.percentile(sims, 95)), 2)

    # Entry Time Calculation (Shift strategy)
    try:
        base_t = datetime.strptime(t_in.strip(), "%H:%M:%S")
        # Shift eo anelanelan'ny 45 hatramin'ny 55 segondra
        shift = 45 + (h_num % 10)
        entry_t = (base_t + timedelta(seconds=shift)).strftime("%H:%M:%S")
    except:
        entry_t = datetime.now(EAT).strftime("%H:%M:%S")

    res = {
        "id": h_hex[:8],
        "time_ref": t_in,
        "entry": entry_t,
        "prob": prob_x3,
        "min": max(2.5, c_min),
        "moyen": max(3.0, c_avg),
        "max": c_max,
        "signal": "💎 ULTRA X3+" if prob_x3 > 44 else "🔥 STRONG X3+",
        "status": "PENDING"
    }
    
    st.session_state.history.append(res)
    save_history(st.session_state.history)
    return res

# ===================== UI MAIN =====================
st.markdown("<div class='main-title'>JETX X3+ LASER</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#ff0066;'>V16.1 PRECISION ENGINE</p>", unsafe_allow_html=True)

col_in, col_out = st.columns([1, 2], gap="large")

with col_in:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📥 PARAMÈTRES ROUND")
    h_val = st.text_input("SERVER HASH", placeholder="Hash du round précédent...")
    t_val = st.text_input("ROUND TIME", placeholder="HH:MM:SS")
    l_cote = st.number_input("LAST COTE", value=2.00, step=0.01, min_value=1.00)
    
    if st.button("🚀 ANALYSE LASER", use_container_width=True):
        if h_val and t_val:
            with st.spinner("Simulation 100K en cours..."):
                st.session_state.last_res = run_x3_engine(h_val, t_val, l_cote)
                st.rerun()
        else:
            st.error("Veuillez remplir le Hash et le Time.")
    st.markdown("</div>", unsafe_allow_html=True)

with col_out:
    if st.session_state.last_res:
        r = st.session_state.last_res
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center; color:#ff0066; font-family:Orbitron;'>{r['signal']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-time'>{r['entry']}</div>", unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        with m1: 
            st.markdown(f"<div class='metric-container'><small>TARGET MIN</small><br><b style='font-size:1.5rem;'>{r['min']}x</b></div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-container'><small>MOYEN</small><br><b style='font-size:1.5rem;'>{r['moyen']}x</b></div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-container'><small>MAX POSS.</small><br><b style='font-size:1.5rem;'>{r['max']}x</b></div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center;'>PROBABILITÉ : <span style='color:#00ffcc;'>{r['prob']}%</span></h3>", unsafe_allow_html=True)
        
        if st.button("🎯 CONFIRM WIN (HIT)", use_container_width=True):
            for h in st.session_state.history:
                if h['id'] == r['id']: h['status'] = 'WIN ✅'
            save_history(st.session_state.history)
            st.success("Résultat enregistré !")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='glass-card' style='height:350px; display:flex; align-items:center; justify-content:center;'>
            <h3 style='color:rgba(255,255,255,0.2);'>EN ATTENTE D'ANALYSE...</h3>
        </div>
        """, unsafe_allow_html=True)

# History table
st.write("### 🕒 LOGS RÉCENTS")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history).iloc[::-1]
    # Re-order columns for clarity
    cols = ['entry', 'prob', 'min', 'moyen', 'max', 'status']
    available_cols = [c for c in cols if c in df.columns]
    st.dataframe(df[available_cols], use_container_width=True, hide_index=True)
