import streamlit as st
import numpy as np
import hashlib
import statistics
from datetime import datetime, timedelta
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIGURATION ----------------
st.set_page_config(page_title="ANDR-X AI PREDICTOR V2", layout="centered")

# ---------------- STYLE (NEON LOOK) ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {background: #000000; color:#00ffcc; font-family: 'Orbitron', sans-serif;}
    .terminal-card {
        background: rgba(0, 255, 204, 0.05);
        padding: 20px; border-radius: 15px; border: 1px solid #00ffcc;
        margin-bottom: 20px;
    }
    .signal-box { font-size: 24px; font-weight: bold; text-align: center; padding: 10px; border-radius: 10px; margin: 10px 0; }
    .buy { background: rgba(0, 255, 0, 0.2); color: #00ff00; border: 1px solid #00ff00; }
    .skip { background: rgba(255, 0, 0, 0.2); color: #ff0000; border: 1px solid #ff0000; }
    .wait { background: rgba(255, 204, 0, 0.2); color: #ffcc00; border: 1px solid #ffcc00; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION INITIALIZATION ----------------
if "pred_log" not in st.session_state: st.session_state.pred_log = []
if "auth" not in st.session_state: st.session_state.auth = False
if "ml_model" not in st.session_state: st.session_state.ml_model = None
if "scaler" not in st.session_state: st.session_state.scaler = None
if "ml_ready" not in st.session_state: st.session_state.ml_ready = False

# ---------------- LOGIN ----------------
if not st.session_state.auth:
    st.title("⚡ HUBRIS SYSTEM")
    pwd = st.text_input("SECURITY CODE", type="password")
    if st.button("ACTIVATE"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# ---------------- AI FUNCTIONS (STABLE VERSION) ----------------
def build_dataset(history):
    data = []
    for h in history:
        # Tsy maintsy misy an'ireto features ireto vao azo ampiasaina ny data
        if all(k in h for k in ["prob", "moy", "max", "ref", "confidence", "signal"]):
            data.append([
                h["prob"],
                h["moy"],
                h["max"],
                float(h["ref"]),
                h["confidence"],
                1 if "BUY" in h["signal"] else 0
            ])
    if len(data) < 5: # Mila farafahakeliny 5 tours vao mianatra ny AI
        return None
    return pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"])

def train_ai():
    df = build_dataset(st.session_state.pred_log)
    if df is None: return

    try:
        X = df.drop("label", axis=1)
        y = df["label"]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = RandomForestClassifier(n_estimators=150)
        model.fit(X_scaled, y)

        st.session_state.ml_model = model
        st.session_state.scaler = scaler
        st.session_state.ml_ready = True
    except:
        pass

def ai_predict(features):
    if not st.session_state.ml_ready or st.session_state.ml_model is None:
        return "Learning..."
    
    try:
        X = np.array(features).reshape(1, -1)
        X_scaled = st.session_state.scaler.transform(X)
        score = st.session_state.ml_model.predict_proba(X_scaled)[0][1]
        return round(score * 100, 1)
    except:
        return "Wait..."

# ---------------- CORE ENGINE ----------------
def run_prediction(hash_str, h_act, last_cote):
    try:
        t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except:
        t_obj = datetime.now()

    # Stable seed generation
    seed_global = int(hashlib.sha256((hash_str + h_act).encode()).hexdigest(), 16) % (2**32)
    np.random.seed(seed_global)

    # Hash analysis
    hash_hex = hashlib.sha256(hash_str.encode()).hexdigest()
    hash_int = int(hash_hex[:8], 16) % 1000
    hash_norm = (hash_int / 100) + 1.1

    # Time & Cycle factors
    t_seconds = t_obj.hour*3600 + t_obj.minute*60 + t_obj.second
    time_factor = (t_seconds % 300) / 300

    # Dynamic Cycle Adjustment
    if last_cote < 1.5: cycle = 0.8
    elif last_cote < 1.8: cycle = 1.0
    elif last_cote <= 2.5: cycle = 1.3
    elif last_cote <= 3: cycle = 1.1
    else: cycle = 0.7

    # Reference Auto-tuning
    ref_val = 2.1 if hash_norm < 2 else 2.2 if hash_norm < 3 else 2.3
    ref_val += time_factor * 0.2

    # Neural Simulation
    seed_val = hash_norm * ref_val * cycle * (1 + time_factor)
    sigma = 0.25 + (hash_norm / 15)
    sims = np.random.lognormal(mean=np.log(seed_val), sigma=sigma, size=15000)

    prob = round(len([s for s in sims if s >= 3.0])/15000 * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 95), 2)
    confidence = round((prob * moy)/12, 1)

    # Entry delay calculation
    delay = int(45 + (hash_norm * 8) + (time_factor * 25))
    h_ent = (t_obj + timedelta(seconds=delay)).strftime("%H:%M:%S")

    # Signal Logic
    if last_cote > 4: signal = "❌ SKIP"
    elif prob < 40 or moy < 2.1: signal = "❌ SKIP"
    elif prob < 55: signal = "⏳ WAIT"
    elif confidence > 15: signal = "🔥 STRONG BUY"
    else: signal = "✅ BUY"

    # AI Score Calculation
    features = [prob, moy, maxv, ref_val, confidence]
    score = ai_predict(features)

    return {
        "h_act": h_act, "h_ent": h_ent, "hash": hash_str[:12]+"...",
        "ref": round(ref_val,2), "prob": prob, "moy": moy, "max": maxv,
        "confidence": confidence, "signal": signal, "ai_score": score
    }

# ---------------- UI INTERFACE ----------------
st.title("🚀 ANDR-X AI PREDICTOR V2")

tab1, tab2, tab3 = st.tabs(["📊 ANALYSE", "📜 HISTORIQUE", "📖 GUIDE"])

with tab1:
    with st.container():
        h_in_field = st.text_input("HASH (Copy from game)")
        col1, col2 = st.columns(2)
        with col1:
            ora_in = st.text_input("HEURE (HH:MM:SS)", value=datetime.now().strftime("%H:%M:%S"))
        with col2:
            cote_in = st.number_input("CÔTE PRÉCÉDENTE", value=1.5, step=0.01)

    if st.button("RUN PREDICTION"):
        if h_in_field:
            res = run_prediction(h_in_field, ora_in, cote_in)
            st.session_state.pred_log.append(res)
            if len(st.session_state.pred_log) >= 5:
                train_ai()
            st.rerun()
        else:
            st.error("Azafady, ampidiro ny HASH!")

    if st.session_state.pred_log:
        r = st.session_state.pred_log[-1]
        
        # Signal CSS Class
        sig_class = "buy" if "BUY" in r['signal'] else "skip" if "SKIP" in r['signal'] else "wait"
        
        st.markdown(f"""
        <div class='terminal-card'>
            <div class='signal-box {sig_class}'>{r['signal']}</div>
            <p style='text-align:center; font-size:18px;'>
                <b>PROB X3+:</b> {r['prob']}% | <b>CONFIDENCE:</b> {r['confidence']}<br>
                <b>AI SCORE:</b> <span style='color:#fff;'>{r['ai_score']}%</span>
            </p>
            <hr style='border: 0.5px solid #333;'>
            <h2 style='text-align:center; color:#fff;'>🕒 {r['h_ent']}</h2>
            <p style='text-align:center; font-size:12px; color:#aaa;'>ORA TOKONY HIDIRANA (HEURE D'ENTRÉE)</p>
        </div>
        """, unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("MOYEN", f"{r['moy']}x")
        m2.metric("MAX", f"{r['max']}x")
        m3.metric("REF", f"{r['ref']}")

with tab2:
    if st.session_state.pred_log:
        df_hist = pd.DataFrame(st.session_state.pred_log)
        st.dataframe(df_hist[::-1], use_container_width=True)
    else:
        st.info("Mbola tsy misy tantara voatahiry.")

with tab3:
    st.markdown("""
    ### 📖 Torolàlana V2 AI
    1. **HASH**: Dikaovy ny Hash avy amin'ny lalao.
    2. **HEURE**: Ny ora nivoahan'ny tour farany.
    3. **CÔTE**: Ny vokatra (multiplier) nivoaka teo aloha.
    
    **Inona ny AI SCORE?**
    - Io dia kajy avy amin'ny **Machine Learning**. Miandrasa tours **5** farafahakeliny vao mipoitra ny isa marina.
    - Arakaraka ny habetsaky ny data (Historique) no maha-marina azy.
    """)

st.sidebar.write(f"**ADMIN:** ANDR-X")
st.sidebar.write(f"**MODE:** AI HYBRID ACTIVE")
st.sidebar.info("Aza adino ny manao 'Refresh' raha misy fahatarana ny server.")
