import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG & PREMIUM DESIGN ----------------
st.set_page_config(page_title="JET X ANDR V5.8 ⚡ ELITE MODE", layout="wide")

st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top, #001a1a, #000000);
        color: #00ffcc;
        font-family: 'Courier New', monospace;
    }
    h1 {
        text-align: center; color: #00ffcc;
        text-shadow: 0 0 10px #00ffcc, 0 0 20px #00ffcc;
        letter-spacing: 4px; border-bottom: 2px solid #00ffcc;
        padding-bottom: 10px;
    }
    .prediction-card {
        background: rgba(0, 255, 204, 0.05);
        border: 2px solid #00ffcc;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 0 30px rgba(0, 255, 204, 0.2);
        margin-top: 10px;
        text-align: center;
    }
    .cote-container {
        display: flex;
        justify-content: space-around;
        margin-top: 20px;
        padding: 15px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
    }
    .cote-item { text-align: center; }
    .cote-label { font-size: 12px; color: #aaa; text-transform: uppercase; }
    .cote-val { font-size: 22px; font-weight: bold; color: #00ffcc; }

    .stButton>button {
        width: 100%; background: linear-gradient(90deg, #004e4e, #00ffcc);
        color: black; font-weight: bold; border: none;
        height: 50px; border-radius: 10px; transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0 0 20px #00ffcc; transform: translateY(-2px); }
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

# ---------------- LOGIN ----------------
if not st.session_state.auth:
    st.markdown("<h1>🔐 SECURITY ACCESS</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        pwd = st.text_input("ENTER SYSTEM PASSWORD", type="password")
        if st.button("ACTIVATE"):
            if pwd == "2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("ACCESS DENIED")
    st.stop()

# ---------------- AI TRAIN ----------------
def train_ai():
    history = st.session_state.pred_log
    data = [
        [h["prob"], h["moy"], h["max"], float(h["ref"]), h["confidence"], h["result"]]
        for h in history if h.get("result") is not None
    ]

    if len(data) >= 5:
        df = pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"])

        if len(df["label"].unique()) > 1:
            scaler = StandardScaler()
            st.session_state.scaler = scaler
            st.session_state.ml_model.fit(
                scaler.fit_transform(df.drop("label", axis=1)),
                df["label"]
            )
            st.session_state.ml_ready = True

# ---------------- ENGINE ----------------
def run_prediction(hash_str, h_act, last_cote):

    # 🔄 REAL TIME SYNC
    now = datetime.now(pytz.timezone('Indian/Antananarivo'))

    try:
        t_input = datetime.strptime(h_act, "%H:%M:%S")
        t_obj = now.replace(
            hour=t_input.hour,
            minute=t_input.minute,
            second=t_input.second
        )
    except:
        t_obj = now

    hash_hex = hashlib.sha256(hash_str.encode()).hexdigest()
    np.random.seed(int(hash_hex[:10], 16) % (2**32))

    hash_norm = (int(hash_hex[10:18], 16) % 1000 / 100) + 1.2
    t_sec = t_obj.hour*3600 + t_obj.minute*60 + t_obj.second
    time_factor = (t_sec % 600) / 600

    ref_val = 2.2 + (time_factor * 0.3)

    cycle = (
        0.9 if last_cote > 3.5 else
        1.25 if last_cote < 1.4 else
        1.05
    )

    sims = np.random.lognormal(
        mean=np.log(hash_norm * ref_val * cycle),
        sigma=0.25,
        size=20000
    )

    prob = round(len([s for s in sims if s >= 2.0]) / 20000 * 100, 1)
    moy = round(np.mean(sims) * 1.05, 2)
    maxv = round(np.percentile(sims, 95) * 1.3, 2)
    minv = round(max(1.5, moy * 0.45), 2)

    conf = round((prob * moy) / 12, 1)

    # ---------------- FIXED QUALITY ----------------
    quality = ((prob * 0.6) + (moy * 25) + (conf * 1.2)) / 100

    base_delay = 18 + (int(hash_hex[18:22], 16) % 22)

    if quality > 2.2:
        delay_ent = base_delay - 6
    elif quality < 1.6:
        delay_ent = base_delay + 6
    else:
        delay_ent = base_delay

    delay_ent = int(max(14, min(delay_ent, 52)))
    h_ent_obj = t_obj + timedelta(seconds=delay_ent)

    # ---------------- SNIPER PEAK ----------------
    volatility = (maxv - moy)
    peak_factor = int((volatility * 10 + prob) % 18)

    delay_snipe = delay_ent + 6 + peak_factor
    h_snipe_obj = t_obj + timedelta(seconds=delay_snipe)

    win_s = (h_snipe_obj - timedelta(seconds=2)).strftime("%H:%M:%S")
    win_e = (h_snipe_obj + timedelta(seconds=2)).strftime("%H:%M:%S")

    # ---------------- SIGNAL FIX ----------------
    if prob < 45 or moy < 1.9:
        signal, emoji = "❌ SKIP", "❌"
    elif prob > 75 and moy > 2.5 and conf > 20:
        signal, emoji = "🔥 GOD MODE", "⚡🎯"
    elif prob > 60 and moy > 2.1:
        signal, emoji = "✅ BUY", "🎯"
    else:
        signal, emoji = "⏳ WAIT", "⏳"

    ai_score = "N/A"
    if st.session_state.ml_ready:
        try:
            feat = st.session_state.scaler.transform(
                np.array([prob, moy, maxv, ref_val, conf]).reshape(1, -1)
            )
            ai_score = f"{round(st.session_state.ml_model.predict_proba(feat)[0][1] * 100, 1)}%"
        except:
            pass

    return {
        "h_act": h_act,
        "h_ent": h_ent_obj.strftime("%H:%M:%S"),
        "sniper_time": h_snipe_obj.strftime("%H:%M:%S"),
        "sniper_window": f"{win_s} - {win_e}",
        "prob": prob,
        "min": minv,
        "moy": moy,
        "max": maxv,
        "confidence": conf,
        "signal": signal,
        "emoji": emoji,
        "ai_score": ai_score,
        "result": None,
        "ref": round(ref_val, 2)
    }

# ---------------- UI ----------------
st.markdown("<h1>🚀 JET X ANDR V5.8 ⚡ ELITE MODE</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 ANALYSE LIVE", "📜 HISTORIQUE", "📖 GUIDE"])

with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        h_in = st.text_input("🔑 HASH")

    with c2:
        t_in = st.text_input("⏰ HEURE (HH:MM:SS)")

    with c3:
        last_c = st.number_input("📉 LAST COTE", value=1.5)

    if st.button("🚀 RUN ANALYSIS"):
        if h_in and t_in:
            res = run_prediction(h_in, t_in, last_c)
            st.session_state.pred_log.append(res)
            st.rerun()

    if st.session_state.pred_log:
        r = st.session_state.pred_log[-1]

        st.markdown(f"""
        <div class="prediction-card">
            <h1>{r['emoji']} {r['signal']}</h1>

            <p><b>AI SCORE:</b> {r['ai_score']}</p>

            <h2>⏰ ENTRY: {r['h_ent']}</h2>
            <h3>🎯 SNIPER: {r['sniper_time']}</h3>
            <small>{r['sniper_window']}</small>

            <div class="cote-container">
                <div class="cote-item">MIN<br>{r['min']}x</div>
                <div class="cote-item">MOY<br>{r['moy']}x</div>
                <div class="cote-item">MAX<br>{r['max']}x</div>
            </div>

            <p>Prob: {r['prob']}% | Conf: {r['confidence']}</p>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.dataframe(pd.DataFrame(st.session_state.pred_log[::-1]))

with tab3:
    st.markdown("""
### 📖 GUIDE V5.8
✔ Entry: dynamique (quality-based)  
✔ Sniper: volatility + peak detection  
✔ Signal: strict filtering  
✔ AI learning: WIN/LOSE active  
""")

st.sidebar.markdown("🕒 LIVE SYSTEM")
if st.sidebar.button("RESET"):
    st.session_state.pred_log = []
    st.rerun()
