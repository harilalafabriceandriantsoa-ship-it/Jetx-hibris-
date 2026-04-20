import streamlit as st
import numpy as np
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import pytz

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# ==========================================
# 🔐 PASSWORD PROTECTION (Amélioré - caché mieux)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #0a0a1f, #1a0033); }
        .login-title {
            font-size: 4.5rem; font-weight: 900; text-align: center;
            background: linear-gradient(90deg, #00ffcc, #ff00ff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='login-title'>JETX ANDR</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#00ffcc; margin-bottom:30px;'>V14 ULTRA STYLÉ</h2>", unsafe_allow_html=True)

    password = st.text_input("🔑 Entrez le mot de passe pour accéder :", 
                             type="password", 
                             placeholder="Entrez JET2026 ici")
    
    if st.button("✅ Valider l'accès"):
        if password == "JET2026":
            st.session_state.authenticated = True
            st.success("✅ Accès autorisé !")
            st.rerun()
        else:
            st.error("❌ Mot de passe incorrect. Essayez à nouveau.")
    st.stop()

# ==========================================
# 💎 INTERFACE ULTRA STYLÉE
# ==========================================
st.set_page_config(page_title="JETX ANDR V14 ULTRA", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');

    .stApp {
        background: linear-gradient(135deg, #0a0a1f 0%, #1a0033 100%);
        color: #e0fbfc;
    }

    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 4rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(0, 255, 204, 0.5);
    }

    .glass-card {
        background: rgba(15, 15, 40, 0.8);
        border: 1px solid rgba(0, 255, 204, 0.6);
        border-radius: 25px;
        padding: 30px;
        backdrop-filter: blur(20px);
        box-shadow: 0 10px 40px rgba(0, 255, 204, 0.2);
    }

    .signal-ultra { color: #00ffcc; text-shadow: 0 0 25px #00ffcc; }
    .signal-strong { color: #ff00ff; text-shadow: 0 0 20px #ff00ff; }
    .signal-good  { color: #00ccff; }
    .signal-light { color: #ffff00; }
    .signal-skip  { color: #ff3366; }

    .stButton>button {
        background: linear-gradient(135deg, #00ff88, #ff00ff, #00ccff) !important;
        color: #000 !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.3rem !important;
        border-radius: 50px !important;
        height: 70px !important;
        box-shadow: 0 0 35px rgba(0, 255, 204, 0.8);
        transition: all 0.3s;
    }

    .stButton>button:hover {
        transform: scale(1.08);
        box-shadow: 0 0 50px rgba(255, 0, 255, 0.9);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE & FONCTIONS
# ==========================================
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

def prepare_ml_data(history):
    data = []
    for i in range(len(history)):
        h = history[i]
        prev = history[:i]
        win_s, loss_s, _ = get_current_streak(prev)
        vols = [p.get("moy", 2.5) for p in prev[-10:]]
        volatility = round(np.std(vols) if len(vols) > 3 else 1.0, 2)
        features = [h.get("x3_prob", 50), h.get("conf", 50), h.get("moy", 2.5),
                    h.get("spread", 3.0), h.get("last_cote_used", 2.0),
                    h.get("strength", 50), win_s, loss_s, volatility]
        label = 1 if h.get("real_result") == "win" else (1 if h.get("strength", 0) > 65 else 0)
        data.append(features + [label])
    return data

def train_ai_ultra():
    data = prepare_ml_data(st.session_state.history)
    if len(data) < 10: return
    df = pd.DataFrame(data)
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    X_scaled = st.session_state.scaler.fit_transform(X)
    st.session_state.ml_clf.fit(X_scaled, y)
    st.session_state.ml_reg.fit(X_scaled, X.iloc[:, 0])
    st.session_state.ml_ready = True

def ai_predict_ultra(features):
    if not st.session_state.ml_ready: return None
    try:
        X = np.array(features).reshape(1, -1)
        X_scaled = st.session_state.scaler.transform(X)
        prob_win = st.session_state.ml_clf.predict_proba(X_scaled)[0][1] * 100
        refined = st.session_state.ml_reg.predict(X_scaled)[0]
        return round(0.65 * prob_win + 0.35 * refined, 1)
    except:
        return None

def entry_calc_fixed(hash_val, spread, t_in, strength, x3_prob):
    now = get_time()
    try:
        t_obj = datetime.strptime(t_in.strip(), "%H:%M:%S").time()
        base_time = datetime.combine(now.date(), t_obj)
    except:
        base_time = now

    h_int = int(hash_val[:12], 16)
    hash_shift = (h_int % 23) - 11
    base_delay = 14 + (h_int % 9)
    prob_factor = 8 if x3_prob > 70 else (4 if x3_prob > 50 else 0)

    final_seconds = int(base_delay + (spread * 0.45) + hash_shift + prob_factor)
    final_seconds = max(18, min(52, final_seconds))

    base_time = base_time.replace(microsecond=0)
    return (base_time + timedelta(seconds=final_seconds)).strftime("%H:%M:%S")

def run_engine_ultra(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:20], 16)
    np.random.seed(h_num & 0xffffffff)

    last_cote = min(last_cote, 7.0)
    if last_cote > 4.8:
        last_cote = (last_cote + 3.0) / 2

    base = 1.18 + (h_num % 950) / 105
    sigma = 0.34 - (last_cote * 0.008)
    sims = np.random.lognormal(np.log(base), sigma, 22000)

    prob_x3 = round(np.mean(sims >= 3.0) * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 95.5), 2)
    minv = round(np.percentile(sims, 4.5), 2)
    spread = round(maxv - minv, 2)

    conf = round(max(28, min(97, prob_x3 * 0.62 + moy * 17 + last_cote * 7)), 1)

    win_s, loss_s, _ = get_current_streak(st.session_state.history)
    vols = [h.get("moy", 2.5) for h in st.session_state.history[-12:]]
    volatility = round(np.std(vols) if len(vols) > 4 else 1.2, 2)

    ai_score = ai_predict_ultra([prob_x3, conf, moy, spread, last_cote, conf, win_s, loss_s, volatility])

    base_strength = prob_x3 * 0.53 + (ai_score or conf) * 0.42
    streak_adj = win_s * 2.1 - loss_s * 2.4
    strength = round(base_strength + streak_adj + (volatility * 1.8), 1)
    strength = max(22, min(96, strength))

    entry = entry_calc_fixed(h_hex, spread, t_in, strength, prob_x3)

    if strength > 82:
        signal = "💎💎💎 ULTRA X3+ BUY"
        signal_class = "signal-ultra"
    elif strength > 71:
        signal = "🔥 STRONG X3 TARGET"
        signal_class = "signal-strong"
    elif strength > 56:
        signal = "🟢 GOOD X3 SCALP"
        signal_class = "signal-good"
    elif strength > 43:
        signal = "⚡ LIGHT ENTRY"
        signal_class = "signal-light"
    else:
        signal = "⚠️ SKIP - Low X3 Chance"
        signal_class = "signal-skip"

    res = {
        "entry": entry, "signal": signal, "signal_class": signal_class,
        "x3_prob": prob_x3, "conf": conf, "moy": moy, "max": maxv, "min": minv,
        "spread": spread, "last_cote_used": round(last_cote, 2),
        "ai_score": ai_score, "strength": strength,
        "win_streak": win_s, "loss_streak": loss_s, "volatility": volatility,
        "real_result": None
    }

    st.session_state.history.append(res)
    if len(st.session_state.history) > 35:
        st.session_state.history.pop(0)

    train_ai_ultra()
    return res

# ==========================================
# UI PRINCIPALE
# ==========================================
st.markdown("<h1 class='main-title'>JETX ANDR V14</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00ffcc; font-size:1.4rem;'>ULTRA STYLÉ • AI + STREAK</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🔑 Paramètres du Round")

    h_in = st.text_input("HASH (Provably Fair)", placeholder="Collez le hash complet...")
    t_in = st.text_input("TIME (HH:MM:SS)", placeholder="Ex: 21:35:12")
    last_cote = st.number_input("LAST COTE (Round précédent)", value=2.3, step=0.1, format="%.2f")

    if st.button("🚀 LANCER LE CALCUL ULTRA"):
        if h_in.strip() and len(t_in.strip()) >= 8:
            with st.spinner("Calcul ultra en cours..."):
                st.session_state.last = run_engine_ultra(h_in, t_in, last_cote)
                st.success("✅ Signal généré avec succès !")
        else:
            st.warning("Veuillez remplir correctement le HASH et le TIME.")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.sidebar.button("🔄 Réinitialiser tout"):
        st.session_state.history = []
        if "last" in st.session_state:
            del st.session_state.last
        st.rerun()

with col2:
    if "last" in st.session_state:
        r = st.session_state.last
        st.markdown(f"""
        <div class="glass-card">
            <h2 class="{r['signal_class']}">{r['signal']}</h2>
            <h3>X3 PROB : <span style="color:#ff00ff; font-size:1.8rem;">{r['x3_prob']}%</span> | CONF : {r['conf']}</h3>
            <h1 style="font-size:4rem; color:#00ffcc;">{r['entry']}</h1>
            <p>MIN: {r['min']} | MOY: {r['moy']} | MAX: {r['max']}</p>
            <small>Strength: <b>{r['strength']}</b> | Win Streak: {r['win_streak']} | Loss Streak: {r['loss_streak']}</small>
        </div>
        """, unsafe_allow_html=True)

# Historique
st.markdown("### 📜 Historique des Signaux")
if st.session_state.history:
    df_hist = pd.DataFrame(st.session_state.history)[::-1]
    edited_df = st.data_editor(
        df_hist,
        column_config={
            "real_result": st.column_config.SelectboxColumn("✅ Résultat Réel", options=["win", "loss", None])
        },
        hide_index=True,
        use_container_width=True
    )

    if st.button("💾 Sauvegarder & Réentraîner l'IA"):
        for d_idx, row in edited_df.iterrows():
            orig_idx = len(st.session_state.history) - 1 - d_idx
            if orig_idx < len(st.session_state.history):
                st.session_state.history[orig_idx]["real_result"] = row["real_result"]
        train_ai_ultra()
        st.success("✅ IA mise à jour avec vos résultats réels et streaks !")
        st.rerun()

st.caption("JETX ANDR V14 ULTRA STYLÉ • Mot de passe : JET2026")
