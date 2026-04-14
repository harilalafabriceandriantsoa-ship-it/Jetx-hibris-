import streamlit as st
import numpy as np
import hashlib
import statistics
from datetime import datetime, timedelta
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG ----------------
st.set_page_config(page_title="ANDR-X AI V3 ⚡ TERMINAL", layout="centered")

st.markdown("""
<style>
.stApp {background:#000; color:#00ffcc;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "pred_log" not in st.session_state:
    st.session_state.pred_log = []

if "auth" not in st.session_state:
    st.session_state.auth = False

if "ml_model" not in st.session_state:
    st.session_state.ml_model = RandomForestClassifier(n_estimators=100)

if "ml_ready" not in st.session_state:
    st.session_state.ml_ready = False

# ---------------- LOGIN ----------------
if not st.session_state.auth:
    st.title("⚡ ANDR-X AI V3 TERMINAL")
    pwd = st.text_input("SECURITY CODE", type="password")

    if st.button("ACTIVATE SYSTEM"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# ---------------- AI DATASET ----------------
def build_dataset(history):
    data = []
    for h in history:
        if "ai_score" in h:
            continue

        data.append([
            h["prob"],
            h["moy"],
            h["max"],
            float(h["ref"]),
            h["confidence"],
            1 if "BUY" in h["signal"] else 0
        ])

    if len(data) < 5:
        return None

    return pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"])


# ---------------- TRAIN AI ----------------
def train_ai():
    df = build_dataset(st.session_state.pred_log)
    if df is None:
        return

    X = df.drop("label", axis=1)
    y = df["label"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestClassifier(n_estimators=150)
    model.fit(X_scaled, y)

    st.session_state.ml_model = model
    st.session_state.scaler = scaler
    st.session_state.ml_ready = True


# ---------------- AI PREDICT ----------------
def ai_predict(features):
    if not st.session_state.ml_ready:
        return None

    X = np.array(features).reshape(1, -1)
    X = st.session_state.scaler.transform(X)

    return round(st.session_state.ml_model.predict_proba(X)[0][1] * 100, 1)


# ---------------- ENGINE ----------------
def run_prediction(hash_str, h_act, last_cote):

    try:
        t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except:
        t_obj = datetime.now()

    # seed stable
    seed_global = int(hashlib.sha256((hash_str + h_act).encode()).hexdigest(), 16) % (2**32)
    np.random.seed(seed_global)

    # HASH
    hash_hex = hashlib.sha256(hash_str.encode()).hexdigest()
    hash_int = int(hash_hex[:8], 16) % 1000
    hash_norm = (hash_int / 100) + 1.1

    # TIME FACTOR
    t_seconds = t_obj.hour*3600 + t_obj.minute*60 + t_obj.second
    time_factor = (t_seconds % 300) / 300

    # CYCLE
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

    # REFERENCE
    if hash_norm < 2:
        ref_val = 2.1
    elif hash_norm < 3:
        ref_val = 2.2
    else:
        ref_val = 2.3

    ref_val += time_factor * 0.2

    base = hash_norm * ref_val * cycle * (1 + time_factor)

    sigma = 0.25 + (hash_norm / 10)

    # MONTE CARLO
    sims = np.random.lognormal(
        mean=np.log(base),
        sigma=sigma,
        size=15000
    )

    success = [s for s in sims if s >= 3.0]

    prob = round(len(success)/15000 * 100, 1)

    # NORMALISATION (stable)
    log_sims = np.log(sims + 1)

    moy = round(np.exp(np.mean(log_sims)) / 1.5, 2)
    maxv = round(np.exp(np.percentile(log_sims, 95)) / 1.2, 2)

    confidence = round((prob * moy)/10, 1)

    # HEURE D’ENTRÉE
    delay = int(50 + (hash_norm * 10) + (time_factor * 30) + (cycle * 10))
    h_ent = (t_obj + timedelta(seconds=delay)).strftime("%H:%M:%S")

    # SIGNAL
    if last_cote > 3:
        signal = "❌ SKIP"
    elif prob < 40 or moy < 2.3:
        signal = "❌ SKIP"
    elif prob < 55:
        signal = "⏳ WAIT"
    elif confidence > 12:
        signal = "🔥 STRONG BUY"
    else:
        signal = "✅ BUY"

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
        "ai_score": ai_score
    }


# ---------------- UI ----------------
st.title("🚀 ANDR-X AI V3 ⚡ TERMINAL")

tab1, tab2, tab3 = st.tabs(["📊 ANALYSE", "📜 HISTORIQUE", "📖 GUIDE"])

# ---------------- TAB 1 ----------------
with tab1:

    hash_in = st.text_input("HASH")
    h_in = st.text_input("HEURE", value=datetime.now().strftime("%H:%M:%S"))
    last_cote = st.number_input("CÔTE PRÉCÉDENTE", value=1.5)

    if st.button("RUN ENGINE"):
        if hash_in:
            res = run_prediction(hash_in, h_in, last_cote)
            st.session_state.pred_log.append(res)
            train_ai()
            st.rerun()

    if st.session_state.pred_log:
        r = st.session_state.pred_log[-1]

        st.markdown(f"""
### 🔥 SIGNAL: {r['signal']}
PROB X3+: {r['prob']}%  
CONFIDENCE: {r['confidence']}  
AI SCORE: {r['ai_score']}  
HEURE D’ENTRÉE: {r['h_ent']}
""")

        # CÔTE DISPLAY
        m1, m2, m3 = st.columns(3)

        with m1:
            st.markdown(f"📉 MIN\n**{round(r['moy']/1.3,2)}x**")

        with m2:
            st.markdown(f"📊 MOYEN\n**{r['moy']}x**")

        with m3:
            st.markdown(f"🚀 MAX\n**{r['max']}x**")


# ---------------- HISTORIQUE ----------------
with tab2:
    st.write("📜 HISTORIQUE COMPLET")
    st.write(st.session_state.pred_log)


# ---------------- GUIDE ----------------
with tab3:
    st.markdown("""
# 📖 ANDR-X AI V3 GUIDE

## 🎯 CÔTE RÉFÉRENCE
🔥 BEST: 1.80 → 2.50  
⏳ MED: 1.50 → 1.80  
❌ BAD: <1.50 ou >3

## ⏱ HEURE D’ENTRÉE
- dynamique
- hash + cycle + time factor
- window -5s → +10s

## ⚠️ SIGNAL
- SKIP ❌
- WAIT ⏳
- BUY ✅
- STRONG BUY 🔥

## 🤖 AI
- machine learning historique
- amélioration automatique
""")

# ---------------- SIDEBAR ----------------
st.sidebar.write("ANDR-X AI V3 ⚡ FINAL")
st.sidebar.write("STATUS: STABLE ENGINE")
st.sidebar.write(datetime.now().strftime("%d/%m/%Y"))
