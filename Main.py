import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG ----------------

st.set_page_config(page_title="ANDR-X AI V7 ⚡ ULTRA TIME ENGINE", layout="centered")

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
    st.session_state.ml_model = RandomForestClassifier(n_estimators=350)

if "scaler" not in st.session_state:
    st.session_state.scaler = StandardScaler()

if "ml_ready" not in st.session_state:
    st.session_state.ml_ready = False


# ---------------- LOGIN ----------------

if not st.session_state.auth:
    st.title("⚡ ANDR-X AI V7 TERMINAL")
    pwd = st.text_input("🔐 SECURITY CODE", type="password")

    if st.button("ACTIVATE SYSTEM"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()


# ---------------- TIME ENGINE ULTRA (HARDENED) ----------------

def extract_time(h):
    try:
        t = datetime.strptime(h, "%H:%M:%S")
    except:
        tz = pytz.timezone('Indian/Antananarivo')
        t = datetime.now(tz)

    return t, t.hour, t.minute, t.second


def ultra_time_score(hash_hex, hour, minute, second):
    """
    🔥 ULTRA TIME ENGINE
    Combinaison:
    - hash entropy
    - micro-time
    - cyclic market pressure
    """

    h1 = int(hash_hex[0:12], 16)
    h2 = int(hash_hex[12:24], 16)
    h3 = int(hash_hex[24:36], 16)

    micro = (h1 % 100) + (h2 % 60) + (h3 % 30)

    time_cycle = (hour * 3600 + minute * 60 + second) % 600

    wave = np.sin(time_cycle / 600 * 3.1415 * 2) * 10

    score = (micro * 0.7) + (time_cycle * 0.3) + wave

    return score / 100


# ---------------- MARKET MODE ----------------

def market_mode(last_cote):
    if last_cote < 1.5:
        return "LOW"
    elif last_cote < 2.0:
        return "STABLE"
    elif last_cote <= 2.5:
        return "OPTIMAL"
    elif last_cote <= 3.0:
        return "VOLATILE"
    else:
        return "RISK"


# ---------------- DATASET ----------------

def build_dataset(history):
    data = []

    for h in history:
        try:
            if all(k in h for k in [
                "prob","cote_moy","cote_max","cote_min",
                "confidence","hour","minute","result"
            ]):
                data.append([
                    h["prob"],
                    h["cote_moy"],
                    h["cote_max"],
                    h["cote_min"],
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
        columns=[
            "prob","cmoy","cmax","cmin",
            "conf","hour","minute","label"
        ]
    )


# ---------------- AI TRAIN ----------------

def train_ai():
    df = build_dataset(st.session_state.pred_log)
    if df is None:
        return

    X = df.drop("label", axis=1)
    y = df["label"]

    X_scaled = st.session_state.scaler.fit_transform(X)

    model = RandomForestClassifier(n_estimators=350, random_state=42)
    model.fit(X_scaled, y)

    st.session_state.ml_model = model
    st.session_state.ml_ready = True


def ai_predict(features):
    if not st.session_state.ml_ready:
        return None

    X = np.array(features).reshape(1, -1)

    try:
        X = st.session_state.scaler.transform(X)
        return round(st.session_state.ml_model.predict_proba(X)[0][1] * 100, 1)
    except:
        return None


# ---------------- BACKTEST ----------------

def winrate():
    logs = st.session_state.pred_log
    if len(logs) == 0:
        return 0

    win = sum([1 for x in logs if x["result"] == 1])
    return round((win / len(logs)) * 100, 2)


def hourly_stats():
    stats = {}

    for h in st.session_state.pred_log:
        hour = h.get("hour", 0)

        if hour not in stats:
            stats[hour] = {"win":0, "total":0}

        stats[hour]["total"] += 1
        stats[hour]["win"] += h.get("result",0)

    return stats


def show_heatmap():
    stats = hourly_stats()

    st.subheader("📈 TIME WINRATE HEATMAP")

    if not stats:
        st.info("Mbola tsisy data")
        return

    for h in sorted(stats.keys()):
        total = stats[h]["total"]
        win = stats[h]["win"]

        rate = round((win/total)*100,2) if total > 0 else 0

        st.write(f"🕐 {h}h → {rate}% | {total} trades")


# ---------------- ENGINE ----------------

def run_prediction(hash_str, h_act, last_cote):

    t_obj, hour, minute, second = extract_time(h_act)

    hash_hex = hashlib.sha256(hash_str.encode()).hexdigest()

    np.random.seed(int(hash_hex[:16], 16) % (2**32 - 1))

    # base randomness
    hash_int = int(hash_hex[:10], 16) % 1000
    hash_norm = (hash_int / 100) + 1.1

    # 🔥 ULTRA TIME SCORE (NEW CORE)
    time_score = ultra_time_score(hash_hex, hour, minute, second)

    cycle = (
        0.8 if last_cote < 1.5 else
        1.0 if last_cote < 2.0 else
        1.3 if last_cote <= 2.5 else
        1.1 if last_cote <= 3 else
        0.7
    )

    ref_val = 2.2 + time_score

    base = hash_norm * ref_val * cycle * (1 + time_score)
    sigma = 0.22 + (hash_norm / 15)

    sims = np.random.lognormal(np.log(base), sigma, 15000)

    prob = round(np.sum(sims >= 3.0) / 15000 * 100, 1)

    log_sims = np.log(sims + 1)

    moy_raw = np.exp(np.mean(log_sims))
    max_raw = np.exp(np.percentile(log_sims, 95))
    min_raw = np.exp(np.percentile(log_sims, 10))

    cote_moy = round(moy_raw / 1.30, 2)
    cote_max = round(max_raw / 1.20, 2)
    cote_min = round(min_raw / 1.45, 2)

    confidence = round((prob * cote_moy) / 10, 1)

    # ENTRY TIME BOOSTED
    delay = int(
        (hash_int % 60) +
        (time_score * 50) +
        (minute % 15)
    )

    if delay < 30:
        delay += 30

    h_ent = (t_obj + timedelta(seconds=delay)).strftime("%H:%M:%S")

    # ---------------- X3 ZONE DETECTION ----------------

    x3_zone = (
        prob >= 52 and
        cote_moy >= 2.1 and
        cote_max >= 3.0 and
        confidence >= 10 and
        abs(last_cote - 2.2) <= 0.6
    )

    if x3_zone:
        signal, emoji, result = "🔥 X3+ ZONE", "🚀🔥", 1
    elif prob >= 55:
        signal, emoji, result = "BUY", "🎯", 1
    else:
        signal, emoji, result = "SKIP", "❌", 0

    features = [
        prob,
        cote_moy,
        cote_max,
        cote_min,
        confidence,
        hour,
        minute
    ]

    ai_score = ai_predict(features)

    return {
        "hash": hash_str[:10] + "...",
        "h_act": h_act,
        "h_ent": h_ent,

        "prob": prob,
        "cote_moy": cote_moy,
        "cote_max": cote_max,
        "cote_min": cote_min,

        "confidence": confidence,
        "signal": signal,
        "emoji": emoji,
        "ai_score": ai_score,

        "result": result,
        "hour": hour,
        "minute": minute
    }


# ---------------- UI ----------------

st.title("🚀 ANDR-X AI V7 ⚡ ULTRA TIME ENGINE")

tab1, tab2, tab3 = st.tabs(["📊 ANALYSE", "📜 HISTORIQUE", "📈 STATS"])

with tab1:

    hash_in = st.text_input("🔑 HASH")
    h_in = st.text_input("⏰ HEURE (HH:MM:SS)")
    last_cote = st.number_input("📉 CÔTE PRÉCÉDENTE", value=1.5)

    if st.button("🚀 RUN"):
        if hash_in and h_in:
            res = run_prediction(hash_in, h_in, last_cote)
            st.session_state.pred_log.append(res)
            train_ai()
            st.rerun()

    if st.session_state.pred_log:
        r = st.session_state.pred_log[-1]

        st.markdown(f"""
# {r.get('emoji','')} {r.get('signal','')}

🎯 PROB: {r.get('prob',0)}%  
🧠 CONF: {r.get('confidence',0)}  
🤖 AI: {r.get('ai_score','None')}%  
⏰ ENTRY: {r.get('h_ent','--:--:--')}
""")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(f"📉 MIN\n{r.get('cote_min',0)}x")
        with c2:
            st.markdown(f"📊 MOY\n{r.get('cote_moy',0)}x")
        with c3:
            st.markdown(f"🚀 MAX\n{r.get('cote_max',0)}x")

with tab2:
    st.write(st.session_state.pred_log[::-1])

with tab3:
    st.metric("WINRATE", f"{winrate()} %")
    show_heatmap()


# ---------------- SIDEBAR ----------------

st.sidebar.title("ANDR-X V7 ULTRA")
tz = pytz.timezone('Indian/Antananarivo')
st.sidebar.write(datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S"))
