import streamlit as st  
import numpy as np  
import hashlib  
from datetime import datetime, timedelta  
import pandas as pd  
import pytz  

from sklearn.ensemble import RandomForestClassifier  
from sklearn.preprocessing import StandardScaler  

# ---------------- CONFIG & PREMIUM UI ----------------  
st.set_page_config(page_title="ANDR-X AI V13 ⚡ RL TRUE ENGINE", layout="centered")  

st.markdown("""
<style>
    .stApp {
        background-color: #05050A;
        color: #00ffcc;
        font-family: monospace;
    }
    h1,h2,h3 {text-align:center;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------  
if "pred_log" not in st.session_state:
    st.session_state.pred_log = []

if "auth" not in st.session_state:
    st.session_state.auth = False

if "ml_model" not in st.session_state:
    st.session_state.ml_model = RandomForestClassifier(n_estimators=150)

if "ml_ready" not in st.session_state:
    st.session_state.ml_ready = False

# ---------------- RL MEMORY ----------------  
if "rl_memory" not in st.session_state:
    st.session_state.rl_memory = {
        "win": 0,
        "lose": 0,
        "success_rate": 0.5
    }

# ---------------- LOGIN ----------------  
if not st.session_state.auth:
    st.title("⚡ V13 RL ENGINE LOGIN")
    pwd = st.text_input("PASSWORD", type="password")

    if st.button("ENTER"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("ACCESS DENIED")
    st.stop()

# ---------------- RL UPDATE ----------------  
def update_rl(result):
    if result == "win":
        st.session_state.rl_memory["win"] += 1
    else:
        st.session_state.rl_memory["lose"] += 1

    total = st.session_state.rl_memory["win"] + st.session_state.rl_memory["lose"]
    if total > 0:
        st.session_state.rl_memory["success_rate"] = (
            st.session_state.rl_memory["win"] / total
        )

# ---------------- TRAIN ----------------  
def train_ai():
    data = []
    for h in st.session_state.pred_log:
        if h.get("result") is not None:
            data.append([
                h["prob"], h["moy"], h["max"], h["ref"], h["conf"],
                1 if h["result"] == "win" else 0
            ])

    if len(data) < 5:
        return

    df = pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"])
    X = df.drop("label", axis=1)
    y = df["label"]

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    model = RandomForestClassifier(n_estimators=150)
    model.fit(Xs, y)

    st.session_state.ml_model = model
    st.session_state.scaler = scaler
    st.session_state.ml_ready = True

# ---------------- ENGINE V13 RL ----------------  
def run_prediction(hash_str, h_act, last_cote):

    try:
        t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except:
        t_obj = datetime.now(pytz.timezone("Indian/Antananarivo"))

    h_hex = hashlib.sha256(hash_str.encode()).hexdigest()

    seed = int(h_hex[:12], 16)
    np.random.seed(seed % (2**32))

    base = (int(h_hex[10:16], 16) % 100) / 20 + 1.2

    # ---------------- SIMULATION ----------------  
    sims = np.random.lognormal(
        mean=np.log(base),
        sigma=0.35,
        size=15000
    )

    prob = round(len([x for x in sims if x >= 2.0]) / 15000 * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 95), 2)

    # ---------------- RL ADAPTIVE CONFIDENCE ----------------  
    sr = st.session_state.rl_memory["success_rate"]

    confidence = round((prob * moy) / 10, 1)
    confidence = round(confidence * (0.6 + sr), 1)

    # ---------------- ADAPTIVE ENTRY TIME (V13 RL CORE) ----------------  
    h_int = int(h_hex[:10], 16)

    base_delay = 18 + (h_int % 20)

    rl_factor = int(sr * 20)  # WIN RATE influence

    hash_noise = (int(h_hex[12:18], 16) % 15)
    time_noise = (t_obj.second + t_obj.minute) % 13

    final_delay = base_delay + rl_factor + hash_noise + time_noise

    # anti-fixed window
    if final_delay < 15:
        final_delay += 10
    if final_delay > 80:
        final_delay = 55 + (final_delay % 20)

    entry_time = t_obj + timedelta(seconds=final_delay)

    sniper_time = entry_time + timedelta(seconds=20)

    # ---------------- SIGNAL RL ----------------  
    if confidence > 85 and sr > 0.55:
        signal = "🔥 ULTRA RL SNIPER"
    elif confidence > 65:
        signal = "🟢 STRONG ENTRY"
    elif confidence > 45:
        signal = "🟡 WAIT"
    else:
        signal = "🔴 NO ENTRY"

    return {
        "entry": entry_time.strftime("%H:%M:%S"),
        "sniper": sniper_time.strftime("%H:%M:%S"),
        "prob": prob,
        "moy": moy,
        "max": maxv,
        "conf": confidence,
        "signal": signal,
        "ref": last_cote,
        "result": None
    }

# ---------------- UI ----------------  
st.title("🚀 ANDR-X V13 RL TRUE ENGINE")

h = st.text_input("HASH")
t = st.text_input("TIME (HH:MM:SS)")
c = st.number_input("COTE REF", value=1.5)

if st.button("RUN RL ENGINE"):
    if h and t:
        r = run_prediction(h, t, c)
        st.session_state.pred_log.append(r)
        train_ai()
        st.rerun()

if st.session_state.pred_log:
    r = st.session_state.pred_log[-1]

    st.markdown(f"""
    ### {r['signal']}

    ENTRY: {r['entry']}  
    SNIPER: {r['sniper']}  

    PROB: {r['prob']}%  
    CONF: {r['conf']}  
    REF: {r['ref']}  
    """)

    c1, c2 = st.columns(2)

    if c1.button("WIN"):
        st.session_state.pred_log[-1]["result"] = "win"
        update_rl("win")
        train_ai()
        st.rerun()

    if c2.button("LOSE"):
        st.session_state.pred_log[-1]["result"] = "lose"
        update_rl("lose")
        train_ai()
        st.rerun()

st.sidebar.write("RL SUCCESS RATE:", st.session_state.rl_memory["success_rate"])
