import streamlit as st
import numpy as np
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time

from sklearn.ensemble import RandomForestClassifier

# ==========================================
# 💎 PREMIUM UI & STYLING
# ==========================================
st.set_page_config(page_title="ANDR-X V14 REAL AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp {
        background-color: #020205;
        color: #e0fbfc;
        font-family: 'Rajdhani', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 SESSION INIT
# ==========================================

if "history" not in st.session_state:
    st.session_state.history = []

if "ml_model" not in st.session_state:
    st.session_state.ml_model = RandomForestClassifier(n_estimators=120)

if "ml_ready" not in st.session_state:
    st.session_state.ml_ready = False


# ==========================================
# 🧠 TIME
# ==========================================

def get_tz_now():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))


# ==========================================
# 🧠 REAL ML TRAINING (NEW)
# ==========================================

def train_real_ai():
    data = []

    for h in st.session_state.history:
        if "result" in h:
            label = 1 if h["result"] == "win" else 0
            data.append([
                h["x3_prob"],
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
# 🧠 ENTRY TIME (SYNC WITH SIGNAL)
# ==========================================

def hyper_time_calc(hash_val, spread, t_in, strength):
    now = get_tz_now()

    try:
        t_obj = datetime.strptime(t_in.strip(), "%H:%M:%S").time()
        base_time = datetime.combine(now.date(), t_obj)
    except:
        base_time = now

    hash_shift = (int(hash_val[:6], 16) % 12) - 4

    # 🔥 sync with strength
    if strength > 80:
        base_delay = 12
    elif strength > 60:
        base_delay = 18
    else:
        base_delay = 25

    final_seconds = int(base_delay + (spread * 1.2) + hash_shift)
    final_seconds = max(10, min(90, final_seconds))

    entry = base_time + timedelta(seconds=final_seconds)
    return entry.strftime("%H:%M:%S")


# ==========================================
# 🧠 CORE ENGINE (UPGRADED)
# ==========================================

def run_ultra_analysis(h_in, t_in, c_ref):

    h_num = int(hashlib.sha256(h_in.encode()).hexdigest()[:16], 16)
    h_norm = (h_num % 1000) / 1000
    np.random.seed(h_num & 0xffffffff)

    variance_scale = 0.25 + (h_norm * 0.2)

    sims = np.random.lognormal(
        np.mean([np.log(c_ref + 0.05), 0.25]),
        variance_scale,
        12000
    )

    prob_x3_real = np.mean(sims >= 3.0) * 100
    moy = np.exp(np.mean(np.log(sims)))
    max_v = np.percentile(sims, 98)
    min_v = np.percentile(sims, 5)

    spread = max_v - min_v

    # 🔥 REAL confidence (no fake boost)
    conf = (prob_x3_real * 0.7) + ((moy / c_ref) * 30)
    conf = max(20, min(99, conf))

    # 🔥 AI prediction
    ai_score = ai_predict(prob_x3_real, conf, moy, spread)

    if ai_score is not None:
        final_strength = (prob_x3_real * 0.5) + (ai_score * 0.5)
    else:
        final_strength = prob_x3_real

    final_strength = round(final_strength, 1)

    # 🔥 ENTRY TIME SYNC
    entry_time = hyper_time_calc(h_in, spread, t_in, final_strength)

    # 🔥 SIGNAL (CLEAN + REAL)
    if final_strength > 80 and moy > 2.2:
        signal, color = "💎 ULTRA AI BUY", "#ff00cc"
    elif final_strength > 65:
        signal, color = "🟢 AI STRONG BUY", "#00ffcc"
    elif final_strength > 50:
        signal, color = "⚡ AI SCALP", "#ffff00"
    else:
        signal, color = "⚠️ AI SKIP", "#ff4444"

    res = {
        "entry": entry_time,
        "signal": signal,
        "color": color,
        "x3_prob": round(prob_x3_real, 1),
        "conf": round(conf, 1),
        "spread": round(spread, 2),
        "moy": round(moy, 2),
        "max": round(max_v, 2),
        "min": round(min_v, 2),
        "ai_score": ai_score
    }

    st.session_state.history.append(res)

    if len(st.session_state.history) > 20:
        st.session_state.history.pop(0)

    train_real_ai()

    return res


# ==========================================
# 🖥️ UI
# ==========================================

st.title("🚀 ANDR-X V14 REAL AI")

h_in = st.text_input("HASH")
t_in = st.text_input("TIME (HH:MM:SS)")
c_ref = st.number_input("COTE", value=2.0)

if st.button("RUN AI"):
    if h_in and t_in:
        with st.spinner("AI Thinking..."):
            time.sleep(0.5)
            st.session_state.last_res = run_ultra_analysis(h_in, t_in, c_ref)

if "last_res" in st.session_state:
    r = st.session_state.last_res

    st.markdown(f"""
    ## {r['signal']}

    🎯 Prob: {r['x3_prob']}%  
    🧠 Confidence: {r['conf']}%  
    🤖 AI Score: {r['ai_score']}  

    ⏰ Entry: {r['entry']}
    """)

    st.write(r)

# ==========================================
# 🧠 FEEDBACK (NEW)
# ==========================================

st.markdown("### 🧠 AI LEARNING FEEDBACK")

if "last_res" in st.session_state:
    col1, col2 = st.columns(2)

    if col1.button("✅ WIN"):
        st.session_state.history[-1]["result"] = "win"
        train_real_ai()

    if col2.button("❌ LOSS"):
        st.session_state.history[-1]["result"] = "loss"
        train_real_ai()

# ==========================================
# 📊 HISTORY
# ==========================================

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df)
