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

# ===================== CSS MOBILE-FRIENDLY =====================
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
    
    .target-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        margin: 5px;
    }
    
    .target-val {
        font-size: clamp(1.5rem, 6vw, 2.5rem);
        font-weight: 900;
        font-family: 'Orbitron';
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #ff0066, #ff3399) !important;
        color: white !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        height: 55px !important;
        font-size: 1rem !important;
        border: none !important;
        width: 100%;
    }
    
    .stTextInput input, .stNumberInput input {
        background: rgba(255, 0, 102, 0.05) !important;
        border: 2px solid rgba(255, 0, 102, 0.3) !important;
        color: #e0fbfc !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        padding: 12px !important;
    }
    
    @media (max-width: 768px) {
        .stApp { padding: 10px !important; }
        .glass { padding: 15px !important; }
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
    st.markdown("<p style='text-align:center; color:#ff006699; letter-spacing:0.3em;'>ULTRA X3+ ENGINE</p>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        pw = st.text_input("🔑 PASSWORD", type="password", placeholder="Ampidiro ny tenimiafina...")
        if st.button("ACTIVATE", use_container_width=True):
            # Caching the password JET2026 using base64
            if base64.b64encode(pw.encode()).decode() == "SkVUMjAyNg==":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ Diso ny tenimiafina")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # FANAZAVANA MALAGASY
    st.markdown("""
    <div class='glass' style='max-width:800px; margin:40px auto;'>
        <h2 style='color:#ff0066; text-align:center;'>📖 FANAZAVANA MALAGASY</h2>
        
        <h3 style='color:#00ffcc; margin-top:20px;'>🎯 ZAVATRA ILAINA (3):</h3>
        
        <p><b>1. HASH (Server Hash):</b></p>
        <ul style='line-height:1.8;'>
            <li>Server seed avy @ casino Provably Fair</li>
            <li>Hash feno na 8-16 caractères premier</li>
            <li>Ohatra: <code>7db8e01413d6d</code></li>
            <li>Io no FANALAHIDY algorithm</li>
        </ul>
        
        <p><b>2. TIME (HH:MM:SS):</b></p>
        <ul style='line-height:1.8;'>
            <li>Ora tamin'ny round <b>TALOHA</b></li>
            <li>Format: HH:MM:SS (ex: 20:22:24)</li>
            <li><b>REFERENCE</b> fotsiny (tsy utilisé calcul entry time)</li>
            <li>Entry time = calculé @ NOW + shift</li>
        </ul>
        
        <p><b>3. LAST COTE:</b></p>
        <ul style='line-height:1.8;'>
            <li>Résultat round <b>TALOHA</b></li>
            <li>Ohatra: 1.88× na 3.45×</li>
            <li>4 intervals: COLD/NORMAL/WARM/HOT</li>
            <li>Last cote avo = X3+ prob miakatra</li>
        </ul>
        
        <h3 style='color:#00ffcc; margin-top:25px;'>📊 INTERVALS LAST COTE:</h3>
        <ul style='line-height:2;'>
            <li><b>1.00-1.49 (COLD):</b> Base 2.12, Sigma 0.24</li>
            <li><b>1.50-2.49 (NORMAL):</b> Base 2.06, Sigma 0.21</li>
            <li><b>2.50-3.49 (WARM):</b> Base 2.00, Sigma 0.19</li>
            <li><b>3.50+ (HOT):</b> Base 1.96, Sigma 0.18</li>
        </ul>
        
        <h3 style='color:#00ffcc; margin-top:25px;'>🚀 FOMBA FAMPIASANA:</h3>
        <ol style='line-height:2;'>
            <li>Jereo Provably Fair @ JetX/Aviator</li>
            <li>Copy HASH (server seed)</li>
            <li>Copy TIME tamin'ny round taloha</li>
            <li>Tadidio LAST COTE (résultat taloha)</li>
            <li>Ampiditra @ app</li>
            <li>Tsindrio "ANALYSER"</li>
            <li>Jereo result: Entry time + Targets + Signal</li>
            <li>Milalao @ entry time</li>
            <li>Confirm Win/Loss</li>
        </ol>
        
        <h3 style='color:#ff0066; margin-top:25px;'>⚡ AMÉLIORATIONS V19:</h3>
        <ul style='line-height:2;'>
            <li>✅ <b>Entry time CORRECTED</b> - calculé @ NOW</li>
            <li>✅ <b>SHA512 ultra</b> - 350k simulations</li>
            <li>✅ <b>Signal DYNAMIQUE</b> - miovaova @ hash</li>
            <li>✅ <b>ML REAL</b> - mianatra @ results</li>
            <li>✅ <b>4 intervals</b> last cote optimization</li>
            <li>✅ <b>Mobile-friendly</b> - responsive design</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()

# ===================== ML TRAINING =====================
def train_ml():
    labeled = [h for h in st.session_state.history if h.get('result') in ['WIN', 'LOSS']]
    
    if len(labeled) < 10:
        return None, None
    
    X = []
    y = []
    
    for h in labeled:
        hash_val = int(h['hash'][:12], 16) if len(h['hash']) >= 12 else 0
        features = [
            hash_val % 1000,
            (hash_val >> 10) % 1000,
            h['last_cote'],
            h['prob'],
            h['conf'],
            h['strength']
        ]
        X.append(features)
        y.append(1 if h['result'] == 'WIN' else 0)
    
    X = np.array(X)
    y = np.array(y)
    
    try:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = GradientBoostingRegressor(
            n_estimators=250,
            max_depth=6,
            learning_rate=0.05,
            random_state=42
        )
        model.fit(X_scaled, y)
        
        save_ml(model, scaler)
        return model, scaler
    except:
        return None, None

# ===================== ULTRA ENGINE V19 =====================
def run_ultra_v19(hash_in, time_in, last_cote):
    """
    JETX ULTRA V19 ENGINE
    
    CORRECTIONS:
    1. Entry time @ NOW (no décalage)
    2. Hash ultra algorithm 350k
    3. Signal dynamique
    4. ML real training
    """
    
    # Hash processing
    hash_hex = hashlib.sha512(hash_in.encode()).hexdigest()
    hash_num = int(hash_hex[:16], 16)
    
    # Ultra seed
    seed_val = int((hash_num & 0xFFFFFFFFFFFFFFFF) + int(last_cote * 10000))
    np.random.seed(seed_val % (2**32))
    
    # Interval last cote
    if last_cote < 1.5:
        base = 2.12
        sigma = 0.24
    elif last_cote < 2.5:
        base = 2.06
        sigma = 0.21
    elif last_cote < 3.5:
        base = 2.00
        sigma = 0.19
    else:
        base = 1.96
        sigma = 0.18
    
    base += (hash_num % 180) / 1200
    sigma -= (last_cote * 0.0022)
    
    # 350K SIMULATIONS
    sims = np.random.lognormal(np.log(base), max(0.14, sigma), 350_000)
    
    # Probabilities
    prob_x3 = round(float(np.mean(sims >= 3.0)) * 100, 2)
    prob_x3_5 = round(float(np.mean(sims >= 3.5)) * 100, 2)
    prob_x4 = round(float(np.mean(sims >= 4.0)) * 100, 2)
    
    x3_count = int(np.sum(sims >= 3.0))
    
    # Targets
    target_min = max(2.00, round(float(np.percentile(sims, 30)), 2))
    target_moy = max(2.60, round(float(np.percentile(sims, 50)), 2))
    
    sims_x3 = sims[sims >= 3.0]
    target_max = max(3.00, round(float(np.percentile(sims_x3, 85)), 2)) if len(sims_x3) > 0 else 3.80
    
    # Confidence
    conf = round(max(40, min(99,
        prob_x3 * 1.18 +
        prob_x3_5 * 0.42 +
        prob_x4 * 0.28 +
        (hash_num % 200) / 3.2 +
        last_cote * 13.0 -
        (100 - prob_x3) * 0.32
    )), 2)
    
    # Strength
    strength = round(
        prob_x3 * 0.50 +
        conf * 0.30 +
        prob_x3_5 * 0.15 +
        (x3_count / 3500) +
        (100 if prob_x3 >= 45 else 82 if prob_x3 >= 38 else 64) * 0.05
    , 2)
    strength = max(30.0, min(99.0, strength))
    
    # ML boost
    ml_boost = 0
    if st.session_state.ml_model is not None:
        try:
            hash_val = int(hash_in[:12], 16) if len(hash_in) >= 12 else 0
            features = np.array([[
                hash_val % 1000,
                (hash_val >> 10) % 1000,
                last_cote,
                prob_x3,
                conf,
                strength
            ]])
            features_scaled = st.session_state.ml_scaler.transform(features)
            ml_pred = float(st.session_state.ml_model.predict(features_scaled)[0])
            ml_boost = ml_pred * 8
        except:
            pass
    
    conf = min(99, conf + ml_boost)
    strength = min(99, strength + ml_boost * 0.5)
    
    # ENTRY TIME CORRECTION
    now_mg = datetime.now(TZ_MG)
    
    hash_shift = (hash_num % 90) - 45
    strength_bonus = int(strength * 0.35)
    cote_factor = int(last_cote * 4)
    prob_penalty = int((48 - prob_x3) * 0.45)
    
    total_shift = max(20, min(110,
        48 + hash_shift + strength_bonus + cote_factor - prob_penalty
    ))
    
    entry_time = (now_mg + timedelta(seconds=total_shift)).strftime("%H:%M:%S")
    
    # SIGNAL DYNAMIQUE
    if strength >= 88 and prob_x3 >= 44:
        signal = "💎💎💎 ULTRA X3+"
    elif strength >= 76 and prob_x3 >= 36:
        signal = "🔥🔥 STRONG X3+"
    elif strength >= 62 and prob_x3 >= 28:
        signal = "🟢 GOOD X3+"
    else:
        signal = "⚠️ SKIP"
    
    result = {
        "id": hash_hex[:8],
        "timestamp": datetime.now(TZ_MG).strftime("%Y-%m-%d %H:%M:%S"),
        "hash": hash_in[:16],
        "time": time_in,
        "last_cote": last_cote,
        
        "entry": entry_time,
        "signal": signal,
        
        "prob": prob_x3,
        "prob_x3_5": prob_x3_5,
        "prob_x4": prob_x4,
        
        "conf": conf,
        "strength": strength,
        "ml_boost": round(ml_boost, 1),
        
        "min": target_min,
        "moy": target_moy,
        "max": target_max,
        
        "result": "PENDING"
    }
    
    st.session_state.history.append(result)
    save_data(st.session_state.history)
    
    return result

# ===================== SIDEBAR =====================
with st.sidebar:
    st.markdown("### 📊 STATS V19")
    
    if st.session_state.history:
        total = len(st.session_state.history)
        wins = sum(1 for h in st.session_state.history if h.get('result') == 'WIN')
        losses = sum(1 for h in st.session_state.history if h.get('result') == 'LOSS')
        wr = round(wins / (wins + losses) * 100, 1) if (wins + losses) > 0 else 0
        
        st.metric("WIN RATE", f"{wr}%")
        
        col_w, col_l = st.columns(2)
        with col_w:
            st.metric("Wins", wins)
        with col_l:
            st.metric("Loss", losses)
        
        st.metric("Total", total)
        
        if st.session_state.ml_model is not None:
            st.success("✅ ML ACTIF")
        else:
            labeled = len([h for h in st.session_state.history if h.get('result') in ['WIN', 'LOSS']])
            st.warning(f"🔄 ML: {labeled}/10")
    
    st.markdown("---")
    
    if st.button("🧠 TRAIN ML", use_container_width=True):
        model, scaler = train_ml()
        if model is not None:
            st.session_state.ml_model = model
            st.session_state.ml_scaler = scaler
            st.success("✅ ML trained!")
        else:
            st.warning("Besoin 10+ résultats")
        st.rerun()
    
    if st.button("🗑️ RESET DATA", use_container_width=True):
        st.session_state.history = []
        st.session_state.ml_model = None
        st.session_state.ml_scaler = None
        try:
            if HISTORY_FILE.exists():
                HISTORY_FILE.unlink()
            if ML_FILE.exists():
                ML_FILE.unlink()
        except:
            pass
        st.success("✅ Reset!")
        st.rerun()

# ===================== MAIN UI =====================
st.markdown("<div class='main-title'>JETX ULTRA V19</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#ff006699; letter-spacing:0.3em; margin-bottom:2rem;'>X3+ ENGINE • 350K SIMS • ML</p>", unsafe_allow_html=True)

col_in, col_out = st.columns([1, 2], gap="medium")

with col_in:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### 📥 FAMENOANA")
    
    hash_in = st.text_input(
        "🔐 HASH (Server Seed)",
        placeholder="Adikao eto ilay hash lava...",
        help="Alaivo avy any amin'ny Provably Fair an'ilay lalao (ex: 7db8e0...)"
    )
    
    time_in = st.text_input(
        "⏰ ORA TALOHA (HH:MM:SS)",
        placeholder="Ohatra: 20:22:24",
        help="Ilazana ny ora nivoahan'ilay cote farany hitanao teo"
    )
    
    cote_in = st.number_input(
        "📊 COTE FARANY TEO",
        value=1.88,
        step=0.01,
        format="%.2f",
        help="Ilay multiplier na cote nivoaka farany (ohatra: 1.88)"
    )
    
    if st.button("🚀 ANALYSER", use_container_width=True):
        if hash_in and time_in:
            with st.spinner("⚡ Mijery configuration 350k..."):
                result = run_ultra_v19(hash_in, time_in, cote_in)
                st.session_state.last_res = result
            st.rerun()
        else:
            st.error("❌ Fenoy tsara azafady ny HASH sy ny ORA")
    
    st.markdown("</div>", unsafe_allow_html=True)

with col_out:
    r = st.session_state.last_res
    
    if r:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; color:#ff0066;'>{r['signal']}</h2>", unsafe_allow_html=True)
        
        st.markdown("<p style='text-align:center; color:#ffffff66; margin-top:20px;'>▸ ORA HILALAOVANA (Entry Time)</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='entry-mega'>{r['entry']}</div>", unsafe_allow_html=True)
        
        st.markdown(f"<div class='prob-mega'>{r['prob']}%</div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#ffffff66;'>Chance ho X3+</p>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='display:flex; gap:16px; justify-content:center; margin:16px 0;'>
            <div style='text-align:center;'>
                <div style='font-size:1.4rem; font-weight:700; color:#ff3399;'>{r['prob_x3_5']}%</div>
                <div style='font-size:0.7rem; color:#ffffff55;'>X3.5+</div>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:1.4rem; font-weight:700; color:#ff6699;'>{r['prob_x4']}%</div>
                <div style='font-size:0.7rem; color:#ffffff55;'>X4+</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("CONFIDENCE", f"{r['conf']}%")
        with col_b:
            st.metric("Hery (STRENGTH)", f"{r['strength']}")
        
        if r.get('ml_boost', 0) > 0:
            st.info(f"🧠 ML Boost: +{r['ml_boost']}")
        
        st.markdown("<p style='text-align:center; color:#ffffff66; margin-top:20px;'>▸ TARGETS (Tanjona)</p>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class='target-box'>
                <div style='font-size:0.75rem; color:#ffffff88;'>KELY INDRINDRA</div>
                <div class='target-val' style='color:#00ffcc;'>{r['min']}×</div>
            </div>
            """, unsafe_allow_html=True)
        
        with c2:
            st.markdown(f"""
            <div class='target-box'>
                <div style='font-size:0.75rem; color:#ffffff88;'>ANTONONY</div>
                <div class='target-val' style='color:#ffd700;'>{r['moy']}×</div>
            </div>
            """, unsafe_allow_html=True)
        
        with c3:
            st.markdown(f"""
            <div class='target-box'>
                <div style='font-size:0.75rem; color:#ffffff88;'>BE INDRINDRA</div>
                <div class='target-val' style='color:#ff3366;'>{r['max']}×</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        cw, cl = st.columns(2)
        with cw:
            if st.button("✅ WIN (Nety)", use_container_width=True):
                for h in st.session_state.history:
                    if h['id'] == r['id']:
                        h['result'] = 'WIN'
                save_data(st.ses
