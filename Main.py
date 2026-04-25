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
    initial_sidebar_state="collapsed"
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

# ===================== CSS STYLING =====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');
    
    .stApp {
        background: radial-gradient(ellipse at 50% 0%, #1a0033 0%, #000008 60%, #001a1a 100%);
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* Title Style */
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: clamp(2rem, 8vw, 3.5rem);
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #ff0066, #ff3399, #00ffcc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .glass {
        background: rgba(10, 0, 25, 0.9);
        border: 2px solid rgba(255, 0, 102, 0.4);
        border-radius: 20px;
        padding: clamp(15px, 5vw, 25px);
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
    }

    /* INPUT STYLING - Eto ilay fanovana soratra ho mainty */
    .stTextInput input, .stNumberInput input {
        background-color: #ffffff !important; /* Fotsy ny ao anatiny */
        color: #000000 !important; /* MAINTY ny soratra ampidirinao */
        font-weight: 900 !important;
        border: 3px solid #ff0066 !important;
        border-radius: 12px !important;
        font-size: 1.1rem !important;
    }

    /* Placeholder (Soratra kely mampianatra) */
    ::placeholder {
        color: #666666 !important;
        opacity: 1;
    }

    .entry-mega {
        font-family: 'Orbitron', sans-serif;
        font-size: clamp(3rem, 12vw, 5rem);
        font-weight: 900;
        text-align: center;
        color: #ff0066;
        text-shadow: 0 0 30px #ff0066;
        margin: 20px 0;
    }
    
    .prob-mega {
        font-size: clamp(3rem, 10vw, 4.5rem);
        font-weight: 900;
        font-family: 'Orbitron';
        text-align: center;
        color: #00ffcc;
        margin: 15px 0;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #ff0066, #ff3399) !important;
        color: white !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        height: 55px !important;
        border: none !important;
        width: 100%;
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

# ===================== LOGIN =====================
if not st.session_state.auth:
    st.markdown("<div class='main-title'>JETX V19.0</div>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        pw = st.text_input("🔑 PASSWORD", type="password")
        if st.button("ACTIVATE"):
            if base64.b64encode(pw.encode()).decode() == "SkVUMjAyNg==":
                st.session_state.auth = True
                st.rerun()
            else: st.error("❌ Password diso")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='glass' style='max-width:850px; margin:20px auto;'>
        <h2 style='color:#ff0066; text-align:center;'>📖 FANAZAVANA MALAGASY</h2>
        <p>1. <b>HASH:</b> Ilay code lava avy @ casino (Provably Fair).<br>
        2. <b>TIME:</b> Ora nivoahan'ilay round teo aloha (HH:MM:SS).<br>
        3. <b>LAST COTE:</b> Multiplier nivoaka teo.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ===================== ML TRAINING ENGINE =====================
def train_ml():
    labeled = [h for h in st.session_state.history if h.get('result') in ['WIN', 'LOSS']]
    if len(labeled) < 10: 
        st.warning("⚠️ Mila data farafahakeliny 10 vao afaka manao Train.")
        return None, None
    
    X, y = [], []
    for h in labeled:
        hash_val = int(h['hash'][:12], 16) if len(h['hash']) >= 12 else 0
        X.append([hash_val % 1000, (hash_val >> 10) % 1000, h['last_cote'], h['prob'], h['conf'], h['strength']])
        y.append(1 if h['result'] == 'WIN' else 0)
    
    try:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(np.array(X))
        model = GradientBoostingRegressor(n_estimators=250, max_depth=6, learning_rate=0.05, random_state=42)
        model.fit(X_scaled, np.array(y))
        save_ml(model, scaler)
        st.success("✅ ML Model nohavaozina!")
        return model, scaler
    except: return None, None

# ===================== SIDEBAR (RESET & ML) =====================
with st.sidebar:
    st.markdown("### ⚙️ SETTINGS")
    if st.button("🧠 TRAIN ML (Intelligence)", use_container_width=True):
        m, s = train_ml()
        if m: st.session_state.ml_model, st.session_state.ml_scaler = m, s

    if st.button("🗑️ RESET DATA", use_container_width=True):
        st.session_state.history = []
        save_data([])
        st.success("Data voafafa!")
        st.rerun()

    st.markdown("---")
    if st.session_state.history:
        wins = sum(1 for h in st.session_state.history if h.get('result') == 'WIN')
        losses = sum(1 for h in st.session_state.history if h.get('result') == 'LOSS')
        total = wins + losses
        wr = round((wins/total)*100, 1) if total > 0 else 0
        st.metric("WIN RATE", f"{wr}%")

# ===================== ULTRA ENGINE V19 =====================
def run_ultra_v19(hash_in, time_in, last_cote):
    hash_hex = hashlib.sha512(hash_in.encode()).hexdigest()
    hash_num = int(hash_hex[:16], 16)
    seed_val = int((hash_num & 0xFFFFFFFFFFFFFFFF) + int(last_cote * 10000))
    np.random.seed(seed_val % (2**32))
    
    if last_cote < 1.5: base, sigma = 2.12, 0.24
    elif last_cote < 2.5: base, sigma = 2.06, 0.21
    elif last_cote < 3.5: base, sigma = 2.00, 0.19
    else: base, sigma = 1.96, 0.18
    
    base += (hash_num % 180) / 1200
    sims = np.random.lognormal(np.log(base), max(0.14, sigma), 350_000)
    
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    target_moy = max(2.60, round(float(np.percentile(sims, 50)), 2))
    conf = round(max(40, min(99, prob_x3 * 1.18 + last_cote * 13.0)), 2)
    strength = max(30.0, min(99.0, prob_x3 * 0.50 + conf * 0.30))
    
    now_mg = datetime.now(TZ_MG)
    total_shift = max(20, min(110, 48 + (hash_num % 90) - 45 + int(strength * 0.35)))
    entry_time = (now_mg + timedelta(seconds=total_shift)).strftime("%H:%M:%S")
    
    signal = "💎💎💎 ULTRA X3+" if strength >= 88 else "🔥🔥 STRONG X3+" if strength >= 76 else "🟢 GOOD X3+" if strength >= 62 else "⚠️ SKIP"
    
    result = {
        "id": hash_hex[:8], "timestamp": now_mg.strftime("%Y-%m-%d %H:%M:%S"),
        "hash": hash_in[:16], "time": time_in, "last_cote": last_cote,
        "entry": entry_time, "signal": signal, "prob": prob_x3, "conf": conf, "strength": strength,
        "moy": target_moy, "result": "PENDING"
    }
    st.session_state.history.append(result)
    save_data(st.session_state.history)
    return result

# ===================== MAIN UI =====================
st.markdown("<div class='main-title'>JETX ULTRA V19</div>", unsafe_allow_html=True)
col_in, col_out = st.columns([1, 2], gap="medium")

with col_in:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### 📥 FAMENOANA DATA")
    h_in = st.text_input("🔐 HASH", placeholder="Adikao eto ny Hash...")
    t_in = st.text_input("⏰ ORA TALOHA", placeholder="HH:MM:SS")
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
        st.markdown(f"<h2 style='text-align:center; color:#ff0066;'>{r['signal']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-mega'>{r['entry']}</div>", unsafe_allow_html=True)
        st.columns(3)[1].metric("PROBABILITÉ", f"{r['prob']}%")
        
        st.markdown("<br>", unsafe_allow_html=True)
        cw, cl = st.columns(2)
        with cw:
            if st.button("✅ WIN", use_container_width=True):
                for h in st.session_state.history:
                    if h['id'] == r['id']: h['result'] = 'WIN'
                save_data(st.session_state.history); st.rerun()
        with cl:
            if st.button("❌ LOSS", use_container_width=True):
                for h in st.session_state.history:
                    if h['id'] == r['id']: h['result'] = 'LOSS'
                save_data(st.session_state.history); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ===================== HISTORIQUE =====================
st.markdown("<h3 style='text-align:center; color:#00ffcc;'>📜 HISTORIQUE</h3>", unsafe_allow_html=True)
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history[::-1])
    st.dataframe(df[['timestamp', 'entry', 'signal', 'result']], use_container_width=True)
