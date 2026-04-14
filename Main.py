import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta, timezone
import pandas as pd

# Mba tsy hisian'ny fahadisoana 'sklearn' dia apetraho ao amin'ny requirements.txt ireto
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
except ImportError:
    st.error("⚠️ Mila apetraka ny 'scikit-learn'. Ampidiro ao amin'ny requirements.txt izy.")

# ---------------- CONFIG ----------------
st.set_page_config(page_title="ANDR-X AI V3 ⚡ TERMINAL", layout="centered")

# Ora Madagasikara (UTC+3)
madagasikara_tz = timezone(timedelta(hours=3))
ora_izao = datetime.now(madagasikara_tz).strftime("%H:%M:%S")

st.markdown("""
<style>
.stApp {background:#000; color:#00ffcc; font-family: monospace;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "pred_log" not in st.session_state:
    st.session_state.pred_log = []

if "auth" not in st.session_state:
    st.session_state.auth = False

if "ml_model" not in st.session_state:
    st.session_state.ml_model = RandomForestClassifier(n_estimators=120)

if "ml_ready" not in st.session_state:
    st.session_state.ml_ready = False

# ---------------- LOGIN ----------------
if not st.session_state.auth:
    st.title("⚡ ANDR-X AI V3 TERMINAL")
    pwd = st.text_input("🔐 SECURITY CODE", type="password")

    if st.button("ACTIVATE SYSTEM"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# ---------------- AI TRAIN ----------------
def build_dataset(history):
    data = []
    for h in history:
        # Tsy ampiasaina ny andrana tsy misy signal
        if "signal" not in h:
            continue

        data.append([
            h["prob"],
            h["moy"],
            h["max"],
            float(h["ref"]),
            h["confidence"],
            1 if "BUY" in h["signal"] else 0
        ])

    # Mila andrana 5 farafahakeliny vao mianatra ny AI
    if len(data) < 5:
        return None

    return pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"])

def train_ai():
    df = build_dataset(st.session_state.pred_log)
    if df is None:
        return

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
    except Exception as e:
        st.error(f"Erreur Training: {e}")

def ai_predict(features):
    # Raha mbola tsy ready ny AI (latsaky ny 5 tours), miverina None
    if not st.session_state.ml_ready or "scaler" not in st.session_state:
        return None

    try:
        X = np.array(features).reshape(1, -1)
        X = st.session_state.scaler.transform(X)
        # Isan-jato (probability)
        return round(st.session_state.ml_model.predict_proba(X)[0][1] * 100, 1)
    except:
        return None

# ---------------- ENGINE ----------------
def run_prediction(hash_str, h_act, last_cote):

    try:
        t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except:
        t_obj = datetime.now(madagasikara_tz)

    seed_global = int(hashlib.sha256((hash_str + h_act).encode()).hexdigest(), 16) % (2**32)
    np.random.seed(seed_global)

    hash_hex = hashlib.sha256(hash_str.encode()).hexdigest()
    hash_int = int(hash_hex[:8], 16) % 1000
    hash_norm = (hash_int / 100) + 1.1

    t_seconds = t_obj.hour*3600 + t_obj.minute*60 + t_obj.second
    time_factor = (t_seconds % 300) / 300

    # cycle lojika
    if last_cote < 1.5:
        cycle = 0.8
    elif last_cote < 1.8:
        cycle = 1.0
    elif last_cote <= 2.5:
        cycle = 1.3
    elif last_cote <= 3:
        cycle = 1.1
    else:
        cycle = 0.7

    ref_val = 2.1 if hash_norm < 2 else 2.2 if hash_norm < 3 else 2.3
    ref_val += time_factor * 0.2

    base = hash_norm * ref_val * cycle * (1 + time_factor)
    sigma = 0.25 + (hash_norm / 10)

    sims = np.random.lognormal(mean=np.log(base), sigma=sigma, size=15000)
    success = [s for s in sims if s >= 3.0]
    prob = round(len(success)/15000 * 100, 1)

    # ---------------- NORMALISATION ----------------
    log_sims = np.log(sims + 1)
    moy_raw = np.exp(np.mean(log_sims))
    max_raw = np.exp(np.percentile(log_sims, 95))

    moy = round(moy_raw / 1.4, 2)
    maxv = round(max_raw / 1.2, 2)
    confidence = round((prob * moy)/10, 1)

    delay = int(50 + (hash_norm * 10) + (time_factor * 30) + (cycle * 10))
    h_ent = (t_obj + timedelta(seconds=delay)).strftime("%H:%M:%S")

    # ---------------- SIGNAL ----------------
    if last_cote > 3:
        signal, emoji = "❌ SKIP", "❌"
    elif prob < 40 or moy < 2.3:
        signal, emoji = "❌ SKIP", "❌"
    elif prob < 55:
        signal, emoji = "⏳ WAIT", "⏳"
    elif confidence > 12:
        signal, emoji = "🔥 STRONG BUY", "🔥🎯"
    else:
        signal, emoji = "✅ BUY", "🎯"

    features = [prob, moy, maxv, ref_val, confidence]
    ai_score = ai_predict(features)

    return {
        "h_act": h_act,
        "h_ent": h_ent,
        "hash": hash_str[:10]+"...",
        "ref": round(ref_val,2),
        "prob": prob,
        "moy": moy,
        "max": maxv,
        "confidence": confidence,
        "signal": signal,
        "emoji": emoji,
        "ai_score": ai_score
    }

# ---------------- UI ----------------
st.title("🚀 ANDR-X AI V3 ⚡ Madagasikara")

tab1, tab2, tab3 = st.tabs(["📊 ANALYSE", "📜 HISTORIQUE", "📖 GUIDE"])

with tab1:
    hash_in = st.text_input("🔑 HASH")
    h_in = st.text_input("⏰ HEURE (MADAGASCAR)", value=ora_izao)
    last_cote = st.number_input("📉 CÔTE PRÉCÉDENTE", value=1.5)

    if st.button("🚀 RUN ANALYSIS"):
        if hash_in:
            res = run_prediction(hash_in, h_in, last_cote)
            st.session_state.pred_log.append(res)
            train_ai() # Mianatra isaky ny misy andrana vaovao
            st.rerun()

    if st.session_state.pred_log:
        r = st.session_state.pred_log[-1]
        
        # Raha None ny ai_score dia mampiseho hafatra
        ai_display = f"{r['ai_score']}%" if r['ai_score'] is not None else "Learning... (Mila 5 tours)"

        st.markdown(f"""
        # {r['emoji']} SIGNAL: {r['signal']}
        🎯 PROB X3+: **{r['prob']}%** 🧠 CONFIDENCE: **{r['confidence']}** 🤖 AI SCORE: **{ai_display}** ⏰ HEURE D’ENTRÉE: **{r['h_ent']}**
        """)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"📉 MIN\n**{round(r['moy']/1.5,2)}x**")
        with m2:
            st.markdown(f"📊 MOYEN\n**{r['moy']}x**")
        with m3:
            st.markdown(f"🚀 MAX\n**{r['max']}x**")

with tab2:
    st.write("📜 TANTARAN'NY ANALYSE")
    if st.session_state.pred_log:
        st.dataframe(pd.DataFrame(st.session_state.pred_log)[::-1])
    else:
        st.info("Mbola tsisy andrana natao.")

with tab3:
    st.markdown("### 📖 TOROLÀLANA\n1. Ampidiro ny HASH farany.\n2. Jereo raha mifanaraka ny ORA.\n3. Andraso ho feno 5 ny tantara vao hiseho ny AI SCORE.")

# ---------------- SIDEBAR ----------------
st.sidebar.markdown(f"⚡ **ANDR-X AI V3**\nOra Madagasikara: {ora_izao}")
st.sidebar.markdown(f"📅 {datetime.now(madagasikara_tz).strftime('%d/%m/%Y')}")
