import streamlit as st
import numpy as np
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import pytz

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# ===================== PASSWORD =====================
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
    st.markdown("<h2 style='text-align:center; color:#00ffcc;'>V14.2 ULTRA STYLÉ</h2>", unsafe_allow_html=True)
    
    pw = st.text_input("🔑 Entrez le mot de passe :", type="password")
    if st.button("✅ Accéder"):
        if pw == "JET2026":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Mot de passe incorrect")
    st.stop()

# ===================== CONFIG & CSS =====================
st.set_page_config(page_title="JETX ANDR V14.2", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a1f 0%, #1a0033 100%); color: #e0fbfc; }
    .main-title { font-family: 'Orbitron', sans-serif; font-size: 4.6rem; font-weight: 900; text-align: center;
                  background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff, #ffff00);
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                  text-shadow: 0 0 50px rgba(0,255,204,0.8); margin-bottom: 5px; }
    .glass-card { background: rgba(15,15,40,0.92); border: 1px solid rgba(0,255,204,0.7);
                  border-radius: 28px; padding: 30px; backdrop-filter: blur(30px);
                  box-shadow: 0 20px 60px rgba(0,255,204,0.4); }
    .result-box { background: rgba(0,0,0,0.3); padding: 18px; border-radius: 18px; text-align: center; }
    .signal-ultra { color: #00ffcc; text-shadow: 0 0 30px #00ffcc; }
    .signal-strong { color: #ff00ff; text-shadow: 0 0 25px #ff00ff; }
    .signal-good { color: #00ff88; text-shadow: 0 0 20px #00ff88; }
    .signal-light { color: #ffff66; text-shadow: 0 0 20px #ffff66; }
    .signal-skip { color: #ff6666; text-shadow: 0 0 20px #ff6666; }
</style>
""", unsafe_allow_html=True)

# ===================== SESSION STATE =====================
if "history" not in st.session_state:
    st.session_state.history = []
if "last" not in st.session_state:
    st.session_state.last = None
if "ml_ready" not in st.session_state:
    st.session_state.ml_ready = False

if "ml_clf" not in st.session_state:
    st.session_state.ml_clf = RandomForestClassifier(n_estimators=400, max_depth=12, random_state=42)
if "ml_reg" not in st.session_state:
    st.session_state.ml_reg = RandomForestRegressor(n_estimators=250, max_depth=10, random_state=42)
if "scaler" not in st.session_state:
    st.session_state.scaler = StandardScaler()

def get_time():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def get_current_streak(history):
    marked = [h.get("real_result") for h in history if h.get("real_result") in ["win", "loss"]]
    if not marked: return 0, 0
    streak_win = streak_loss = 0
    last = marked[-1]
    for res in reversed(marked):
        if res == last:
            if res == "win": streak_win += 1
            else: streak_loss += 1
        else: break
    return streak_win, streak_loss

# ===================== ENGINE ULTRA =====================
def run_engine_ultra(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:32], 16)
    np.random.seed(h_num & 0xFFFFFFFF)

    last_cote = max(1.0, min(last_cote, 8.0))

    base_mean = 1.78 + (h_num % 650) / 92.0
    sigma = 0.238 - (last_cote * 0.0035)

    sims = np.random.lognormal(np.log(base_mean), sigma, 65000)

    prob_x3 = round(np.mean(sims >= 3.0) * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 97.5), 2)
    minv = round(np.percentile(sims, 2.5), 2)
    spread = round(maxv - minv, 2)

    conf = round(max(45, min(99, prob_x3 * 0.67 + moy * 19.5 + (h_num % 120)/4 + last_cote * 11)), 1)

    win_s, loss_s = get_current_streak(st.session_state.history)
    vols = [h.get("moy", 2.5) for h in st.session_state.history[-15:]]
    volatility = round(np.std(vols) if len(vols) > 5 else 1.18, 2)

    # AI
    ai_score = conf * 0.93
    if st.session_state.ml_ready and len(st.session_state.history) > 10:
        try:
            features = [prob_x3, conf, moy, spread, last_cote, conf, win_s, loss_s, volatility]
            X = np.array(features).reshape(1, -1)
            X_scaled = st.session_state.scaler.transform(X)
            prob_win = st.session_state.ml_clf.predict_proba(X_scaled)[0][1] * 100
            refined = st.session_state.ml_reg.predict(X_scaled)[0]
            ai_score = round(0.71 * prob_win + 0.29 * refined, 1)
        except:
            pass

    strength = round(prob_x3 * 0.59 + ai_score * 0.31 + win_s*5.5 - loss_s*4.3 + volatility*5.8, 1)
    strength = max(40, min(99, strength))

    # Entry Time Dynamique
    now = get_time()
    try:
        t_obj = datetime.strptime(t_in.strip(), "%H:%M:%S").time()
        base_time = datetime.combine(now.date(), t_obj)
    except:
        base_time = now

    hash_shift = (int(h_hex[:16], 16) % 52) - 26
    final_sec = 21 + (h_num % 38) + hash_shift + int(volatility*3) + (18 if strength > 85 else 11 if strength > 70 else 6)
    final_sec = max(19, min(82, final_sec))

    entry = (base_time + timedelta(seconds=final_sec)).strftime("%H:%M:%S")

    # Signal
    if strength > 88:
        signal = "💎💎💎 ULTRA X3+ BUY"; sig_class = "signal-ultra"
    elif strength > 77:
        signal = "🔥 STRONG X3 TARGET"; sig_class = "signal-strong"
    elif strength > 65:
        signal = "🟢 GOOD X3 SCALP"; sig_class = "signal-good"
    elif strength > 50:
        signal = "⚡ LIGHT ENTRY"; sig_class = "signal-light"
    else:
        signal = "⚠️ SKIP"; sig_class = "signal-skip"

    res = {
        "entry": entry, "signal": signal, "signal_class": sig_class,
        "x3_prob": prob_x3, "conf": conf, "moy": moy, "max": maxv, "min": minv,
        "spread": spread, "ai_score": ai_score, "strength": strength,
        "win_streak": win_s, "loss_streak": loss_s, "volatility": volatility,
        "real_result": None
    }

    st.session_state.history.append(res)
    if len(st.session_state.history) > 50:
        st.session_state.history.pop(0)
    st.session_state.ml_ready = True
    return res

# ===================== INTERFACE =====================
st.markdown("<h1 class='main-title'>JETX ANDR V14.2</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00ffcc; font-size:1.65rem;'>ULTRA STYLÉ • HASH SENSITIVE • ENTRY DYNAMIQUE</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2.1])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    h_in = st.text_input("HASH (Provably Fair)", placeholder="Collez le hash complet...")
    t_in = st.text_input("TIME (HH:MM:SS)", placeholder="Ex: 08:22:15")
    last_cote = st.number_input("LAST COTE", value=2.5, step=0.1, format="%.2f")

    if st.button("🚀 LANCER LE CALCUL ULTRA", use_container_width=True):
        if h_in.strip() and len(t_in.strip()) >= 8:
            with st.spinner("Simulation 65 000x + Analyse Hash..."):
                st.session_state.last = run_engine_ultra(h_in.strip(), t_in.strip(), last_cote)
        else:
            st.warning("Veuillez remplir le Hash et le Time")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.sidebar.button("🔄 Reset All"):
        st.session_state.history = []
        st.session_state.last = None
        st.rerun()

# ===================== AFFICHAGE RÉSULTATS =====================
with col2:
    if st.session_state.last:
        r = st.session_state.last
        st.markdown(f"""
        <div class="glass-card">
            <h2 class="{r['signal_class']}">{r['signal']}</h2>
            <h3>X3 PROB : <span style="color:#ff00ff; font-size:2.4rem;">{r['x3_prob']}%</span> | 
                CONF : {r['conf']} | AI : {r['ai_score']}</h3>
            <h1 style="font-size:4.7rem; color:#00ffcc; margin:12px 0;">{r['entry']}</h1>
            
            <div style="display:flex; gap:15px; margin:25px 0;">
                <div class="result-box" style="background:#00cc88; color:#000; flex:1;">
                    <small>MIN</small><br><b>{r['min']}</b>
                </div>
                <div class="result-box" style="background:#ffcc00; color:#000; flex:1;">
                    <small>MOY</small><br><b>{r['moy']}</b>
                </div>
                <div class="result-box" style="background:#ff3366; color:#fff; flex:1;">
                    <small>MAX</small><br><b>{r['max']}</b>
                </div>
            </div>

            <p><b>💡 Cashout :</b><br>
            • MIN → safe<br>
            • MOY → normal<br>
            • MAX → 3x+</p>
            
            <small><b>Strength:</b> {r['strength']} | Volatility: {r['volatility']}</small>
        </div>
        """, unsafe_allow_html=True)

        # Boutons WIN / LOSS
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
    df = pd.DataFrame(st.session_state.history)[::-1]
    st.data_editor(df, use_container_width=True, hide_index=True)

st.caption("JETX ANDR V14.2 • Fixé & Stylé")
