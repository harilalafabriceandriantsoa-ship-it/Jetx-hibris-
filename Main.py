import streamlit as st
import numpy as np
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import pytz

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------- CONFIG ----------------
st.set_page_config(page_title="ANDR-X AI V3 ⚡ TERMINAL", layout="centered")

st.markdown("""
<style>
.stApp {background:#000; color:#00ffcc; font-family: monospace;}
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

# 🧠 RL MEMORY (AMPY VAOVAO)
if "rl_score" not in st.session_state:
    st.session_state.rl_score = {
        "win": 0,
        "lose": 0
    }

# ---------------- V4 ULTRA SYNC ----------------
def ultra_sync_delay(t_obj, raw_delay):
    server_tick = 6
    t_seconds = t_obj.hour*3600 + t_obj.minute*60 + t_obj.second
    phase = t_seconds % server_tick

    aligned = raw_delay - phase

    if phase >= 4:
        aligned -= 1
    elif phase <= 1:
        aligned += 1

    if aligned < 12:
        aligned += server_tick * 2

    return aligned

# ---------------- DOUBLE ENTRY ----------------
def compute_entry_window(t_obj, final_delay):
    base_time = t_obj + timedelta(seconds=final_delay)
    early = base_time - timedelta(seconds=2)
    late = base_time + timedelta(seconds=2)

    return {
        "entry_main": base_time.strftime("%H:%M:%S"),
        "entry_early": early.strftime("%H:%M:%S"),
        "entry_late": late.strftime("%H:%M:%S")
    }

# ---------------- LOGIN ----------------
if not st.session_state.auth:
    st.title("⚡ ANDR-X AI V3 TERMINAL")
    pwd = st.text_input("🔐 SECURITY CODE", type="password")

    if st.button("ACTIVATE SYSTEM"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# ---------------- AI TRAIN ----------------
def build_dataset(history):
    data = []
    for h in history:
        if all(k in h for k in ["prob", "moy", "max", "ref", "confidence", "result"]):
            if h["result"] is not None:
                data.append([
                    h["prob"],
                    h["moy"],
                    h["max"],
                    float(h["ref"]),
                    h["confidence"],
                    1 if h["result"] == "win" else 0
                ])

    if len(data) < 5:
        return None

    return pd.DataFrame(data, columns=["prob","moy","max","ref","conf","label"])

def train_ai():
    df = build_dataset(st.session_state.pred_log)
    if df is None:
        return

    try:
        X = df.drop("label", axis=1)
        y = df["label"]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = RandomForestClassifier(n_estimators=150)
        model.fit(X_scaled, y)

        st.session_state.ml_model = model
        st.session_state.scaler = scaler
        st.session_state.ml_ready = True
    except:
        pass

def ai_predict(features):
    if not st.session_state.ml_ready or "scaler" not in st.session_state:
        return None

    try:
        X = np.array(features).reshape(1, -1)
        X = st.session_state.scaler.transform(X)
        return round(st.session_state.ml_model.predict_proba(X)[0][1] * 100, 1)
    except:
        return None

# ---------------- RL UPDATE ----------------
def update_rl(result):
    if result == "win":
        st.session_state.rl_score["win"] += 1
    elif result == "lose":
        st.session_state.rl_score["lose"] += 1

# ---------------- ENGINE ----------------
def run_prediction(hash_str, h_act, last_cote):

    try:
        t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except:
        tz_mg = pytz.timezone('Indian/Antananarivo')
        t_obj = datetime.now(tz_mg)

    seed_global = int(hashlib.sha256((hash_str + h_act).encode()).hexdigest(), 16) % (2**32)
    np.random.seed(seed_global)

    hash_hex = hashlib.sha256(hash_str.encode()).hexdigest()
    hash_int = int(hash_hex[:8], 16) % 1000
    hash_norm = (hash_int / 100) + 1.1

    t_seconds = t_obj.hour*3600 + t_obj.minute*60 + t_obj.second
    time_factor = (t_seconds % 300) / 300

    if last_cote < 1.5:
        cycle = 0.8
    elif last_cote < 1.8:
        cycle = 1.0
    elif last_cote <= 2.5:
        cycle = 1.3
    elif last_cote <= 3:
        cycle = 1.1
    else:
        cycle = 0.7

    ref_val = 2.1 if hash_norm < 2 else 2.2 if hash_norm < 3 else 2.3
    ref_val += time_factor * 0.2

    base = hash_norm * ref_val * cycle * (1 + time_factor)
    sigma = 0.25 + (hash_norm / 10)

    sims = np.random.lognormal(mean=np.log(base), sigma=sigma, size=15000)
    success = [s for s in sims if s >= 3.0]
    prob = round(len(success)/15000 * 100, 1)

    log_sims = np.log(sims + 1)
    moy_raw = np.exp(np.mean(log_sims))
    max_raw = np.exp(np.percentile(log_sims, 95))

    moy = round(moy_raw / 1.4, 2)
    maxv = round(max_raw / 1.2, 2)
    confidence = round((prob * moy)/10, 1)

    # RL influence
    total = st.session_state.rl_score["win"] + st.session_state.rl_score["lose"]
    if total > 0:
        winrate = st.session_state.rl_score["win"] / total
        confidence = round(confidence * (0.8 + winrate), 1)

    # --- HEURE V4 ULTRA SYNC ---
    hash_time = int(hash_hex[8:16], 16)
    hash_time2 = int(hash_hex[16:24], 16)
    hash_time3 = int(hash_hex[24:32], 16)

    layer1 = hash_time % 18
    layer2 = hash_time2 % 10
    layer3 = hash_time3 % 6

    if last_cote < 1.5:
        dynamic_boost = 8
    elif last_cote < 2.5:
        dynamic_boost = 5
    else:
        dynamic_boost = 2

    micro = int((hash_norm % 1) * 6)

    raw_delay = 18 + layer1 + layer2 + layer3 + dynamic_boost + micro

    final_delay = ultra_sync_delay(t_obj, raw_delay)

    # DOUBLE ENTRY
    entry_window = compute_entry_window(t_obj, final_delay)

    h_ent = entry_window["entry_main"]
    h_early = entry_window["entry_early"]
    h_late = entry_window["entry_late"]

    if last_cote > 3:
        signal, emoji = "❌ SKIP", "❌"
    elif prob < 40 or moy < 2.3:
        signal, emoji = "❌ SKIP", "❌"
    elif prob < 55:
        signal, emoji = "⏳ WAIT", "⏳"
    elif confidence > 12:
        signal, emoji = "🔥 STRONG BUY", "🔥🎯"
    else:
        signal, emoji = "✅ BUY", "🎯"

    features = [prob, moy, maxv, ref_val, confidence]
    ai_score = ai_predict(features)

    return {
        "h_act": h_act,
        "h_ent": h_ent,
        "h_early": h_early,
        "h_late": h_late,
        "hash": hash_str[:10]+"...",
        "ref": round(ref_val,2),
        "prob": prob,
        "moy": moy,
        "max": maxv,
        "confidence": confidence,
        "signal": signal,
        "emoji": emoji,
        "ai_score": ai_score,
        "result": None
    }

# ---------------- UI ----------------
st.title("🚀 ANDR-X AI V3 ⚡ TERMINAL")

tab1, tab2 = st.tabs(["📊 ANALYSE", "📜 HISTORIQUE"])

with tab1:
    hash_in = st.text_input("🔑 HASH")
    h_in = st.text_input("⏰ HEURE (HH:MM:SS)")
    last_cote = st.number_input("📉 CÔTE PRÉCÉDENTE", value=1.5)

    if st.button("🚀 RUN ANALYSIS"):
        if hash_in and h_in:
            res = run_prediction(hash_in, h_in, last_cote)
            st.session_state.pred_log.append(res)
            train_ai()
            st.rerun()

    if st.session_state.pred_log:
        r = st.session_state.pred_log[-1]

        st.markdown(f"""
        # {r.get('emoji')} SIGNAL: {r.get('signal')}

        🎯 PROB: {r.get('prob')}%
        🧠 CONF: {r.get('confidence')}
        🤖 AI: {r.get('ai_score')}

        ⏰ MAIN: {r.get('h_ent')}
        🟢 EARLY: {r.get('h_early')}
        🔵 LATE: {r.get('h_late')}
        """)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ WIN"):
                st.session_state.pred_log[-1]["result"] = "win"
                update_rl("win")
                train_ai()
                st.rerun()

        with col2:
            if st.button("❌ LOSE"):
                st.session_state.pred_log[-1]["result"] = "lose"
                update_rl("lose")
                train_ai()
                st.rerun()

with tab2:
    st.write(st.session_state.pred_log[::-1])
