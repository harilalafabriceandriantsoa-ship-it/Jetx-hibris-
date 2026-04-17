import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG ----------------
st.set_page_config(page_title="ANDR-X AI ULTRA ENTRY", layout="centered")

st.markdown("""
<style>
.stApp {
    background:#050505;
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

# ---------------- LOGIN ----------------
if not st.session_state.auth:
    st.title("🔐 LOGIN")
    pwd = st.text_input("PASSWORD", type="password")
    if st.button("ENTER"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# ---------------- AI TRAIN (SAFE) ----------------
def train_ai():
    data = []
    for h in st.session_state.pred_log:
        if h.get("result") is not None:
            data.append([
                h.get("prob",0),
                h.get("moy",0),
                h.get("max",0),
                h.get("ref",0),
                h.get("conf",0),
                1 if h.get("result")=="win" else 0
            ])

    if len(data) < 5:
        return

    df = pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"])
    X = df.drop("label", axis=1)
    y = df["label"]

    scaler = StandardScaler()
    model = RandomForestClassifier(n_estimators=150)

    model.fit(scaler.fit_transform(X), y)

    st.session_state.model = model
    st.session_state.scaler = scaler
    st.session_state.ready = True

# ---------------- ENGINE (ULTRA ENTRY FIXED) ----------------
def run_prediction(hash_str, h_act, last_cote):

    tz = pytz.timezone("Indian/Antananarivo")

    try:
        t = datetime.strptime(h_act, "%H:%M:%S")
    except:
        t = datetime.now(tz)

    h = hashlib.sha256(hash_str.encode()).hexdigest()

    seed = int(h[:12], 16)
    np.random.seed(seed % (2**32))

    base = (int(h[10:16], 16) % 100) / 25 + 1.2

    sims = np.random.lognormal(mean=np.log(base), sigma=0.30, size=12000)

    prob = round(len([x for x in sims if x >= 2.0]) / 12000 * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 95), 2)

    conf = round((prob * moy) / 10, 1)

    # ---------------- ULTRA ENTRY SYSTEM ----------------
    hash_time = int(h[8:16], 16)

    base_delay = (
        (hash_time % 40) +
        (int(last_cote * 3) % 10) +
        (int(base * 6) % 8)
    )

    # 🔥 VARIABLE (anti fixe)
    jitter = np.random.randint(-6, 7)

    delay = base_delay + jitter
    delay = max(10, min(80, delay))

    entry_center = t + timedelta(seconds=delay)

    # ⏰ ULTRA WINDOW (IMPORTANT FIX)
    entry_start = entry_center - timedelta(seconds=5)
    entry_end = entry_center + timedelta(seconds=6)

    # SIGNAL
    if conf > 80 and moy > 2.4:
        signal = "🔥 ULTRA ENTRY"
    elif conf > 60:
        signal = "🟢 STRONG ENTRY"
    elif conf > 40:
        signal = "🟡 WAIT"
    else:
        signal = "🔴 NO ENTRY"

    return {
        "h_ent": entry_center.strftime("%H:%M:%S"),
        "h_window": f"{entry_start.strftime('%H:%M:%S')} → {entry_end.strftime('%H:%M:%S')}",
        "prob": prob,
        "moy": moy,
        "max": maxv,
        "conf": conf,
        "signal": signal,
        "ref": last_cote,
        "result": None
    }

# ---------------- UI ----------------
st.title("🚀 ANDR-X ULTRA ENTRY SYSTEM")

h = st.text_input("HASH")
t = st.text_input("HEURE (HH:MM:SS)")
c = st.number_input("COTE REF", value=1.5)

if st.button("RUN"):
    if h and t:
        r = run_prediction(h,t,c)
        st.session_state.pred_log.append(r)
        train_ai()
        st.rerun()

if st.session_state.pred_log:
    r = st.session_state.pred_log[-1]

    st.markdown(f"""
    ### {r['signal']}
    ENTRY: **{r['h_ent']}**  
    WINDOW: **{r.get('h_window','N/A')}**

    PROB: {r['prob']}%  
    CONF: {r['conf']}  
    MOY: {r['moy']}x  
    """)
