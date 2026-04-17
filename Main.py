import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG ----------------

st.set_page_config(page_title="ANDR-X AI V9 ⚡ ULTRA X3", layout="centered")

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
    st.session_state.ml_model = RandomForestClassifier(n_estimators=300)

if "scaler" not in st.session_state:
    st.session_state.scaler = StandardScaler()

if "ml_ready" not in st.session_state:
    st.session_state.ml_ready = False


# ---------------- LOGIN ----------------

if not st.session_state.auth:
    st.title("⚡ ANDR-X AI V9 TERMINAL")
    pwd = st.text_input("🔐 CODE", type="password")

    if st.button("ACTIVATE"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()


# ---------------- TIME ----------------

def extract_time(h):
    try:
        t = datetime.strptime(h, "%H:%M:%S")
    except:
        tz = pytz.timezone('Indian/Antananarivo')
        t = datetime.now(tz)

    return t, t.hour, t.minute, t.second


# ---------------- TIME ENGINE ----------------

def time_engine(hash_hex, hour, minute, second):

    a = int(hash_hex[0:10], 16)
    b = int(hash_hex[10:20], 16)
    c = int(hash_hex[20:30], 16)

    micro = (a % 90) + (b % 70) + (c % 50)

    cycle = np.sin((hour * 60 + minute) / 1440 * 6.28) * 15

    noise = (second % 30) * 1.5

    return (micro + cycle + noise) / 100


# ---------------- AI SAFE ----------------

def ai_predict(features):
    if not st.session_state.ml_ready:
        return None

    try:
        X = np.array(features).reshape(1, -1)
        X = st.session_state.scaler.transform(X)
        return round(st.session_state.ml_model.predict_proba(X)[0][1] * 100, 1)
    except:
        return None


# ---------------- ULTRA X3 DETECTOR ----------------

def detect_x3(prob, moy, maxv, minv, confidence, last_cote, time_score):

    cond_prob = prob >= 55
    cond_moy = moy >= 2.2
    cond_max = maxv >= 3.2
    cond_conf = confidence >= 12

    spread = maxv - minv
    cond_stable = spread >= 1.2 and spread <= 4.5

    cond_market = 1.6 <= last_cote <= 2.6

    cond_time = time_score >= 0.25

    cond_realistic = prob <= 92

    score = sum([
        cond_prob,
        cond_moy,
        cond_max,
        cond_conf,
        cond_stable,
        cond_market,
        cond_time,
        cond_realistic
    ])

    if score >= 7:
        return "🔥 X3 STRONG", "🚀🔥", 1
    elif score >= 5:
        return "⚡ X3 POSSIBLE", "⚡", 0
    else:
        return None, None, None


# ---------------- ENGINE ----------------

def run_prediction(hash_str, h_act, last_cote):

    t_obj, hour, minute, second = extract_time(h_act)

    hash_hex = hashlib.sha256(hash_str.encode()).hexdigest()

    np.random.seed(int(hash_hex[:12], 16) % (2**32 - 1))

    hash_norm = (int(hash_hex[:8], 16) % 1000) / 100 + 1.1

    time_score = time_engine(hash_hex, hour, minute, second)

    cycle = (
        0.85 if last_cote < 1.5 else
        1.05 if last_cote < 2.0 else
        1.25 if last_cote <= 2.5 else
        1.1 if last_cote <= 3 else
        0.8
    )

    ref = 2.15 + time_score

    base = hash_norm * ref * cycle

    sims = np.random.lognormal(np.log(base), 0.25, 12000)

    prob = round(np.mean(sims >= 3.0) * 100, 1)
    prob = min(prob, 95)

    log_sims = np.log(sims + 1)

    moy = round(np.exp(np.mean(log_sims)) / 1.3, 2)
    maxv = round(np.exp(np.percentile(log_sims, 95)) / 1.2, 2)
    minv = round(np.exp(np.percentile(log_sims, 10)) / 1.4, 2)

    confidence = round((prob * moy) / 10, 1)
    confidence = min(confidence, 100)

    # ENTRY TIME

    delay = int(
        (hash_norm * 40) +
        (time_score * 80) +
        (minute % 20)
    )

    if delay < 20:
        delay += 20

    h_ent = (t_obj + timedelta(seconds=delay)).strftime("%H:%M:%S")

    # ---------------- SIGNAL VIA X3 DETECTOR ----------------

    signal, emoji, result = detect_x3(
        prob,
        moy,
        maxv,
        minv,
        confidence,
        last_cote,
        time_score
    )

    if signal is None:
        if prob >= 55:
            signal, emoji, result = "BUY", "🎯", 1
        elif prob >= 40:
            signal, emoji, result = "POSSIBLE", "⏳", 0
        else:
            signal, emoji, result = "SKIP", "❌", 0

    return {
        "hash": hash_str[:10] + "...",
        "h_ent": h_ent,

        "prob": prob,
        "moy": moy,
        "max": maxv,
        "min": minv,

        "confidence": confidence,
        "signal": signal,
        "emoji": emoji,

        "ai_score": None,

        "result": result,
        "hour": hour,
        "minute": minute
    }


# ---------------- UI ----------------

st.title("🚀 ANDR-X AI V9 ⚡ ULTRA X3 ENGINE")

tab1, tab2, tab3 = st.tabs(["📊 ANALYSE", "📜 HISTORIQUE", "📈 STATS"])

with tab1:

    hash_in = st.text_input("🔑 HASH")
    h_in = st.text_input("⏰ HEURE")
    last_cote = st.number_input("📉 CÔTE", value=1.5)

    if st.button("RUN"):
        if hash_in:
            res = run_prediction(hash_in, h_in, last_cote)
            st.session_state.pred_log.append(res)
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
            st.markdown(f"📉 MIN\n{r.get('min',0)}x")
        with c2:
            st.markdown(f"📊 MOY\n{r.get('moy',0)}x")
        with c3:
            st.markdown(f"🚀 MAX\n{r.get('max',0)}x")

with tab2:
    st.write(st.session_state.pred_log[::-1])

with tab3:
    if len(st.session_state.pred_log) > 0:
        win = sum([1 for x in st.session_state.pred_log if x["result"] == 1])
        st.metric("WINRATE", f"{round(win/len(st.session_state.pred_log)*100,2)} %")

# RESET

if st.sidebar.button("🧹 RESET DATA"):
    st.session_state.pred_log = []
    st.rerun()

# CLOCK

tz = pytz.timezone('Indian/Antananarivo')
st.sidebar.write(datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S"))
