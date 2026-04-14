import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG ----------------
st.set_page_config(page_title="ANDR-X AI V3 FIXED", layout="centered")

st.markdown("""
<style>
.stApp {background:#000; color:#00ffcc;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "log" not in st.session_state:
    st.session_state.log = []

if "auth" not in st.session_state:
    st.session_state.auth = False

if "model" not in st.session_state:
    st.session_state.model = RandomForestClassifier(n_estimators=120)

if "ready" not in st.session_state:
    st.session_state.ready = False

# ---------------- LOGIN ----------------
if not st.session_state.auth:
    st.title("⚡ ANDR-X SYSTEM")
    pwd = st.text_input("SECURITY", type="password")

    if st.button("ENTER"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# ---------------- AI TRAIN ----------------
def build_data(log):
    data = []

    for x in log:
        if "ai" in x:
            continue

        data.append([
            x["prob"],
            x["moy"],
            x["max"],
            x["ref"],
            x["conf"],
            1 if "BUY" in x["signal"] else 0
        ])

    if len(data) < 5:
        return None

    return pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"])


def train():
    df = build_data(st.session_state.log)
    if df is None:
        return

    X = df.drop("label", axis=1)
    y = df["label"]

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    model = RandomForestClassifier(n_estimators=150)
    model.fit(Xs, y)

    st.session_state.model = model
    st.session_state.scaler = scaler
    st.session_state.ready = True


def ai_score(features):
    if not st.session_state.ready:
        return None

    X = np.array(features).reshape(1, -1)
    X = st.session_state.scaler.transform(X)

    return round(st.session_state.model.predict_proba(X)[0][1] * 100, 1)

# ---------------- ENGINE ----------------
def predict(hash_str, time_str, last_cote):

    try:
        t = datetime.strptime(time_str, "%H:%M:%S")
    except:
        t = datetime.now()

    # seed dynamique (NO FIXED)
    seed = int(hashlib.sha256((hash_str + time_str).encode()).hexdigest(), 16) % (2**32)
    np.random.seed(seed)

    # hash feature
    h = hashlib.sha256(hash_str.encode()).hexdigest()
    hnum = int(h[:8], 16) % 1000
    hash_norm = (hnum / 100) + 1.0

    # time factor
    sec = t.hour*3600 + t.minute*60 + t.second
    tf = (sec % 300) / 300

    # cycle
    if last_cote < 1.5:
        cycle = 0.85
    elif last_cote < 1.8:
        cycle = 1.0
    elif last_cote <= 2.5:
        cycle = 1.25
    elif last_cote <= 3:
        cycle = 1.1
    else:
        cycle = 0.75

    # reference dynamic (NO FIXED RANGE)
    ref = 2.0 + (hash_norm * 0.15) + (tf * 0.25)

    base = hash_norm * ref * cycle * (1 + tf)

    sigma = 0.2 + (hash_norm / 12)

    # ---------------- SIMULATION ----------------
    sims = np.random.lognormal(
        mean=np.log(base),
        sigma=sigma,
        size=15000
    )

    prob = round(np.mean(sims >= 3.0) * 100, 1)

    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 95), 2)

    conf = round((prob * moy) / 10, 1)

    # ---------------- ENTRY TIME ----------------
    delay = int(40 + (hash_norm * 12) + (tf * 25) + (cycle * 10))
    entry = (t + timedelta(seconds=delay)).strftime("%H:%M:%S")

    # ---------------- SIGNAL ----------------
    if prob < 40:
        signal = "❌ SKIP"
    elif prob < 55:
        signal = "⏳ WAIT"
    elif conf > 12:
        signal = "🔥 STRONG BUY"
    else:
        signal = "✅ BUY"

    features = [prob, moy, maxv, ref, conf]
    ai = ai_score(features)

    return {
        "hash": hash_str[:10]+"...",
        "prob": prob,
        "moy": moy,
        "max": maxv,
        "ref": round(ref,2),
        "conf": conf,
        "signal": signal,
        "entry": entry,
        "ai": ai
    }

# ---------------- UI ----------------
st.title("🚀 ANDR-X AI V3 (NO FIXED VALUES)")

tab1, tab2, tab3 = st.tabs(["📊 ANALYSE", "📜 HISTORIQUE", "📖 GUIDE"])

# ---------------- TAB 1 ----------------
with tab1:

    h = st.text_input("HASH")
    t = st.text_input("HEURE", value=datetime.now().strftime("%H:%M:%S"))
    c = st.number_input("CÔTE PRÉCÉDENTE", value=1.5)

    if st.button("RUN"):
        if h:
            r = predict(h, t, c)
            st.session_state.log.append(r)
            train()
            st.rerun()

    if st.session_state.log:
        r = st.session_state.log[-1]

        st.markdown(f"""
### 🔥 {r['signal']}
PROB X3+: **{r['prob']}%**  
CONF: **{r['conf']}**  
AI: **{r['ai']}**  
⏱ ENTRY: **{r['entry']}**
""")

        st.write("📊 MIN / MOY / MAX")
        st.write("MIN: 2.00x (base)")
        st.write(f"MOY: {r['moy']}x")
        st.write(f"MAX: {r['max']}x")

# ---------------- TAB 2 ----------------
with tab2:
    st.write(st.session_state.log)

# ---------------- TAB 3 ----------------
with tab3:
    st.markdown("""
# 📖 GUIDE

## 🎯 CÔTE RÉFÉRENCE
- BEST: 1.80 → 2.50
- OK: 1.50 → 1.80
- BAD: <1.50 or >3

## ⏱ ENTRY
- dynamique (hash + heure + cycle)
- window 5–10 sec

## ⚠️ SIGNAL
- SKIP = aza miditra
- WAIT = miandrasa
- BUY = azo idirana
- STRONG BUY = tsara indrindra
""")

# ---------------- SIDEBAR ----------------
st.sidebar.write("VERSION V3 FIXED REMOVED")
st.sidebar.write(datetime.now().strftime("%d/%m/%Y"))
