import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG ----------------

st.set_page_config(page_title="ANDR-X AI V5 ⚡ REAL INTELLIGENCE", layout="centered")

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

if "ml_model" not in st.session_state:
    st.session_state.ml_model = RandomForestClassifier(n_estimators=250)

if "scaler" not in st.session_state:
    st.session_state.scaler = StandardScaler()

if "ml_ready" not in st.session_state:
    st.session_state.ml_ready = False


# ---------------- LOGIN ----------------

if not st.session_state.auth:
    st.title("⚡ ANDR-X AI V5 REAL TERMINAL")
    pwd = st.text_input("🔐 SECURITY CODE", type="password")

    if st.button("ACTIVATE SYSTEM"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()


# ---------------- TIME FEATURES ----------------

def extract_time_features(h_act):
    try:
        t = datetime.strptime(h_act, "%H:%M:%S")
    except:
        tz = pytz.timezone('Indian/Antananarivo')
        t = datetime.now(tz)

    return t, t.hour, t.minute


# ---------------- DATASET ----------------

def build_dataset(history):
    data = []

    for h in history:
        try:
            if all(k in h for k in ["prob","moy","max","ref","confidence","result","hour","minute"]):
                data.append([
                    h["prob"],
                    h["moy"],
                    h["max"],
                    h["ref"],
                    h["confidence"],
                    h["hour"],
                    h["minute"],
                    h["result"]
                ])
        except:
            continue

    if len(data) < 10:
        return None

    return pd.DataFrame(
        data,
        columns=["prob","moy","max","ref","conf","hour","minute","label"]
    )


# ---------------- TRAIN AI ----------------

def train_ai():
    df = build_dataset(st.session_state.pred_log)
    if df is None:
        return

    X = df.drop("label", axis=1)
    y = df["label"]

    X_scaled = st.session_state.scaler.fit_transform(X)

    model = RandomForestClassifier(n_estimators=300, random_state=42)
    model.fit(X_scaled, y)

    st.session_state.ml_model = model
    st.session_state.ml_ready = True


def ai_predict(features):
    if not st.session_state.ml_ready:
        return None

    X = np.array(features).reshape(1, -1)
    X = st.session_state.scaler.transform(X)

    return round(st.session_state.ml_model.predict_proba(X)[0][1] * 100, 1)


# ---------------- BACKTEST TIME ----------------

def hourly_stats():
    logs = st.session_state.pred_log
    stats = {}

    for h in logs:
        hour = h.get("hour", 0)

        if hour not in stats:
            stats[hour] = {"win":0, "total":0}

        stats[hour]["total"] += 1
        stats[hour]["win"] += h.get("result",0)

    return stats


def show_heatmap():
    stats = hourly_stats()

    st.subheader("📈 TIME WINRATE HEATMAP")

    if len(stats) == 0:
        st.info("Mbola tsisy data")
        return

    for h in sorted(stats.keys()):
        total = stats[h]["total"]
        win = stats[h]["win"]

        rate = round((win/total)*100,2) if total > 0 else 0

        st.write(f"🕐 {h}h → {rate}% | trades: {total}")


# ---------------- ENGINE ----------------

def run_prediction(hash_str, h_act, last_cote):

    tz = pytz.timezone('Indian/Antananarivo')

    t_obj, hour, minute = extract_time_features(h_act)

    # HASH CORE
    hash_hex = hashlib.sha256(hash_str.encode()).hexdigest()

    seed = int(hash_hex[:16], 16) % (2**32 - 1)
    np.random.seed(seed)

    hash_int = int(hash_hex[:8], 16) % 1000
    hash_norm = (hash_int / 100) + 1.1

    # TIME FACTOR
    time_factor = (hour * 60 + minute) % 300 / 300

    # CYCLE
    cycle = (
        0.8 if last_cote < 1.5 else
        1.0 if last_cote < 1.8 else
        1.3 if last_cote <= 2.5 else
        1.1 if last_cote <= 3 else
        0.7
    )

    ref_val = 2.1 if hash_norm < 2 else 2.2 if hash_norm < 3 else 2.3
    ref_val += time_factor * 0.3

    base = hash_norm * ref_val * cycle * (1 + time_factor)
    sigma = 0.2 + (hash_norm / 12)

    sims = np.random.lognormal(np.log(base), sigma, 14000)
    success = np.sum(sims >= 3.0)

    prob = round(success / 14000 * 100, 1)

    moy = round(np.exp(np.mean(np.log(sims + 1))) / 1.35, 2)
    maxv = round(np.exp(np.percentile(np.log(sims + 1), 95)) / 1.25, 2)

    confidence = round((prob * moy) / 10, 1)

    # ENTRY TIME (HASH + TIME AI CONTROLLED)
    h_seed = int(hash_hex[8:16], 16)
    h_seed2 = int(hash_hex[16:24], 16)
    h_seed3 = int(hash_hex[24:32], 16)

    delay = (
        (h_seed % 50) +
        (h_seed2 % 35) +
        (h_seed3 % 30) +
        int(hash_norm * 10) % 20 +
        int(cycle * 10) % 15 +
        (minute % 10)
    )

    if delay < 25:
        delay += 25

    h_ent = (t_obj + timedelta(seconds=delay)).strftime("%H:%M:%S")

    # SIGNAL
    if last_cote > 3:
        signal, emoji, result = "❌ SKIP", "❌", 0
    elif prob < 40 or moy < 2.2:
        signal, emoji, result = "❌ SKIP", "❌", 0
    elif prob < 55:
        signal, emoji, result = "⏳ WAIT", "⏳", 0
    else:
        signal, emoji, result = "✅ BUY", "🎯", 1

    features = [prob, moy, maxv, ref_val, confidence, hour, minute]
    ai_score = ai_predict(features)

    return {
        "hash": hash_str[:10] + "...",
        "h_act": h_act,
        "h_ent": h_ent,
        "prob": prob,
        "moy": moy,
        "max": maxv,
        "ref": round(ref_val,2),
        "confidence": confidence,
        "signal": signal,
        "emoji": emoji,
        "ai_score": ai_score,
        "result": result,
        "hour": hour,
        "minute": minute
    }


# ---------------- WINRATE ----------------

def winrate():
    logs = st.session_state.pred_log
    if len(logs) == 0:
        return 0

    win = sum([1 for x in logs if x["result"] == 1])
    return round((win / len(logs)) * 100, 2)


# ---------------- UI ----------------

st.title("🚀 ANDR-X AI V5 ⚡ REAL TIME INTELLIGENCE")

tab1, tab2, tab3 = st.tabs(["📊 ANALYSE", "📜 HISTORIQUE", "📈 TIME AI"])

with tab1:

    hash_in = st.text_input("🔑 HASH")
    h_in = st.text_input("⏰ HEURE (HH:MM:SS)")
    last_cote = st.number_input("📉 CÔTE PRÉCÉDENTE", value=1.5)

    if st.button("🚀 RUN ANALYSIS"):
        if hash_in and h_in:
            res = run_prediction(hash_in, h_in, last_cote)
            st.session_state.pred_log.append(res)
            train_ai()
            st.rerun()

    if st.session_state.pred_log:
        r = st.session_state.pred_log[-1]

        st.markdown(f"""
# {r['emoji']} {r['signal']}

🎯 PROB: {r['prob']}%  
🧠 CONF: {r['confidence']}  
🤖 AI: {r['ai_score']}%  
⏰ ENTRY: {r['h_ent']}
""")

with tab2:
    st.write(st.session_state.pred_log[::-1])

with tab3:
    st.metric("WINRATE", f"{winrate()} %")
    show_heatmap()

# ---------------- SIDEBAR ----------------

st.sidebar.title("ANDR-X V5")
tz = pytz.timezone('Indian/Antananarivo')
st.sidebar.write(datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S"))
