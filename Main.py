import streamlit as st
import numpy as np
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import pytz

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# ==========================================
# 🔐 PASSWORD PROTECTION
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #0a0a1f, #1a0033); }
        .login-title { font-size: 5rem; font-weight: 900; text-align: center;
                       background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("<h1 class='login-title'>JETX ANDR</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#00ffcc; margin-bottom:40px;'>V14.2 ULTRA ADVANCED</h2>", unsafe_allow_html=True)
    
    pw = st.text_input("🔑 Entrez le mot de passe :", type="password")
    if st.button("✅ Accéder à l'application", use_container_width=True):
        if pw == "JET2026":
            st.session_state.authenticated = True
            st.success("✅ Accès autorisé !")
            st.rerun()
        else:
            st.error("❌ Mot de passe incorrect")
    st.stop()

# ==========================================
# 💎 UI + CSS
# ==========================================
st.set_page_config(page_title="JETX ANDR V14.2", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a1f 0%, #1a0033 100%); color: #e0fbfc; }
    .main-title { font-family: 'Orbitron', sans-serif; font-size: 4.8rem; font-weight: 900; text-align: center;
                  background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff, #ffff00);
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                  text-shadow: 0 0 50px rgba(0,255,204,0.8); margin-bottom: 8px; }
    .glass-card { background: rgba(15,15,40,0.9); border: 1px solid rgba(0,255,204,0.7);
                  border-radius: 28px; padding: 32px; backdrop-filter: blur(30px);
                  box-shadow: 0 20px 60px rgba(0,255,204,0.4); }
    .signal-ultra { color: #00ffcc; text-shadow: 0 0 30px #00ffcc; }
    .signal-strong { color: #ff00ff; text-shadow: 0 0 25px #ff00ff; }
    .signal-good  { color: #00ff88; text-shadow: 0 0 20px #00ff88; }
    .signal-light { color: #ffff66; text-shadow: 0 0 20px #ffff66; }
    .signal-skip  { color: #ff6666; text-shadow: 0 0 20px #ff6666; }
    .stButton>button { background: linear-gradient(135deg, #00ff88, #ff00ff, #00ccff) !important;
                       color: #000 !important; font-family: 'Orbitron', sans-serif !important;
                       font-weight: 700 !important; border-radius: 50px !important; height: 72px !important;
                       font-size: 1.4rem !important; box-shadow: 0 0 40px rgba(0,255,204,0.8); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE
# ==========================================
if "history" not in st.session_state:
    st.session_state.history = []
if "last" not in st.session_state:
    st.session_state.last = None

if "ml_clf" not in st.session_state:
    st.session_state.ml_clf = RandomForestClassifier(n_estimators=400, max_depth=12, random_state=42)
if "ml_reg" not in st.session_state:
    st.session_state.ml_reg = RandomForestRegressor(n_estimators=250, max_depth=10, random_state=42)
if "ml_ready" not in st.session_state:
    st.session_state.ml_ready = False
if "scaler" not in st.session_state:
    st.session_state.scaler = StandardScaler()

def get_time():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def get_current_streak(history):
    marked = [h.get("real_result") for h in history if h.get("real_result") in ["win", "loss"]]
    if not marked: return 0, 0, None
    streak_win = streak_loss = 0
    last = marked[-1]
    for res in reversed(marked):
        if res == last:
            if res == "win": streak_win += 1
            else: streak_loss += 1
        else: break
    return streak_win, streak_loss, last

def prepare_ml_data(history):
    data = []
    for i in range(len(history)):
        h = history[i]
        prev = history[:i]
        win_s, loss_s, _ = get_current_streak(prev)
        vols = [p.get("moy", 2.5) for p in prev[-15:]]
        volatility = round(np.std(vols) if len(vols) > 5 else 1.15, 2)
        features = [
            h.get("x3_prob", 50), h.get("conf", 50), h.get("moy", 2.5),
            h.get("spread", 3.0), h.get("last_cote_used", 2.0),
            h.get("strength", 50), win_s, loss_s, volatility
        ]
        label = 1 if h.get("real_result") == "win" else 0
        data.append(features + [label])
    return data

def train_ai_ultra():
    data = prepare_ml_data(st.session_state.history)
    if len(data) < 12: 
        return
    df = pd.DataFrame(data)
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    X_scaled = st.session_state.scaler.fit_transform(X)
    st.session_state.ml_clf.fit(X_scaled, y)
    st.session_state.ml_reg.fit(X_scaled, df.iloc[:, 2])  # moy column
    st.session_state.ml_ready = True

def ai_predict_ultra(features):
    if not st.session_state.ml_ready or len(st.session_state.history) < 12:
        return None
    try:
        X = np.array(features).reshape(1, -1)
        X_scaled = st.session_state.scaler.transform(X)
        prob_win = st.session_state.ml_clf.predict_proba(X_scaled)[0][1] * 100
        refined = st.session_state.ml_reg.predict(X_scaled)[0]
        return round(0.71 * prob_win + 0.29 * refined, 1)
    except:
        return None

# ==========================================
# ENGINE ULTRA AVANCÉ (Hash Sensitive)
# ==========================================
def run_engine_ultra(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:32], 16)
    np.random.seed(h_num & 0xFFFFFFFF)

    last_cote = max(1.0, min(last_cote, 8.5))

    # Calcul très sensible au hash
    base_mean = 1.78 + (h_num % 680) / 92.0
    sigma = 0.238 - (last_cote * 0.0035)

    sims = np.random.lognormal(np.log(base_mean), sigma, 65000)

    prob_x3 = round(np.mean(sims >= 3.0) * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 97.5), 2)
    minv = round(np.percentile(sims, 2.5), 2)
    spread = round(maxv - minv, 2)

    conf = round(max(40, min(99, prob_x3 * 0.67 + moy * 19.5 + (h_num % 120)/4.2 + last_cote * 11)), 1)

    win_s, loss_s, _ = get_current_streak(st.session_state.history)
    vols = [h.get("moy", 2.5) for h in st.session_state.history[-15:]]
    volatility = round(np.std(vols) if len(vols) > 5 else 1.15, 2)

    features = [prob_x3, conf, moy, spread, last_cote, conf, win_s, loss_s, volatility]
    ai_score = ai_predict_ultra(features)

    # Strength
    strength = round(prob_x3 * 0.57 + (ai_score or conf) * 0.33 + win_s*5.5 - loss_s*4.3 + volatility*6.2, 1)
    strength = max(38, min(99, strength))

    # ===================== HEURE D'ENTRÉE DYNAMIQUE =====================
    now = get_time()
    try:
        t_obj = datetime.strptime(t_in.strip(), "%H:%M:%S").time()
        base_time = datetime.combine(now.date(), t_obj)
    except:
        base_time = now

    hash_shift = (int(h_hex[:18], 16) % 52) - 26
    volatility_factor = int(volatility * 3.2)
    strength_factor = 16 if strength > 88 else 11 if strength > 76 else 6 if strength > 63 else 3
    prob_factor = 24 if prob_x3 > 85 else 17 if prob_x3 > 73 else 11

    final_seconds = 21 + (h_num % 39) + hash_shift + volatility_factor + strength_factor + prob_factor
    final_seconds = max(17, min(82, final_seconds))

    entry = (base_time + timedelta(seconds=final_seconds)).strftime("%H:%M:%S")

    # Signal
    if strength > 88:
        signal = "💎💎💎 ULTRA X3+ BUY"
        signal_class = "signal-ultra"
    elif strength > 77:
        signal = "🔥 STRONG X3 TARGET"
        signal_class = "signal-strong"
    elif strength > 65:
        signal = "🟢 GOOD X3 SCALP"
        signal_class = "signal-good"
    elif strength > 50:
        signal = "⚡ LIGHT ENTRY"
        signal_class = "signal-light"
    else:
        signal = "⚠️ SKIP - Low X3 Chance"
        signal_class = "signal-skip"

    res = {
        "entry": entry, "signal": signal, "signal_class": signal_class,
        "x3_prob": prob_x3, "conf": conf, "moy": moy, "max": maxv, "min": minv,
        "spread": spread, "last_cote_used": round(last_cote, 2),
        "ai_score": ai_score or round(conf*0.93, 1), "strength": strength,
        "win_streak": win_s, "loss_streak": loss_s, "volatility": volatility,
        "real_result": None
    }

    st.session_state.history.append(res)
    if len(st.session_state.history) > 60:
        st.session_state.history.pop(0)
    
    train_ai_ultra()
    return res

# ==========================================
# INTERFACE
# ==========================================
st.markdown("<h1 class='main-title'>JETX ANDR V14.2</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00ffcc; font-size:1.7rem;'>HASH SENSITIVE • ENTRY DYNAMIQUE • 65K SIMULATIONS</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2.1])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    h_in = st.text_input("HASH (Provably Fair)", placeholder="Collez le hash complet...")
    t_in = st.text_input("TIME (HH:MM:SS)", placeholder="Ex: 08:15:42")
    last_cote = st.number_input("LAST COTE", value=2.4, step=0.1, format="%.2f")

    if st.button("🚀 LANCER LE CALCUL ULTRA", use_container_width=True):
        if h_in.strip() and len(t_in.strip()) >= 8:
            with st.spinner("Simulation 65 000x + Analyse Hash Avancée..."):
                st.session_state.last = run_engine_ultra(h_in.strip(), t_in.strip(), last_cote)
        else:
            st.warning("Veuillez remplir le Hash et le Time")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.sidebar.button("🔄 Reset All Data"):
        st.session_state.history = []
        st.session_state.last = None
        st.rerun()

with col2:
    if st.session_state.last:
        r = st.session_state.last
        st.markdown(f"""
        <div class="glass-card">
            <h2 class="{r.get('signal_class')}">{r.get('signal')}</h2>
            <h3>X3 PROB : <span style="color:#ff00ff;font-size:2.3rem;">{r.get('x3_prob')}%</span> | 
                CONF : {r.get('conf')} | AI : {r.get('ai_score')}</h3>
            <h1 style="font-size:4.8rem;color:#00ffcc;margin:15px 0;">{r.get('entry')}</h1>
            
            <div style="display:flex; gap:15px; margin:25px 0;">
                <div style="background:#00cc88;color:#000;padding:16px;border-radius:16px;flex:1;text-align:center;">
                    <small>MIN</small><br><b>{r.get('min')}</b>
                </div>
                <div style="background:#ffcc00;color:#000;padding:16px;border-radius:16px;flex:1;text-align:center;">
                    <small>MOY</small><br><b>{r.get('moy')}</b>
                </div>
                <div style="background:#ff3366;color:#fff;padding:16px;border-radius:16px;flex:1;text-align:center;">
                    <small>MAX</small><br><b>{r.get('max')}</b>
                </div>
            </div>

            <p><b>💡 Cashout :</b><br>
            • MIN → safe<br>
            • MOY → normal<br>
            • MAX → 3x+</p>
            
            <small>Strength: <b>{r.get('strength')}</b> | Volatility: {r.get('volatility')}</small>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Marque ce round :**")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ WIN", use_container_width=True):
                if st.session_state.history:
                    st.session_state.history[-1]["real_result"] = "win"
                    st.rerun()
        with c2:
            if st.button("❌ LOSS", use_container_width=True):
                if st.session_state.history:
                    st.session_state.history[-1]["real_result"] = "loss"
                    st.rerun()

# Historique
st.markdown("### 📜 Historique")
if st.session_state.history:
    df_hist = pd.DataFrame(st.session_state.history)[::-1]
    edited = st.data_editor(df_hist, use_container_width=True, hide_index=True)
    
    if st.button("💾 Sauvegarder & Réentraîner IA"):
        for i, row in edited.iterrows():
            orig_idx = len(st.session_state.history) - 1 - i
            if 0 <= orig_idx < len(st.session_state.history):
                st.session_state.history[orig_idx]["real_result"] = row["real_result"]
        train_ai_ultra()
        st.success("✅ IA mise à jour")
        st.rerun()

st.caption("JETX ANDR V14.2 ULTRA • Fix complet • Hash Sensitive")
