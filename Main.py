import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG & PREMIUM DESIGN ----------------
st.set_page_config(page_title="JET X ANDR V4.1 ⚡ TERMINAL", layout="wide")

st.markdown("""
<style>
    /* Background Cyberpunk */
    .stApp {
        background: radial-gradient(circle at top, #001a1a, #000000);
        color: #00ffcc;
        font-family: 'Courier New', monospace;
    }
    
    /* Titre Principal */
    h1 {
        text-align: center; color: #00ffcc;
        text-shadow: 0 0 10px #00ffcc, 0 0 20px #00ffcc;
        letter-spacing: 4px; border-bottom: 2px solid #00ffcc;
        padding-bottom: 10px;
    }

    /* Boite de Prediction Stylé */
    .prediction-card {
        background: rgba(0, 255, 204, 0.05);
        border: 2px solid #00ffcc;
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 0 30px rgba(0, 255, 204, 0.2);
        margin-top: 20px;
        text-align: center;
    }

    /* Bokotra / Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #004e4e, #00ffcc);
        color: black;
        font-weight: bold;
        border: none;
        height: 55px;
        border-radius: 12px;
        transition: 0.3s;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        box-shadow: 0 0 30px #00ffcc;
        transform: scale(1.02);
    }

    /* Tabs Style */
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] {
        background: #0a0a0a;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 10px 30px;
        color: #ccc;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        border-color: #00ffcc;
        color: #00ffcc;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "pred_log" not in st.session_state:
    st.session_state.pred_log = []

if "auth" not in st.session_state:
    st.session_state.auth = False

if "ml_model" not in st.session_state:
    st.session_state.ml_model = RandomForestClassifier(n_estimators=120)

if "ml_ready" not in st.session_state:
    st.session_state.ml_ready = False

# ---------------- LOGIN ----------------
if not st.session_state.auth:
    st.markdown("<h1>🔐 JET X SECURITY ACCESS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        pwd = st.text_input("ENTER SYSTEM PASSWORD", type="password")
        if st.button("ACTIVATE TERMINAL"):
            if pwd == "2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("ACCESS DENIED")
    st.stop()

# ---------------- AI ENGINE ----------------
def build_dataset(history):
    data = []
    for h in history:
        if all(k in h for k in ["prob","moy","max","ref","confidence","result"]) and h["result"] is not None:
            data.append([h["prob"], h["moy"], h["max"], float(h["ref"]), h["confidence"], h["result"]])
    return pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"]) if len(data) >= 5 else None

def train_ai():
    df = build_dataset(st.session_state.pred_log)
    if df is not None:
        try:
            X, y = df.drop("label", axis=1), df["label"]
            scaler = StandardScaler()
            st.session_state.scaler = scaler
            st.session_state.ml_model.fit(scaler.fit_transform(X), y)
            st.session_state.ml_ready = True
        except: pass

def ai_predict(features):
    if not st.session_state.ml_ready: return "N/A"
    try:
        X = st.session_state.scaler.transform(np.array(features).reshape(1, -1))
        return f"{round(st.session_state.ml_model.predict_proba(X)[0][1] * 100, 1)}%"
    except: return "WAIT..."

# ---------------- LOGIC ----------------
def run_prediction(hash_str, h_act, last_cote):
    try: t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except: t_obj = datetime.now(pytz.timezone('Indian/Antananarivo'))

    seed = int(hashlib.sha256((hash_str + h_act).encode()).hexdigest(), 16) % (2**32)
    np.random.seed(seed)
    
    hash_hex = hashlib.sha256(hash_str.encode()).hexdigest()
    hash_norm = (int(hash_hex[:8], 16) % 1000 / 100) + 1.1
    t_seconds = t_obj.hour*3600 + t_obj.minute*60 + t_obj.second
    time_factor = (t_seconds % 300) / 300

    cycle = 0.8 if last_cote < 1.5 else 1.0 if last_cote < 1.8 else 1.3 if last_cote <= 2.5 else 1.1 if last_cote <= 3 else 0.7
    ref_val = (2.1 if hash_norm < 2 else 2.2 if hash_norm < 3 else 2.3) + (time_factor * 0.2)

    sims = np.random.lognormal(mean=np.log(hash_norm * ref_val * cycle * (1 + time_factor)), sigma=0.25+(hash_norm/10), size=15000)
    prob = round(len([s for s in sims if s >= 3.0])/15000 * 100, 1)
    moy, maxv = round(np.exp(np.mean(np.log(sims+1)))/1.4, 2), round(np.exp(np.percentile(np.log(sims+1), 95))/1.2, 2)
    conf = round((prob * moy)/10, 1)

    # Entry Time (Anti-Fixe)
    delay = int(max(20, min(18 + (int(hash_hex[8:16], 16)%40) + (t_seconds%60)//5 + np.random.uniform(-2,2), 65)))
    h_ent = (t_obj + timedelta(seconds=delay)).strftime("%H:%M:%S")

    signal, emoji = ("❌ SKIP", "❌") if (last_cote > 3 or prob < 40 or moy < 2.3) else \
                    ("⏳ WAIT", "⏳") if prob < 55 else \
                    ("🔥 STRONG BUY", "🔥🎯") if conf > 12 else ("✅ BUY", "🎯")

    return {"h_act": h_act, "h_ent": h_ent, "hash": hash_str[:10], "ref": round(ref_val,2), "prob": prob, 
            "moy": moy, "max": maxv, "confidence": conf, "signal": signal, "emoji": emoji, "ai_score": ai_predict([prob, moy, maxv, ref_val, conf]), "result": None}

# ---------------- UI ----------------
st.markdown("<h1>🚀 JET X ANDR V4.1 ⚡ TERMINAL</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 ANALYSE LIVE", "📜 HISTORIQUE", "📖 GUIDE"])

with tab1:
    c_in1, c_in2, c_in3 = st.columns(3)
    with c_in1: h_in = st.text_input("🔑 CURRENT HASH")
    with c_in2: t_in = st.text_input("⏰ HEURE (HH:MM:SS)", placeholder="13:15:00")
    with c_in3: last_c = st.number_input("📉 CÔTE PRÉCÉDENTE", value=1.5, step=0.1)

    if st.button("🚀 EXECUTE AI ANALYSIS"):
        if h_in and t_in:
            res = run_prediction(h_in, t_in, last_c)
            st.session_state.pred_log.append(res)
            st.rerun()
        else: st.warning("Fenoy ny HASH sy ny HEURE!")

    if st.session_state.pred_log:
        r = st.session_state.pred_log[-1]
        st.markdown(f"""
        <div class="prediction-card">
            <h1 style="border:none; font-size:45px; margin:0;">{r['emoji']} {r['signal']}</h1>
            <p style="font-size:20px; color:#ff00cc;">AI SCORE: {r['ai_score']}</p>
            <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px; margin:20px 0; border:1px dashed #00ffcc;">
                <span style="font-size:18px;">🎯 ENTRY TIME</span><br>
                <b style="font-size:40px; color:#00ffcc;">{r['h_ent']}</b>
            </div>
            <div style="display:flex; justify-content:space-around; font-weight:bold;">
                <div>PROB: {r['prob']}%</div>
                <div>CONF: {r['confidence']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_res1, col_res2 = st.columns(2)
        with col_res1:
            if st.button("✅ WIN"):
                st.session_state.pred_log[-1]["result"] = 1
                train_ai()
                st.rerun()
        with col_res2:
            if st.button("❌ LOSE"):
                st.session_state.pred_log[-1]["result"] = 0
                train_ai()
                st.rerun()

with tab2:
    if st.session_state.pred_log:
        st.dataframe(pd.DataFrame(st.session_state.pred_log[::-1])[['h_act', 'h_ent', 'signal', 'prob', 'result']], use_container_width=True)

with tab3:
    st.markdown("""
# 📖 JET X ANDR V4.1 GUIDE

✔️ BEST COTE: 1.8 – 2.5  
✔️ ENTRY: 20s – 65s (ANTI-FIXE)  
✔️ AI LEARNS from WIN/LOSE  
✔️ Use STRONG / BUY only  
""")

st.sidebar.markdown(f"**SERVER: ONLINE**\n\n🕒 {datetime.now(pytz.timezone('Indian/Antananarivo')).strftime('%H:%M:%S')}")
if st.sidebar.button("🗑️ RESET SYSTEM"):
    st.session_state.pred_log = []
    st.rerun()
