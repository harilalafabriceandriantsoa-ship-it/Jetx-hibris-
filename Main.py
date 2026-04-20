import streamlit as st 
import numpy as np
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import pytz

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# ==========================================
# 💎 UI
# ==========================================
st.set_page_config(page_title="JETX ANDR V14 ULTRA FIXED", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #020205; color: #e0fbfc; font-family: 'Rajdhani', sans-serif; }
    .main-title {
        font-family: 'Orbitron', sans-serif; font-size: 3.2rem; font-weight: 700;
        text-align: center; background: linear-gradient(90deg, #00ffcc, #ff00cc, #00ccff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .glass-card {
        background: rgba(10, 10, 25, 0.75); border: 1px solid rgba(0, 255, 204, 0.4);
        border-radius: 20px; padding: 28px; backdrop-filter: blur(20px); margin-bottom: 25px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #00ffcc 0%, #0088ff 50%, #ff00cc 100%) !important;
        color: #000 !important; font-weight: 700 !important; border-radius: 15px !important;
        height: 60px !important; width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# Session State
if "history" not in st.session_state:
    st.session_state.history = []

if "ml_clf" not in st.session_state:
    st.session_state.ml_clf = RandomForestClassifier(n_estimators=250, max_depth=9, random_state=42)
if "ml_reg" not in st.session_state:
    st.session_state.ml_reg = RandomForestRegressor(n_estimators=180, max_depth=8, random_state=42)
if "ml_ready" not in st.session_state:
    st.session_state.ml_ready = False
if "scaler" not in st.session_state:
    st.session_state.scaler = StandardScaler()

def get_time():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

# ==========================================
# 🔥 STREAK (inchangé)
# ==========================================
def get_current_streak(history):
    marked = [h.get("real_result") for h in history if h.get("real_result") in ["win", "loss"]]
    if not marked:
        return 0, 0, None
    streak_win = streak_loss = 0
    last = marked[-1]
    for res in reversed(marked):
        if res == last:
            if res == "win": streak_win += 1
            else: streak_loss += 1
        else:
            break
    return streak_win, streak_loss, last

# ==========================================
# 🧠 AI TRAINING + STREAK + VOLATILITY
# ==========================================
def prepare_ml_data(history):
    data = []
    for i in range(len(history)):
        h = history[i]
        prev = history[:i]
        win_s, loss_s, _ = get_current_streak(prev)
        
        # Volatility simple (écart-type des derniers moy)
        vols = [p.get("moy", 2.5) for p in prev[-10:]]
        volatility = round(np.std(vols) if len(vols) > 3 else 1.0, 2)

        features = [
            h.get("x3_prob", 50), h.get("conf", 50), h.get("moy", 2.5),
            h.get("spread", 3.0), h.get("last_cote_used", 2.0),
            h.get("strength", 50), win_s, loss_s, volatility
        ]
        label = 1 if h.get("real_result") == "win" else (1 if h.get("strength", 0) > 65 else 0)
        data.append(features + [label])
    return data

def train_ai_ultra():
    data = prepare_ml_data(st.session_state.history)
    if len(data) < 10:
        return
    df = pd.DataFrame(data)
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    X_scaled = st.session_state.scaler.fit_transform(X)
    st.session_state.ml_clf.fit(X_scaled, y)
    st.session_state.ml_reg.fit(X_scaled, X.iloc[:, 0])
    st.session_state.ml_ready = True

def ai_predict_ultra(features):
    if not st.session_state.ml_ready:
        return None
    try:
        X = np.array(features).reshape(1, -1)
        X_scaled = st.session_state.scaler.transform(X)
        prob_win = st.session_state.ml_clf.predict_proba(X_scaled)[0][1] * 100
        refined = st.session_state.ml_reg.predict(X_scaled)[0]
        return round(0.65 * prob_win + 0.35 * refined, 1)
    except:
        return None

# ==========================================
# ⏰ ENTRY TIME ENGINE - FIXED & HASH DEPENDANT (Tena Matanjaka)
# ==========================================
def entry_calc_fixed(hash_val, spread, t_in, strength, x3_prob):
    now = get_time()
    try:
        t_obj = datetime.strptime(t_in.strip(), "%H:%M:%S").time()
        base_time = datetime.combine(now.date(), t_obj)
    except:
        base_time = now

    # === PLUS ARKARAKA NY HASH ===
    # On prend plus de bytes du hash pour plus de variation
    h_int = int(hash_val[:12], 16)          # 12 premiers caractères hex = très sensible
    hash_shift = (h_int % 23) - 11          # shift entre -11 et +11 secondes

    # Delay base plus variable selon hash + probabilité X3
    base_delay = 14 + (h_int % 9)           # entre 14 et 22 secondes de base
    prob_factor = 8 if x3_prob > 70 else (4 if x3_prob > 50 else 0)

    final_seconds = int(base_delay + (spread * 0.45) + hash_shift + prob_factor)
    final_seconds = max(18, min(52, final_seconds))   # plage réaliste et variable

    base_time = base_time.replace(microsecond=0)
    entry_time = base_time + timedelta(seconds=final_seconds)
    return entry_time.strftime("%H:%M:%S")

# ==========================================
# 🚀 ENGINE CORE - ALGORITHM PLUS MATANJAKA
# ==========================================
def run_engine_ultra(h_in, t_in, c_ref, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:20], 16)

    np.random.seed(h_num & 0xffffffff)

    # Ajustement last_cote
    last_cote = min(last_cote, 7.0)
    if last_cote > 4.8:
        last_cote = (last_cote + 3.0) / 2

    # Base + simulation plus réaliste pour JetX (beaucoup de <2x + queue longue)
    base = 1.18 + (h_num % 950) / 105
    sigma = 0.34 - (last_cote * 0.008)   # variance légèrement réduite si last cote élevé

    sims = np.random.lognormal(np.log(base), sigma, 22000)

    prob_x3 = round(np.mean(sims >= 3.0) * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 95.5), 2)
    minv = round(np.percentile(sims, 4.5), 2)
    spread = round(maxv - minv, 2)

    conf = round(max(28, min(97, prob_x3 * 0.62 + moy * 17 + last_cote * 7)), 1)

    # Streak + Volatility
    win_s, loss_s, _ = get_current_streak(st.session_state.history)
    vols = [h.get("moy", 2.5) for h in st.session_state.history[-12:]]
    volatility = round(np.std(vols) if len(vols) > 4 else 1.2, 2)

    ai_score = ai_predict_ultra([prob_x3, conf, moy, spread, last_cote, conf, win_s, loss_s, volatility])

    # Strength ultra
    base_strength = prob_x3 * 0.53 + (ai_score or conf) * 0.42
    streak_adj = win_s * 2.1 - loss_s * 2.4
    strength = round(base_strength + streak_adj + (volatility * 1.8), 1)
    strength = max(22, min(96, strength))

    # Entry Time FIXÉ & HASH DEPENDANT
    entry = entry_calc_fixed(h_hex, spread, t_in, strength, prob_x3)

    # Signaux ciblés X3+
    if strength > 82:
        signal = "💎💎💎 ULTRA X3+ BUY"
    elif strength > 71:
        signal = "🔥 STRONG X3 TARGET"
    elif strength > 56:
        signal = "🟢 GOOD X3 SCALP"
    elif strength > 43:
        signal = "⚡ LIGHT ENTRY"
    else:
        signal = "⚠️ SKIP - Low X3 Chance"

    res = {
        "entry": entry,
        "signal": signal,
        "x3_prob": prob_x3,
        "conf": conf,
        "moy": moy,
        "max": maxv,
        "min": minv,
        "spread": spread,
        "last_cote_used": round(last_cote, 2),
        "ai_score": ai_score,
        "strength": strength,
        "win_streak": win_s,
        "loss_streak": loss_s,
        "volatility": volatility,
        "real_result": None
    }

    st.session_state.history.append(res)
    if len(st.session_state.history) > 35:
        st.session_state.history.pop(0)

    train_ai_ultra()
    return res

# ==========================================
# UI
# ==========================================
st.markdown("<h1 class='main-title'>JETX ANDR V14 ULTRA - ENTRY FIXED</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2.2])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    h_in = st.text_input("HASH (provably fair)", placeholder="Colle le hash complet...")
    t_in = st.text_input("TIME (HH:MM:SS)", placeholder="Ex: 21:15:30")
    last_cote = st.number_input("LAST COTE", value=2.3, step=0.1)

    if st.button("🚀 RUN ULTRA ENGINE"):
        if h_in and len(t_in) >= 8:
            with st.spinner("Calcul hash + entry time en cours..."):
                st.session_state.last = run_engine_ultra(h_in, t_in, 2.5, last_cote)
                st.success("Signal prêt !")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.sidebar.button("🔄 RESET ALL"):
        st.session_state.history = []
        if "last" in st.session_state: del st.session_state.last
        st.rerun()

with col2:
    if "last" in st.session_state:
        r = st.session_state.last
        streak_text = f"Win: {r['win_streak']} | Loss: {r['loss_streak']} | Vol: {r.get('volatility', 1.2):.1f}"
        st.markdown(f"""
        <div class="glass-card">
            <h2 style="color:#00ffcc;">{r['signal']}</h2>
            <h3>X3 PROB: <span style="color:#ff00cc;">{r['x3_prob']}%</span> | CONF: {r['conf']}</h3>
            <h1 style="font-size:3.6rem; color:#00ffcc;">{r['entry']}</h1>
            <p>MIN: {r['min']} | MOY: {r['moy']} | MAX: {r['max']}</p>
            <small>Strength: {r['strength']} | AI: {r.get('ai_score','N/A')}</small><br>
            <small style="color:#ffff00;">{streak_text}</small>
        </div>
        """, unsafe_allow_html=True)

# History + Editor
st.markdown("### 📜 HISTORY - Marque WIN/LOSS")
if st.session_state.history:
    df_hist = pd.DataFrame(st.session_state.history)[::-1]
    edited = st.data_editor(df_hist, use_container_width=True,
        column_config={"real_result": st.column_config.SelectboxColumn("Résultat Réel", options=["win","loss",None])})

    if st.button("💾 Sauvegarder & Réentraîner AI"):
        for idx, row in edited.iterrows():
            orig_idx = len(st.session_state.history) - 1 - idx
            st.session_state.history[orig_idx]["real_result"] = row["real_result"]
        train_ai_ultra()
        st.success("AI mise à jour avec streak + vrais résultats !")
        st.rerun()

st.caption("JETX ANDR V14 ULTRA - Entry time fixé & 100% dépendant du hash | Algorithm renforcé pour X3+")
