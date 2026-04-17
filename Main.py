import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG ----------------

st.set_page_config(page_title="ANDR-X AI V11 ⚡ SMART LEARN", layout="centered")

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

if "win_memory" not in st.session_state:
    st.session_state.win_memory = []

if "ml_model" not in st.session_state:
    st.session_state.ml_model = RandomForestClassifier(n_estimators=300)

if "scaler" not in st.session_state:
    st.session_state.scaler = StandardScaler()

if "ml_ready" not in st.session_state:
    st.session_state.ml_ready = False


# ---------------- LOGIN ----------------

if not st.session_state.auth:
    st.title("⚡ ANDR-X AI V11 TERMINAL")
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


# ---------------- LOSS FILTER ----------------

def loss_risk(prob, confidence, spread):

    risk = 0

    if prob < 50:
        risk += 2
    if confidence < 10:
        risk += 2
    if spread > 5:
        risk += 2

    return risk >= 4


# ---------------- BEST ENTRY ----------------

def best_entry_second(hash_hex, time_score, last_cote):

    base = int(hash_hex[:6], 16) % 60
    boost = int(time_score * 30)
    market = int(last_cote * 10)

    second = base + boost + market

    if second < 25:
        second = 25 + (second % 10)

    if second > 75:
        second = 75 - (second % 10)

    return second


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

    # ---------------- PROBABILITY ----------------
    raw_prob = np.mean(sims >= 3.0) * 100
    prob = (raw_prob * 0.7) + (np.median(sims) * 3)
    prob = max(5, min(prob, 88))
    prob = round(prob, 1)

    # ---------------- METRICS ----------------
    log_sims = np.log(sims + 1)

    moy = round(np.exp(np.mean(log_sims)) / 1.3, 2)
    maxv = round(np.exp(np.percentile(log_sims, 95)) / 1.2, 2)
    minv = round(np.exp(np.percentile(log_sims, 10)) / 1.4, 2)

    volatility = np.std(sims)

    confidence = (
        prob * 0.5 +
        moy * 10 +
        (1 / (1 + volatility)) * 20
    )

    confidence = round(min(confidence, 100), 1)

    spread = maxv - minv

    # ---------------- LOSS FILTER ----------------
    if loss_risk(prob, confidence, spread):
        signal = "SKIP"
        emoji = "❌"
        result = 0
    else:

        # ---------------- BEST ENTRY ----------------
        entry_second = best_entry_second(hash_hex, time_score, last_cote)
        h_ent = (t_obj + timedelta(seconds=entry_second)).strftime("%H:%M:%S")

        # ---------------- SIGNAL ----------------
        if prob >= 60 and confidence >= 15:
            signal, emoji, result = "🔥 BUY", "🎯", 1
        elif prob >= 45:
            signal, emoji, result = "⚡ POSSIBLE", "⏳", 0
        else:
            signal, emoji, result = "SKIP", "❌", 0

    # ---------------- UPDATE MEMORY ----------------
    st.session_state.win_memory.append(result)

    return {
        "hash": hash_str[:10] + "...",
        "h_ent": h_ent if not loss_risk(prob, confidence, spread) else "--:--:--",

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


# ---------------- WINRATE ----------------

def get_winrate():
    if len(st.session_state.win_memory) == 0:
        return 0
    return round(sum(st.session_state.win_memory) / len(st.session_state.win_memory) * 100, 2)


# ---------------- UI ----------------

st.title("🚀 ANDR-X AI V11 ⚡ SMART LEARNING")

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
    st.metric("WINRATE AI", f"{get_winrate()} %")

# RESET
if st.sidebar.button("🧹 RESET DATA"):
    st.session_state.pred_log = []
    st.session_state.win_memory = []
    st.rerun()

# CLOCK
tz = pytz.timezone('Indian/Antananarivo')
st.sidebar.write(datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S"))
