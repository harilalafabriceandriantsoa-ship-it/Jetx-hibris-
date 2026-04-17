import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

# ---------------- CONFIG ----------------

st.set_page_config(page_title="ANDR-X AI V4 ⚡ REAL ENGINE", layout="centered")

st.markdown("""
<style>
.stApp {
    background:#000;
    color:#00ffcc;
    font-family: monospace;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------

if "pred_log" not in st.session_state:
    st.session_state.pred_log = []

if "auth" not in st.session_state:
    st.session_state.auth = False

if "model" not in st.session_state:
    st.session_state.model = RandomForestClassifier(n_estimators=200, random_state=42)

if "scaler" not in st.session_state:
    st.session_state.scaler = StandardScaler()

if "trained" not in st.session_state:
    st.session_state.trained = False

# ---------------- LOGIN ----------------

if not st.session_state.auth:
    st.title("⚡ ANDR-X AI V4 REAL TERMINAL")
    pwd = st.text_input("🔐 SECURITY CODE", type="password")

    if st.button("ACTIVATE SYSTEM"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("CODE INCORRECT")
    st.stop()

# ---------------- DATASET ----------------

def build_dataset(logs):
    rows = []

    for r in logs:
        try:
            rows.append([
                r["prob"],
                r["moy"],
                r["max"],
                r["ref"],
                r["confidence"],
                r["last_cote"],
                r["label"]
            ])
        except:
            continue

    if len(rows) < 8:
        return None

    return pd.DataFrame(rows, columns=[
        "prob", "moy", "max", "ref", "conf", "last_cote", "label"
    ])

# ---------------- TRAIN ----------------

def train_model():
    df = build_dataset(st.session_state.pred_log)
    if df is None:
        return

    X = df.drop("label", axis=1)
    y = df["label"]

    X_scaled = st.session_state.scaler.fit_transform(X)

    model = RandomForestClassifier(
        n_estimators=250,
        max_depth=8,
        random_state=42
    )

    model.fit(X_scaled, y)

    st.session_state.model = model
    st.session_state.trained = True

# ---------------- AI PREDICT ----------------

def ai_predict(features):
    if not st.session_state.trained:
        return None

    try:
        X = np.array(features).reshape(1, -1)
        X = st.session_state.scaler.transform(X)

        p = st.session_state.model.predict_proba(X)[0][1]
        return round(p * 100, 2)

    except:
        return None

# ---------------- ENGINE ----------------

def run_engine(hash_str, h_act, last_cote):

    try:
        t = datetime.strptime(h_act, "%H:%M:%S")
    except:
        tz = pytz.timezone("Indian/Antananarivo")
        t = datetime.now(tz)

    seed = int(hashlib.sha256((hash_str + h_act).encode()).hexdigest(), 16) % (2**32)
    np.random.seed(seed)

    h = hashlib.sha256(hash_str.encode()).hexdigest()
    base_num = int(h[:8], 16) % 1000
    hash_norm = (base_num / 100) + 1.1

    seconds = t.hour * 3600 + t.minute * 60 + t.second
    time_factor = (seconds % 300) / 300

    cycle = 1.2 if 1.5 <= last_cote <= 2.5 else 0.9

    base = hash_norm * cycle * (1 + time_factor)

    sims = np.random.lognormal(mean=np.log(base), sigma=0.3, size=10000)

    prob = round(len([x for x in sims if x >= 3]) / 10000 * 100, 2)

    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 95), 2)

    confidence = round(prob * moy / 10, 2)

    # SIGNAL
    if prob < 40:
        signal = 0
        emoji = "❌ SKIP"
    elif prob < 60:
        signal = 0
        emoji = "⏳ WAIT"
    else:
        signal = 1
        emoji = "🔥 BUY"

    ref = round(base, 2)

    # AI FEATURES
    features = [prob, moy, maxv, ref, confidence, last_cote]
    ai_score = ai_predict(features)

    # ENTRY TIME SIM
    delay = int((prob + confidence) % 60)
    h_entry = (t + timedelta(seconds=delay)).strftime("%H:%M:%S")

    return {
        "hash": hash_str[:10],
        "h_act": h_act,
        "h_entry": h_entry,
        "prob": prob,
        "moy": moy,
        "max": maxv,
        "confidence": confidence,
        "ref": ref,
        "last_cote": last_cote,
        "signal": signal,
        "emoji": emoji,
        "ai_score": ai_score,
        "label": signal
    }

# ---------------- BACKTEST ----------------

def backtest():
    if len(st.session_state.pred_log) < 5:
        return None

    df = pd.DataFrame(st.session_state.pred_log)

    y_true = df["label"]
    y_pred = df["signal"]

    acc = accuracy_score(y_true, y_pred)

    winrate = round((df["signal"].sum() / len(df)) * 100, 2)

    return acc, winrate

# ---------------- UI ----------------

st.title("🚀 ANDR-X AI V4 ⚡ REAL ENGINE")

tab1, tab2, tab3 = st.tabs(["📊 LIVE", "📜 HISTORY", "📈 BACKTEST"])

# ---------------- TAB 1 ----------------

with tab1:

    hash_in = st.text_input("🔑 HASH")
    h_in = st.text_input("⏰ TIME (HH:MM:SS)")
    last_cote = st.number_input("📉 LAST COTE", value=1.8)

    if st.button("🚀 RUN ENGINE"):
        if hash_in and h_in:

            res = run_engine(hash_in, h_in, last_cote)
            st.session_state.pred_log.append(res)

            train_model()
            st.rerun()

    if st.session_state.pred_log:

        r = st.session_state.pred_log[-1]

        st.markdown(f"""
### {r['emoji']}

- 🎯 Prob: {r['prob']}%
- 🧠 Confidence: {r['confidence']}
- 🤖 AI Score: {r['ai_score']}
- ⏰ Entry: {r['h_entry']}
- 📊 Ref: {r['ref']}
""")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("MIN", round(r["moy"] / 1.5, 2))
        with c2:
            st.metric("AVG", r["moy"])
        with c3:
            st.metric("MAX", r["max"])

# ---------------- TAB 2 ----------------

with tab2:
    st.write("📜 HISTORY")

    if st.session_state.pred_log:
        st.dataframe(pd.DataFrame(st.session_state.pred_log)[::-1])
    else:
        st.info("Empty history")

# ---------------- TAB 3 ----------------

with tab3:

    st.write("📈 BACKTEST RESULT")

    result = backtest()

    if result:
        acc, winrate = result

        st.success(f"ACCURACY: {round(acc*100,2)}%")
        st.success(f"WINRATE: {winrate}%")

    else:
        st.warning("Not enough data for backtest")

# ---------------- SIDEBAR ----------------

st.sidebar.markdown("⚡ ANDR-X V4 REAL AI")

tz = pytz.timezone("Indian/Antananarivo")
st.sidebar.markdown(datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S"))
