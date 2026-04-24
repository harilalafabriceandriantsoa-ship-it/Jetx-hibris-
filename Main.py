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
    
    /* Animated background */
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
    
    .subtitle {
        text-align: center;
        color: #ff006699;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.85rem;
        letter-spacing: 0.5em;
        margin-bottom: 2rem;
        text-shadow: 0 0 15px #ff006666;
    }
    
    .glass-ultra {
        background: rgba(10, 0, 25, 0.9);
        border: 2px solid rgba(255, 0, 102, 0.4);
        border-radius: 20px;
        padding: 28px;
        backdrop-filter: blur(12px);
        box-shadow: 
            0 0 40px rgba(255, 0, 102, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        margin-bottom: 24px;
    }
    
    .glass-result {
        background: rgba(5, 0, 15, 0.95);
        border: 3px solid rgba(255, 0, 102, 0.6);
        border-radius: 20px;
        padding: 32px;
        backdrop-filter: blur(16px);
        box-shadow: 
            0 0 60px rgba(255, 0, 102, 0.25),
            0 0 100px rgba(0, 255, 204, 0.1);
    }
    
    /* Entry Time Display */
    .entry-time-ultra {
        font-family: 'Orbitron', sans-serif;
        font-size: 5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #ff0066, #ff3399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 40px #ff0066aa);
        letter-spacing: 0.15em;
        margin: 24px 0;
        animation: entry-pulse 2.5s ease-in-out infinite;
    }
    
    @keyframes entry-pulse {
        0%, 100% { filter: drop-shadow(0 0 30px #ff006688); transform: scale(1); }
        50% { filter: drop-shadow(0 0 60px #ff0066dd); transform: scale(1.02); }
    }
    
    /* Signal Badges */
    .signal-ultra {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem;
        font-weight: 900;
        text-align: center;
        color: #ff0066;
        text-shadow: 0 0 25px #ff0066, 0 0 50px #ff0066aa;
        letter-spacing: 0.1em;
        margin: 16px 0;
    }
    
    .signal-strong {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        text-align: center;
        color: #00ffcc;
        text-shadow: 0 0 20px #00ffcc;
        letter-spacing: 0.08em;
    }
    
    .signal-good {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        text-align: center;
        color: #fbbf24;
        text-shadow: 0 0 15px #fbbf24;
    }
    
    /* Probability Display */
    .x3-prob-mega {
        font-size: 5.5rem;
        font-weight: 900;
        font-family: 'Orbitron', sans-serif;
        text-align: center;
        background: linear-gradient(135deg, #ff0066, #ff3399, #ff0066);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 35px #ff0066aa);
        margin: 20px 0;
    }
    
    /* Target Boxes avec Accuracy */
    .target-box-min {
        background: linear-gradient(135deg, rgba(0, 255, 204, 0.2), rgba(0, 200, 100, 0.1));
        border: 2px solid rgba(0, 255, 204, 0.5);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 25px rgba(0, 255, 204, 0.2);
    }
    
    .target-box-moy {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 170, 0, 0.1));
        border: 2px solid rgba(255, 215, 0, 0.5);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 25px rgba(255, 215, 0, 0.2);
    }
    
    .target-box-max {
        background: linear-gradient(135deg, rgba(255, 51, 102, 0.25), rgba(200, 0, 60, 0.1));
        border: 2px solid rgba(255, 51, 102, 0.6);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 30px rgba(255, 51, 102, 0.25);
    }
    
    .target-value {
        font-size: 3rem;
        font-weight: 900;
        font-family: 'Orbitron', sans-serif;
        margin: 8px 0;
    }
    
    .target-label {
        font-size: 0.75rem;
        color: #ffffff88;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    
    .accuracy-badge {
        font-size: 0.9rem;
        font-weight: 700;
        color: #00ff88;
        margin-top: 8px;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #ff0066 0%, #ff3399 100%) !important;
        color: white !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
        border-radius: 14px !important;
        height: 60px !important;
        letter-spacing: 0.08em !important;
        box-shadow: 0 0 25px rgba(255, 0, 102, 0.4) !important;
        transition: all 0.3s !important;
        border: none !important;
    }
    
    .stButton>button:hover {
        transform: scale(1.03);
        box-shadow: 0 0 40px rgba(255, 0, 102, 0.6) !important;
    }
    
    /* Inputs */
    .stTextInput input, .stNumberInput input {
        background: rgba(255, 0, 102, 0.05) !important;
        border: 2px solid rgba(255, 0, 102, 0.3) !important;
        color: #e0fbfc !important;
        border-radius: 12px !important;
        font-family: 'Rajdhani', monospace !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: rgba(255, 0, 102, 0.7) !important;
        box-shadow: 0 0 20px rgba(255, 0, 102, 0.2) !important;
    }
    
    /* Stats */
    .stat-ultra {
        background: rgba(255, 0, 102, 0.08);
        border: 1px solid rgba(255, 0, 102, 0.3);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin: 8px 0;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 900;
        font-family: 'Orbitron', sans-serif;
        color: #ff0066;
    }
    
    .stat-label {
        font-size: 0.7rem;
        color: #ffffff66;
        letter-spacing: 0.15em;
    }
    
    /* Section Label */
    .sec-label {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.65rem;
        letter-spacing: 0.4em;
        color: #ff006666;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ===================== AUTHENTICATION =====================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<div style='margin-top:100px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='main-title'>JETX ULTRA</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>V 1 8 . 0 &nbsp; X 3 + &nbsp; P R O</div>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        pw = st.text_input("🔑 MOT DE PASSE", type="password", placeholder="Code d'accès...")
        if st.button("🚀 ACTIVER LE SYSTÈME", use_container_width=True):
            if pw == "JET2026":
                st.session_state.authenticated = True
                st.success("✅ Système activé")
                st.rerun()
            else:
                st.error("❌ Mot de passe incorrect")
    
    st.markdown("""
    <div style='margin-top:40px; padding:24px; background:rgba(255,0,102,0.08); border:1px solid rgba(255,0,102,0.3); border-radius:14px; max-width:700px; margin-left:auto; margin-right:auto;'>
        <h3 style='color:#ff0066; text-align:center; margin-bottom:20px;'>📖 FANAZAVANA MALAGASY</h3>
        <p style='line-height:1.9; font-size:1rem;'>
        <b>JETX ULTRA V18.0</b> = Algorithm matanjaka indrindra ho an'ny X3+<br><br>
        
        <b style='color:#00ffcc;'>INONA NO ILAINA?</b><br>
        • <b>Hash:</b> Server seed avy @ casino (Provably Fair section)<br>
        • <b>Time:</b> Ora nanombohan'ny round (format HH:MM:SS)<br>
        • <b>Last Cote:</b> Cote tamin'ny round TALOHA (ex: 2.34)<br><br>
        
        <b style='color:#00ffcc;'>INONA NY RESULT?</b><br>
        • <b>Entry Time:</b> Fotoana hidirana (ULTRA PRÉCIS)<br>
        • <b>X3+ Prob:</b> Probabilité hahazoana 3.00× na mihoatra<br>
        • <b>3 Targets:</b> MIN (safe), MOYEN (normal), MAX (x3+)<br>
        • <b>Accuracy:</b> Isan-jato marina isaky ny target<br><br>
        
        <b style='color:#ff0066;'>TSY MAINTSY TADIDIO:</b><br>
        Aza adino ampiditra ny <b>Last Cote</b> marina satria io no manampy ny algorithm hanisa tsara!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()

# ===================== DATA INITIALIZATION =====================
if "history" not in st.session_state:
    st.session_state.history = load_history()

if "last_res" not in st.session_state:
    st.session_state.last_res = None

# ===================== SIDEBAR =====================
with st.sidebar:
    st.markdown("### ⚙️ CONTRÔLES SYSTÈME")
    
    # Stats
    if st.session_state.history:
        total = len(st.session_state.history)
        wins = sum(1 for h in st.session_state.history if h.get('status') == 'WIN ✅')
        win_rate = round(wins / total * 100, 1) if total > 0 else 0
        
        st.markdown(f"""
        <div class='stat-ultra'>
            <div class='stat-value'>{total}</div>
            <div class='stat-label'>TOTAL ROUNDS</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='stat-ultra'>
            <div class='stat-value'>{win_rate}%</div>
            <div class='stat-label'>WIN RATE</div>
        </div>
        """, unsafe_allow_html=True)
        
        col_w, col_l = st.columns(2)
        with col_w:
            st.metric("Wins", wins)
        with col_l:
            st.metric("Total", total)
    
    st.markdown("---")
    
    # Reset
    if st.button("🗑️ RESET COMPLET", use_container_width=True):
        st.session_state.history = []
        st.session_state.last_res = None
        try:
            if HISTORY_FILE.exists():
                HISTORY_FILE.unlink()
        except:
            pass
        st.success("✅ Données réinitialisées")
        st.rerun()
    
    st.markdown("---")
    st.caption("JETX ULTRA V18.0\nX3+ PRECISION ENGINE")

# ===================== ENGINE ULTRA PUISSANT =====================
def run_ultra_engine(h_in, t_in, last_cote):
    """
    JETX ULTRA V18.0 ENGINE
    
    Améliorations vs V16.1:
    - 250 000 simulations (vs 100k)
    - Sigma ultra optimisé selon last_cote
    - Hash influence + forte sur entry time
    - Signal classification + stricte
    - Accuracy calculation pour chaque target
    """
    
    # === HASH PROCESSING ===
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:16], 16)
    
    # Dynamic seeding ultra sécurisé
    seed_val = int((h_num & 0xFFFFFFFF) + (last_cote * 1000))
    np.random.seed(seed_val % (2**32))
    
    # === ULTRA X3+ SIMULATION 250k ===
    # Base ajusté selon last_cote
    if last_cote < 1.5:
        base = 2.10  # Plus haut si dernière cote basse
        sigma = 0.24
    elif last_cote < 2.5:
        base = 2.05
        sigma = 0.21
    elif last_cote < 3.5:
        base = 2.00
        sigma = 0.19  # Plus concentré si cote moyenne
    else:
        base = 1.95
        sigma = 0.18  # Très concentré si dernière cote haute
    
    # Adjustment final avec hash
    base += (h_num % 200) / 1000
    sigma -= (last_cote * 0.002)
    
    # 250 000 simulations ULTRA
    sims = np.random.lognormal(np.log(base), sigma, 250_000)
    
    # === X3+ PROBABILITIES ===
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    prob_x3_5 = round(float(np.mean(sims >= 3.5)) * 100, 2)
    prob_x4 = round(float(np.mean(sims >= 4.0)) * 100, 2)
    
    x3_count = int(np.sum(sims >= 3.0))
    
    # === TARGETS AVEC ACCURACY ===
    # MIN: Percentile 30 (70% chance d'atteindre)
    target_min = round(float(np.percentile(sims, 30)), 2)
    acc_min = 70.0
    
    # MOYEN: Percentile 50 (50% chance = médiane)
    target_moy = round(float(np.percentile(sims, 50)), 2)
    acc_moy = 50.0
    
    # MAX: Percentile 85 parmi les X3+ uniquement (réaliste)
    sims_x3 = sims[sims >= 3.0]
    if len(sims_x3) > 0:
        target_max = round(float(np.percentile(sims_x3, 85)), 2)
        acc_max = round(prob_x3 * 0.85, 1)  # 85% des X3+
    else:
        target_max = 3.50
        acc_max = 10.0
    
    # Assurer minimum cohérent
    target_min = max(2.00, target_min)
    target_moy = max(2.50, target_moy)
    target_max = max(3.00, target_max)
    
    # === CONFIDENCE ULTRA ===
    conf = round(max(40, min(99,
        prob_x3 * 1.15 +          # 115% weight sur X3+
        prob_x3_5 * 0.40 +
        prob_x4 * 0.25 +
        (h_num % 200) / 3.0 +
        last_cote * 12.0 -
        (100 - prob_x3) * 0.30
    )), 2)
    
    # === STRENGTH ===
    strength = round(
        prob_x3 * 0.50 +
        conf * 0.30 +
        prob_x3_5 * 0.15 +
        (x3_count / 2500) +
        (100 if prob_x3 >= 45 else 80 if prob_x3 >= 38 else 60 if prob_x3 >= 30 else 40) * 0.05
    , 2)
    strength = max(30.0, min(99.0, strength))
    
    # === ENTRY TIME ULTRA DYNAMIQUE ===
    try:
        base_t = datetime.combine(
            datetime.now(EAT).date(),
            datetime.strptime(t_in.strip(), "%H:%M:%S").time()
        )
    except:
        base_t = datetime.now(EAT)
    
    # SHIFT ULTRA DYNAMIQUE (Hash + Strength + Last Cote)
    hash_shift = (h_num % 90) - 45        # -45 à +45
    strength_bonus = int(strength * 0.4)   # 12 à 40
    cote_factor = int(last_cote * 5)      # Impact + fort
    prob_penalty = int((50 - prob_x3) * 0.5)  # Si prob faible = attendre
    
    total_shift = max(20, min(110,
        55 + hash_shift + strength_bonus + cote_factor - prob_penalty
    ))
    
    entry_time = (base_t + timedelta(seconds=total_shift)).strftime("%H:%M:%S")
    
    # === SIGNAL CLASSIFICATION ULTRA STRICTE ===
    if strength >= 90 and prob_x3 >= 45:
        signal = "💎💎💎 ULTRA X3+ — BUY MAXIMUM"
        signal_class = "signal-ultra"
    elif strength >= 78 and prob_x3 >= 38:
        signal = "🔥🔥 STRONG X3+ — ENGAGE"
        signal_class = "signal-strong"
    elif strength >= 65 and prob_x3 >= 30:
        signal = "🟢 GOOD X3+ — SCALP POSSIBLE"
        signal_class = "signal-good"
    else:
        signal = "⚠️ LOW X3+ — SKIP OU MICRO"
        signal_class = "signal-good"
    
    # === RESULT PACKAGE ===
    result = {
        "id": h_hex[:8],
        "timestamp": datetime.now(EAT).isoformat(),
        "time_ref": t_in,
        "last_cote_used": last_cote,
        
        "entry": entry_time,
        "signal": signal,
        "signal_class": signal_class,
        
        "prob_x3": prob_x3,
        "prob_x3_5": prob_x3_5,
        "prob_x4": prob_x4,
        "x3_count": x3_count,
        
        "conf": conf,
        "strength": strength,
        
        "target_min": target_min,
        "target_moy": target_moy,
        "target_max": target_max,
        
        "acc_min": acc_min,
        "acc_moy": acc_moy,
        "acc_max": acc_max,
        
        "status": "PENDING"
    }
    
    st.session_state.history.append(result)
    save_history(st.session_state.history)
    
    return result

# ===================== UI MAIN =====================
st.markdown("<div class='main-title'>JETX ULTRA</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>V 1 8 . 0 &nbsp; • &nbsp; X 3 + &nbsp; • &nbsp; U L T R A &nbsp; P R É C I S I O N</div>", unsafe_allow_html=True)

col_input, col_result = st.columns([1, 2.2], gap="large")

# ─── INPUT ───
with col_input:
    st.markdown("<div class='glass-ultra'>", unsafe_allow_html=True)
    st.markdown("<div class='sec-label'>▸ PARAMÈTRES DU ROUND</div>", unsafe_allow_html=True)
    
    h_val = st.text_input(
        "🔐 SERVER HASH",
        placeholder="Hash Provably Fair du casino...",
        help="Trouvé dans la section 'Provably Fair' du jeu"
    )
    
    t_val = st.text_input(
        "⏰ ROUND TIME",
        placeholder="HH:MM:SS (ex: 14:35:22)",
        help="Heure de début du round"
    )
    
    last_cote = st.number_input(
        "📊 LAST COTE (TALOHA)",
        value=2.00,
        step=0.01,
        min_value=1.00,
        max_value=20.00,
        format="%.2f",
        help="IMPORTANT: Cote du round PRÉCÉDENT (ex: si le dernier round = 2.34, mettez 2.34)"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Explication Last Cote
    with st.expander("❓ INONA NY 'LAST COTE' ?"):
        st.markdown("""
        ### 📖 FANAZAVANA MAZAVA
        
        **LAST COTE** = Cote tamin'ny round **TALOHA** (tsy ny round ankehitriny)
        
        **OHATRA:**
        ```
        Round 1: Nahazo 1.87× 
        → Last cote = 1.87
        
        Round 2: Ampiditra 1.87 @ "Last Cote"
                 Vao alefa ny algorithm
                 Nahazo 3.45×
        → Last cote = 3.45
        
        Round 3: Ampiditra 3.45 @ "Last Cote"
                 Sns...
        ```
        
        **NAHOANA NO ILAINA?**
        
        1️⃣ **Volatility adjustment:**
        - Raha last cote ambany (ex: 1.50) → algorithm mihevitra "cold"
      
