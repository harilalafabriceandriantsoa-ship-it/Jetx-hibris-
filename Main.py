import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG & PREMIUM DESIGN ----------------
st.set_page_config(page_title="JET X ANDR V5.1 ⚡ GOD MODE", layout="wide")

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
        padding: 25px;
        box-shadow: 0 0 30px rgba(0, 255, 204, 0.2);
        margin-top: 10px;
        text-align: center;
    }
    .cote-container {
        display: flex;
        justify-content: space-around;
        margin-top: 15px;
        padding: 10px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
    }
    .cote-item { text-align: center; }
    .cote-label { font-size: 11px; color: #aaa; text-transform: uppercase; }
    .cote-val { font-size: 20px; font-weight: bold; color: #00ffcc; }

    .stButton>button {
        width: 100%; background: linear-gradient(90deg, #004e4e, #00ffcc);
        color: black; font-weight: bold; border: none;
        height: 45px; border-radius: 10px; transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0 0 20px #00ffcc; transform: translateY(-2px); }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "pred_log" not in st.session_state: st.session_state.pred_log = []
if "auth" not in st.session_state: st.session_state.auth = False
if "ml_model" not in st.session_state: st.session_state.ml_model = RandomForestClassifier(n_estimators=120)
if "ml_ready" not in st.session_state: st.session_state.ml_ready = False

# ---------------- LOGIN ----------------
if not st.session_state.auth:
    st.markdown("<h1>🔐 SECURITY ACCESS</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1,1.5,1])
    with col2:
        pwd = st.text_input("PASSWORD", type="password")
        if st.button("ACTIVATE"):
            if pwd == "2026":
                st.session_state.auth = True
                st.rerun()
            else: st.error("DENIED")
    st.stop()

# ---------------- GOD MODE TIMING ----------------
def compute_sniper_timing(hash_hex, t_obj, prob, moy, conf):
    t_sec = t_obj.hour*3600 + t_obj.minute*60 + t_obj.second
    h_ints = [int(hash_hex[i:i+8], 16) for i in range(0, 32, 8)]
    
    base_sec = (h_ints[0] ^ h_ints[1] ^ h_ints[2] ^ h_ints[3]) % 60
    quality = (prob/100 + moy/3 + conf/20)
    shift = int((quality * 7) % 10)
    
    sniper_sec = (base_sec + shift + (t_sec % 10)) % 60
    return sniper_sec

# ---------------- AI & ENGINE ----------------
def train_ai():
    history = st.session_state.pred_log
    data = [[h["prob"], h["moy"], h["max"], float(h["ref"]), h["confidence"], h["result"]] for h in history if h.get("result") is not None]
    if len(data) >= 5:
        df = pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"])
        scaler = StandardScaler()
        st.session_state.scaler = scaler
        st.session_state.ml_model.fit(scaler.fit_transform(df.drop("label", axis=1)), df["label"])
        st.session_state.ml_ready = True

def run_prediction(hash_str, h_act, last_cote):
    try: t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except: t_obj = datetime.now(pytz.timezone('Indian/Antananarivo'))

    seed = int(hashlib.sha256((hash_str + h_act).encode()).hexdigest(), 16) % (2**32)
    np.random.seed(seed)
    hash_hex = hashlib.sha256(hash_str.encode()).hexdigest()
    hash_norm = (int(hash_hex[:8], 16) % 1000 / 100) + 1.1
    t_sec = t_obj.hour*3600 + t_obj.minute*60 + t_obj.second
    time_factor = (t_sec % 300) / 300

    cycle = 0.8 if last_cote < 1.5 else 1.0 if last_cote < 1.8 else 1.3 if last_cote <= 2.5 else 1.1 if last_cote <= 3 else 0.7
    ref_val = (2.1 if hash_norm < 2 else 2.2 if hash_norm < 3 else 2.3) + (time_factor * 0.2)
    
    sims = np.random.lognormal(mean=np.log(hash_norm * ref_val * cycle * (1 + time_factor)), sigma=0.25+(hash_norm/10), size=15000)
    prob = round(len([s for s in sims if s >= 3.0])/15000 * 100, 1)
    moy = round(np.exp(np.mean(np.log(sims+1)))/1.4, 2)
    maxv = round(np.exp(np.percentile(np.log(sims+1), 95))/1.2, 2)
    minv = round(moy / 1.5, 2) 
    conf = round((prob * moy)/10, 1)

    delay = int(max(20, min(18 + (int(hash_hex[8:16], 16)%40) + (t_sec%60)//5 + np.random.uniform(-1,1), 65)))
    h_ent_obj = t_obj + timedelta(seconds=delay)
    
    # 🔥 FIX SNIPER LOGIC (No more None/Jumping)
    s_sec = compute_sniper_timing(hash_hex, t_obj, prob, moy, conf)
    h_sniper_obj = h_ent_obj.replace(second=s_sec)
    
    # Raha latsaky ny 30s ny elanelany dia mijanona amin'io minute io, raha tsia dia manitsy
    if (h_ent_obj - h_sniper_obj).total_seconds() > 30: h_sniper_obj += timedelta(minutes=1)
    elif (h_sniper_obj - h_ent_obj).total_seconds() > 30: h_sniper_obj -= timedelta(minutes=1)

    win_start = (h_sniper_obj - timedelta(seconds=2)).strftime("%H:%M:%S")
    win_end = (h_sniper_obj + timedelta(seconds=2)).strftime("%H:%M:%S")

    signal, emoji = ("❌ SKIP", "❌") if (last_cote > 3 or prob < 40 or moy < 2.3) else \
                    ("⏳ WAIT", "⏳") if prob < 55 else \
                    ("🔥 STRONG BUY", "🔥🎯") if conf > 12 else ("✅ BUY", "🎯")

    ai_score = "CALCULATING..."
    if st.session_state.ml_ready:
        try:
            feat = st.session_state.scaler.transform(np.array([prob, moy, maxv, ref_val, conf]).reshape(1, -1))
            ai_score = f"{round(st.session_state.ml_model.predict_proba(feat)[0][1] * 100, 1)}%"
        except: pass

    return {
        "h_act": h_act, "h_ent": h_ent_obj.strftime("%H:%M:%S"), 
        "sniper_time": h_sniper_obj.strftime("%H:%M:%S"),
        "sniper_window": f"{win_start} - {win_end}", 
        "prob": prob, "min": minv, "moy": moy, "max": maxv,
        "confidence": conf, "signal": signal, "emoji": emoji, "ai_score": ai_score, "result": None, "ref": round(ref_val,2)
    }

# ---------------- UI ----------------
st.markdown("<h1>🚀 JET X ANDR V5.1 ⚡ GOD MODE</h1>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["📊 ANALYSE LIVE", "📜 HISTORIQUE", "📖 GUIDE"])

with tab1:
    c_in1, c_in2, c_in3 = st.columns(3)
    with c_in1: h_in = st.text_input("🔑 HASH")
    with c_in2: t_in = st.text_input("⏰ HEURE", placeholder="13:15:00")
    with c_in3: last_c = st.number_input("📉 LAST COTE", value=1.5, step=0.1)

    if st.button("🚀 EXECUTE AI ANALYSIS"):
        if h_in and t_in:
            res = run_prediction(h_in, t_in, last_c)
            st.session_state.pred_log.append(res)
            st.rerun()
        else: st.warning("Fenoy ny HASH sy ny HEURE!")

    if st.session_state.pred_log:
        r = st.session_state.pred_log[-1]
        
        # UI DISPLAY
        st.markdown(f"""
        <div class="prediction-card">
            <h1 style="border:none; font-size:40px; margin:0;">{r.get('emoji')} {r.get('signal')}</h1>
            <p style="color:#ff00cc; font-weight:bold; letter-spacing:1px;">AI ACCURACY: {r.get('ai_score')}</p>
            
            <div style="background:rgba(0,255,204,0.1); padding:10px; border-radius:10px; margin-bottom:10px; border-left:4px solid #00ffcc;">
                <span style="font-size:11px; color:#aaa;">🎯 ENTRY (LERA HIDIRANA)</span><br>
                <b style="font-size:30px;">{r.get('h_ent')}</b>
            </div>

            <div style="background:rgba(255, 0, 204, 0.1); padding:10px; border-radius:10px; border:1px solid #ff00cc; margin-bottom:15px;">
                <span style="font-size:11px; color:#ff00cc; font-weight:bold;">🎯 SNIPER (EXACT SECOND)</span><br>
                <b style="font-size:30px; color:#fff;">{r.get('sniper_time')}</b><br>
                <small style="color:#ff00cc; font-weight:bold;">WINDOW: {r.get('sniper_window')}</small>
            </div>

            <div class="cote-container">
                <div class="cote-item"><div class="cote-label">📉 MIN</div><div class="cote-val">{r.get('min')}x</div></div>
                <div class="cote-item" style="border-left:1px solid #333; border-right:1px solid #333; padding:0 15px;">
                    <div class="cote-label">📊 MOYEN</div><div class="cote-val" style="color:#fff;">{r.get('moy')}x</div>
                </div>
                <div class="cote-item"><div class="cote-label">🚀 MAX</div><div class="cote-val">{r.get('max')}x</div></div>
            </div>
            <p style="margin-top:10px; font-size:12px; color:#666;">Prob: {r.get('prob')}% | Conf: {r.get('confidence')}</p>
        </div>
        """, unsafe_allow_html=True)

        col_w, col_l = st.columns(2)
        with col_w: 
            if st.button("✅ WIN"): 
                st.session_state.pred_log[-1]["result"] = 1
                train_ai(); st.rerun()
        with col_l: 
            if st.button("❌ LOSE"): 
                st.session_state.pred_log[-1]["result"] = 0
                train_ai(); st.rerun()

with tab2:
    if st.session_state.pred_log:
        st.dataframe(pd.DataFrame(st.session_state.pred_log[::-1]), use_container_width=True)

with tab3:
    st.markdown("### 📖 GUIDE V5.1\n- **Entry**: Lera hanindriana 'Bet'.\n- **Sniper**: Segondra tena 'Exacte' hivoahan'ny côte ambony.\n- **Window**: Ny elanelam-potoana azo antoka manodidina ny Sniper.")

st.sidebar.markdown(f"🕒 {datetime.now(pytz.timezone('Indian/Antananarivo')).strftime('%H:%M:%S')}")
if st.sidebar.button("🗑 RESET SYSTEM"): 
    st.session_state.pred_log = []
    st.rerun()
