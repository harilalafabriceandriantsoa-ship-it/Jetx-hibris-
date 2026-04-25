import streamlit as st 
import numpy as np
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import pytz
import json
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import base64

# ===================== CONFIG =====================
st.set_page_config(
    page_title="JETX ULTRA V19.0 X3+", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== PERSISTENCE =====================
try:
    DATA_DIR = Path(__file__).parent / "jetx_v19_data"
except:
    DATA_DIR = Path.cwd() / "jetx_v19_data"

DATA_DIR.mkdir(exist_ok=True, parents=True)
HISTORY_FILE = DATA_DIR / "history.json"
ML_FILE = DATA_DIR / "ml_model.pkl"

def save_data(data):
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except: pass

def load_data():
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except: pass
    return []

def save_ml(model, scaler):
    try:
        with open(ML_FILE, 'wb') as f:
            pickle.dump({'model': model, 'scaler': scaler}, f)
    except: pass

def load_ml():
    try:
        if ML_FILE.exists():
            with open(ML_FILE, 'rb') as f:
                data = pickle.load(f)
                return data['model'], data['scaler']
    except: pass
    return None, None

# ===================== CSS ULTRA V19 (REFIXED) =====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');
    
    .stApp {
        background: radial-gradient(ellipse at 50% 0%, #1a0033 0%, #000008 60%, #001a1a 100%);
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }
    
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: clamp(2rem, 8vw, 3.5rem);
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #ff0066, #ff3399, #00ffcc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .glass {
        background: rgba(10, 0, 25, 0.9);
        border: 2px solid rgba(255, 0, 102, 0.4);
        border-radius: 20px;
        padding: 20px;
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
    }
    
    /* MANAMAFY NY LOKON'NY SORATRA AO ANATY INPUT */
    .stTextInput input, .stNumberInput input {
        background: rgba(255, 255, 255, 0.15) !important;
        border: 2px solid #ff0066 !important;
        color: #FFFFFF !important; /* Fotsy tanteraka ny soratra soratanao */
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        border-radius: 12px !important;
    }
    
    /* MANAMAFY NY SORATRA ONDRY (PLACEHOLDER) */
    ::placeholder {
        color: rgba(255, 255, 255, 0.9) !important; /* Fotsy be ilay ohatra */
        font-weight: bold !important;
    }

    .entry-mega {
        font-family: 'Orbitron', sans-serif;
        font-size: clamp(3rem, 12vw, 5rem);
        font-weight: 900;
        text-align: center;
        color: #ff0066;
        text-shadow: 0 0 30px #ff0066;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #ff0066, #ff3399) !important;
        color: white !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        height: 55px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ===================== SESSION STATE =====================
if "auth" not in st.session_state:
    st.session_state.auth = False
if "history" not in st.session_state:
    st.session_state.history = load_data()
if "last_res" not in st.session_state:
    st.session_state.last_res = None
if "ml_model" not in st.session_state:
    st.session_state.ml_model, st.session_state.ml_scaler = load_ml()

TZ_MG = pytz.timezone("Indian/Antananarivo")

# ===================== LOGIN & FANAZAVANA =====================
if not st.session_state.auth:
    st.markdown("<div class='main-title'>JETX V19.0</div>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        pw = st.text_input("🔑 PASSWORD", type="password", placeholder="JET2026")
        if st.button("ACTIVATE", use_container_width=True):
            if pw == "JET2026": # Notsotsoriko mba tsy hisy fahadisoana
                st.session_state.auth = True
                st.rerun()
            else: st.error("❌ Password diso")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='glass' style='max-width:850px; margin:20px auto;'>
        <h2 style='color:#ff0066; text-align:center;'>📖 FANAZAVANA MALAGASY</h2>
        <h3 style='color:#00ffcc;'>1. HASH (Server Seed)</h3>
        <p>Ity no fanalahidy mibaiko ny round ho avy. Raiso ao amin'ny casino ny Hash farany.</p>
        <h3 style='color:#00ffcc;'>2. TIME (Ora taloha)</h3>
        <p>Ny ora nivoahan'ilay round teo aloha (HH:MM:SS).</p>
        <h3 style='color:#00ffcc;'>3. COTE (Multiplier)</h3>
        <p>Ny isa nivoaka teo (ohatra: 2.15). Io no manome ny 'Energy' an'ny simulation.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ===================== ML TRAINING =====================
def train_ml():
    labeled = [h for h in st.session_state.history if h.get('result') in ['WIN', 'LOSS']]
    if len(labeled) < 10: return None, None
    X, y = [], []
    for h in labeled:
        hash_val = int(hashlib.md5(h['hash'].encode()).hexdigest()[:12], 16)
        X.append([hash_val % 1000, (hash_val >> 10) % 1000, h['last_cote'], h['prob'], h['conf'], h['strength']])
        y.append(1 if h['result'] == 'WIN' else 0)
    try:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(np.array(X))
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X_scaled, np.array(y))
        save_ml(model, scaler)
        return model, scaler
    except: return None, None

# ===================== ULTRA ENGINE V19 =====================
def run_ultra_v19(hash_in, time_in, last_cote):
    hash_hex = hashlib.sha512(hash_in.encode()).hexdigest()
    hash_num = int(hash_hex[:16], 16)
    np.random.seed(hash_num % (2**32))
    
    base = 2.05 if last_cote < 2 else 1.95
    sims = np.random.lognormal(np.log(base), 0.2, 100_000)
    
    prob = round(float(np.mean(sims >= 3.0)) * 100, 2)
    strength = max(40, min(99, prob * 1.2 + (last_cote * 5)))
    
    now_mg = datetime.now(TZ_MG)
    entry_time = (now_mg + timedelta(seconds=65)).strftime("%H:%M:%S")
    
    result = {
        "id": hash_hex[:8], "timestamp": now_mg.strftime("%H:%M:%S"),
        "hash": hash_in, "time": time_in, "last_cote": last_cote,
        "entry": entry_time, "signal": "💎 ULTRA X3+" if strength > 75 else "⚠️ SKIP",
        "prob": prob, "conf": strength, "strength": strength,
        "min": round(base, 2), "moy": round(base+0.5, 2), "max": round(base+1.5, 2), "result": "PENDING"
    }
    st.session_state.history.append(result)
    save_data(st.session_state.history)
    return result

# ===================== SIDEBAR (RESET DATA AZA ATO) =====================
with st.sidebar:
    st.markdown("### 🛠️ TOOLS")
    if st.button("🗑️ RESET DATA", use_container_width=True):
        st.session_state.history = []
        save_data([])
        st.success("Data nodiovina!")
        st.rerun()
    
    if st.button("🧠 TRAIN ML", use_container_width=True):
        model, scaler = train_ml()
        if model: 
            st.session_state.ml_model, st.session_state.ml_scaler = model, scaler
            st.success("ML Model vonona!")
        else: st.warning("Mila data 10 farafahakeliny.")

# ===================== MAIN UI =====================
st.markdown("<div class='main-title'>JETX ULTRA V19</div>", unsafe_allow_html=True)
col_in, col_out = st.columns([1, 1.5])

with col_in:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### 📥 FAMENOANA DATA")
    h_in = st.text_input("🔐 HASH", placeholder="Ampidiro ny Hash eto...")
    t_in = st.text_input("⏰ ORA TALOHA", placeholder="HH:MM:SS (ohatra: 14:15:02)")
    c_in = st.number_input("📊 COTE FARANY", value=1.88, step=0.01)
    
    if st.button("🚀 ANALYSER", use_container_width=True):
        if h_in and t_in:
            st.session_state.last_res = run_ultra_v19(h_in, t_in, c_in)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col_out:
    r = st.session_state.last_res
    if r:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center;'>{r['signal']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-mega'>{r['entry']}</div>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center; color:#00ffcc;'>PROBABILITÉ: {r['prob']}%</h3>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        if c1.button("✅ WIN", use_container_width=True):
            st.session_state.history[-1]['result'] = 'WIN'
            save_data(st.session_state.history); st.rerun()
        if c2.button("❌ LOSS", use_container_width=True):
            st.session_state.history[-1]['result'] = 'LOSS'
            save_data(st.session_state.history); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ===================== HISTORIQUE =====================
if st.session_state.history:
    st.markdown("### 📜 HISTORIQUE")
    df = pd.DataFrame(st.session_state.history[::-1])
    st.table(df[['timestamp', 'entry', 'signal', 'result']].head(10))
