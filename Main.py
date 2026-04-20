import streamlit as st
import numpy as np
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time

from sklearn.ensemble import RandomForestClassifier

# ==========================================
# 💎 CONFIG UI
# ==========================================
st.set_page_config(page_title="ANDR-X V14 REAL AI", layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: #020205;
    color: #00ffcc;
    font-family: monospace;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 SESSION INIT
# ==========================================
if "history" not in st.session_state:
    st.session_state.history = []

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "ml_model" not in st.session_state:
    st.session_state.ml_model = RandomForestClassifier(n_estimators=120)

if "ml_ready" not in st.session_state:
    st.session_state.ml_ready = False

# ==========================================
# 🔐 LOGIN SYSTEM (RESTORED)
# ==========================================
if not st.session_state.authenticated:
    st.title("🔐 ANDR-X V14 ACCESS")

    pwd = st.text_input("ENTER PASSWORD", type="password")

    if st.button("LOGIN"):
        if pwd == "2026":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Wrong password")

    st.stop()

# ==========================================
# 🧠 TIME
# ==========================================
def get_now():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

# ==========================================
# 🧠 AI TRAINING
# ==========================================
def train_ai():
    data = []

    for h in st.session_state.history:
        if "result" in h:
            label = 1 if h["result"] == "win" else 0
            data.append([
                h["prob"],
                h["conf"],
                h["moy"],
                h["spread"],
                label
            ])

    if len(data) < 6:
        return

    df = pd.DataFrame(data, columns=["prob","conf","moy","spread","label"])

    X = df[["prob","conf","moy","spread"]]
    y = df["label"]

    model = RandomForestClassifier(n_estimators=150, max_depth=6)
    model.fit(X, y)

    st.session_state.ml_model = model
    st.session_state.ml_ready = True

def ai_predict(prob, conf, moy, spread):
    if not st.session_state.ml_ready:
        return None

    try:
        X = np.array([[prob, conf, moy, spread]])
        return round(st.session_state.ml_model.predict_proba(X)[0][1] * 100, 1)
    except:
        return None

# ==========================================
# 🧠 ENTRY TIME
# ==========================================
def calc_entry(hash_val, spread, t_in, strength):
    now = get_now()

    try:
        t_obj = datetime.strptime(t_in.strip(), "%H:%M:%S").time()
        base_time = datetime.combine(now.date(), t_obj)
    except:
        base_time = now

    hash_shift = (int(hash_val[:6], 16) % 12) - 4

    if strength > 80:
        base_delay = 12
    elif strength > 60:
        base_delay = 18
    else:
        base_delay = 25

    final = int(base_delay + (spread * 1.2) + hash_shift)
    final = max(10, min(90, final))

    entry = base_time + timedelta(seconds=final)
    return entry.strftime("%H:%M:%S")

# ==========================================
# 🧠 CORE ENGINE
# ==========================================
def run_ai(hash_in, time_in, cote):

    h_num = int(hashlib.sha256(hash_in.encode()).hexdigest()[:16], 16)
    h_norm = (h_num % 1000) / 1000
    np.random.seed(h_num & 0xffffffff)

    variance = 0.25 + (h_norm * 0.2)

    sims = np.random.lognormal(
        np.mean([np.log(cote + 0.05), 0.25]),
        variance,
        12000
    )

    prob = np.mean(sims >= 3.0) * 100
    moy = np.exp(np.mean(np.log(sims)))
    max_v = np.percentile(sims, 98)
    min_v = np.percentile(sims, 5)

    spread = max_v - min_v

    conf = (prob * 0.7) + ((moy / cote) * 30)
    conf = max(20, min(99, conf))

    ai_score = ai_predict(prob, conf, moy, spread)

    if ai_score:
        strength = (prob * 0.5) + (ai_score * 0.5)
    else:
        strength = prob

    entry = calc_entry(hash_in, spread, time_in, strength)

    if strength > 80 and moy > 2.2:
        signal = "💎 ULTRA BUY"
    elif strength > 65:
        signal = "🟢 STRONG BUY"
    elif strength > 50:
        signal = "⚡ SCALP"
    else:
        signal = "❌ SKIP"

    res = {
        "entry": entry,
        "signal": signal,
        "prob": round(prob,1),
        "conf": round(conf,1),
        "moy": round(moy,2),
        "max": round(max_v,2),
        "min": round(min_v,2),
        "spread": round(spread,2),
        "ai_score": ai_score
    }

    st.session_state.history.append(res)

    if len(st.session_state.history) > 30:
        st.session_state.history.pop(0)

    train_ai()

    return res

# ==========================================
# 🖥 UI MAIN
# ==========================================
st.title("🚀 ANDR-X V14 REAL AI")

col1, col2 = st.columns([1,2])

with col1:
    hash_in = st.text_input("HASH")
    time_in = st.text_input("TIME (HH:MM:SS)")
    cote = st.number_input("COTE", value=2.2)

    if st.button("RUN AI"):
        if hash_in and time_in:
            with st.spinner("Processing..."):
                time.sleep(0.5)
                st.session_state.last = run_ai(hash_in, time_in, cote)
        else:
            st.error("Fill all fields")

    if st.button("🗑 RESET DATA"):
        st.session_state.history = []
        if "last" in st.session_state:
            del st.session_state.last
        st.rerun()

with col2:
    if "last" in st.session_state:
        r = st.session_state.last

        st.markdown(f"""
        ## {r['signal']}

        🎯 Prob: {r['prob']}%  
        🧠 Confidence: {r['conf']}%  
        🤖 AI Score: {r['ai_score']}  

        ⏰ Entry: {r['entry']}
        """)

        st.write(r)

# ==========================================
# 🧠 FEEDBACK
# ==========================================
st.markdown("### 🧠 AI LEARNING")

if "last" in st.session_state:
    c1, c2 = st.columns(2)

    if c1.button("✅ WIN"):
        st.session_state.history[-1]["result"] = "win"
        train_ai()

    if c2.button("❌ LOSS"):
        st.session_state.history[-1]["result"] = "loss"
        train_ai()

# ==========================================
# 📜 HISTORY (RESTORED)
# ==========================================
st.markdown("### 📜 HISTORY")

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df[::-1])
else:
    st.info("No history yet")

# ==========================================
# ⏰ SIDEBAR TIME
# ==========================================
st.sidebar.markdown("### ⏰ TIME")
st.sidebar.write(get_now().strftime("%d/%m/%Y %H:%M:%S"))
