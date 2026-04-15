import streamlit as st  
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG ----------------
st.set_page_config(page_title="ANDR-X AI V3 ⚡ TERMINAL", layout="centered")

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
        if "ai_score" in h and h["ai_score"] is None:
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


def ai_predict(features):
    if not st.session_state.ml_ready or "scaler" not in st.session_state:
        return None

    X = np.array(features).reshape(1, -1)
    X = st.session_state.scaler.transform(X)
    return round(st.session_state.ml_model.predict_proba(X)[0][1] * 100, 1)

# ---------------- ENGINE ----------------
def run_prediction(hash_str, h_act, last_cote):

    try:
        t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except:
        tz_mg = pytz.timezone('Indian/Antananarivo')
        t_obj = datetime.now(tz_mg)

    seed_global = int(hashlib.sha256((hash_str + h_act).encode()).hexdigest(), 16) % (2**32)
    np.random.seed(seed_global)

    hash_hex = hashlib.sha256(hash_str.encode()).hexdigest()
    hash_int = int(hash_hex[:8], 16) % 1000
    hash_norm = (hash_int / 100) + 1.1

    t_seconds = t_obj.hour*3600 + t_obj.minute*60 + t_obj.second
    time_factor = (t_seconds % 300) / 300

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

    log_sims = np.log(sims + 1)
    moy = round(np.exp(np.mean(log_sims)) / 1.4, 2)
    maxv = round(np.exp(np.percentile(log_sims, 95)) / 1.2, 2)

    confidence = round((prob * moy)/10, 1)

    # ---------------- LEVEL GOD ENGINE 🔥 ----------------
    entry_score = round(
        (prob * 0.4) +
        (confidence * 3) +
        (moy * 10) +
        (50 if last_cote < 2.5 else 20), 1
    )

    entry_score = min(100, entry_score)

    countdown = max(5, int(60 - entry_score))

    decision = "❌ NO TRADE"
    if entry_score >= 75:
        decision = "🔥 STRONG ENTRY"
    elif entry_score >= 55:
        decision = "⏳ WAIT"
    else:
        decision = "❌ SKIP"

    h_ent = (t_obj + timedelta(seconds=countdown)).strftime("%H:%M:%S")

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
        "signal": decision,
        "entry_score": entry_score,
        "countdown": countdown,
        "ai_score": ai_score
    }

# ---------------- UI ----------------
st.title("🚀 ANDR-X AI V3 ⚡ TERMINAL")

tab1, tab2, tab3 = st.tabs(["📊 ANALYSE", "📜 HISTORIQUE", "📖 GUIDE"])

with tab1:

    hash_in = st.text_input("🔑 HASH")
    h_in = st.text_input("⏰ HEURE (HH:MM:SS)", value="")
    last_cote = st.number_input("📉 CÔTE PRÉCÉDENTE", value=1.5)

    if st.button("🚀 RUN ANALYSIS"):
        res = run_prediction(hash_in, h_in, last_cote)
        st.session_state.pred_log.append(res)
        train_ai()
        st.rerun()

    if st.session_state.pred_log:
        r = st.session_state.pred_log[-1]

        st.markdown(f"""
🔥 SIGNAL: {r['signal']}  
🎯 ENTRY SCORE: {r['entry_score']}/100  
⏳ COUNTDOWN: {r['countdown']}s  
⏰ ENTRY TIME: {r['h_ent']}  
🧠 AI SCORE: {r['ai_score']}%
""")

with tab2:
    st.dataframe(pd.DataFrame(st.session_state.pred_log))

with tab3:
    st.markdown("""
# 🔥 LEVEL GOD SYSTEM

✔ Entry Score 0-100  
✔ Countdown dynamique  
✔ Signal intelligent  
✔ AI filter  

⚠️ Tsy prediction 100% fa probabilistic system
""")
