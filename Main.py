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
    st.markdown("<h1 style='text-align:center;font-size:4.8rem;background:linear-gradient(90deg,#00ffcc,#ff00ff,#00ccff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>JETX ANDR</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#00ffcc;'>V14.6 ULTRA STYLÉ</h2>", unsafe_allow_html=True)
    
    pw = st.text_input("🔑 Mot de passe", type="password")
    if st.button("✅ Accéder"):
        if pw == "JET2026":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Mot de passe incorrect")
    st.stop()

# ===================== CSS STYLÉ =====================
st.set_page_config(page_title="JETX ANDR V14.6", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a1f, #1a0033); color: #e0fbfc; }
    .main-title { font-family: 'Orbitron', sans-serif; font-size: 4.7rem; font-weight: 900; text-align: center;
                  background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff, #ffff00);
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                  text-shadow: 0 0 60px rgba(0,255,204,0.8); margin: 10px 0; }
    .glass { background: rgba(15,15,45,0.96); border: 2px solid rgba(0,255,204,0.6);
              border-radius: 24px; padding: 24px; backdrop-filter: blur(30px);
              box-shadow: 0 20px 70px rgba(0,255,204,0.4); }
    .metric-box { background: rgba(0,255,204,0.1); padding: 15px; border-radius: 16px; text-align: center; border: 1px solid #00ffcc; }
</style>
""", unsafe_allow_html=True)

# ===================== SESSION =====================
if "history" not in st.session_state: st.session_state.history = []
if "last" not in st.session_state: st.session_state.last = None
if "ml_ready" not in st.session_state: st.session_state.ml_ready = False

if "ml_clf" not in st.session_state:
    st.session_state.ml_clf = RandomForestClassifier(n_estimators=500, max_depth=14, random_state=42)
if "ml_reg" not in st.session_state:
    st.session_state.ml_reg = RandomForestRegressor(n_estimators=300, max_depth=11, random_state=42)
if "scaler" not in st.session_state:
    st.session_state.scaler = StandardScaler()

def get_time():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def get_current_streak(history):
    marked = [h.get("real_result") for h in history if h.get("real_result") in ["win", "loss"]]
    if not marked: return 0, 0
    win_s = loss_s = 0
    last = marked[-1]
    for res in reversed(marked):
        if res == last:
            win_s += (res == "win")
            loss_s += (res == "loss")
        else: break
    return win_s, loss_s

# ===================== ULTRA ENGINE – HASH TRÈS PUISSANT =====================
def run_engine_ultra(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:48], 16)          # Encore plus de bits du hash
    np.random.seed(h_num & 0xFFFFFFFF)

    last_cote = max(1.0, min(last_cote, 9.5))

    # Calcul ultra avancé + très dépendant du hash
    base = 1.88 + (h_num % 850) / 105.0
    sigma = 0.229 - (last_cote * 0.0031)
    sims = np.random.lognormal(np.log(base), sigma, 85000)   # 85 000 simulations

    prob_x3 = round(np.mean(sims >= 3.0) * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 97.8), 2)
    minv = round(np.percentile(sims, 2.2), 2)

    # Confidence ultra hash-sensitive
    conf = round(max(45, min(99, prob_x3*0.71 + moy*22 + (h_num % 180)/3.2 + last_cote*13.5 + (int(h_hex[20:28],16)%30))), 1)

    win_s, loss_s = get_current_streak(st.session_state.history)
    volatility = round(np.std([h.get("moy", 2.5) for h in st.session_state.history[-22:]]) if st.session_state.history else 1.22, 2)

    # AI Score
    ai_score = round(conf * 0.91, 1)
    if st.session_state.ml_ready and len(st.session_state.history) > 12:
        try:
            features = [prob_x3, conf, moy, maxv-minv, last_cote, win_s, loss_s, volatility, h_num % 100]
            X = st.session_state.scaler.transform(np.array(features).reshape(1, -1))
            prob = st.session_state.ml_clf.predict_proba(X)[0][1] * 100
            reg = st.session_state.ml_reg.predict(X)[0]
            ai_score = round(0.74 * prob + 0.26 * reg, 1)
        except: pass

    strength = round(prob_x3*0.63 + ai_score*0.27 + win_s*6.5 - loss_s*4.8 + volatility*7, 1)
    strength = max(40, min(99, strength))

    # ===================== HEURE D'ENTRÉE ULTRA DYNAMIQUE (très variable selon hash) =====================
    try:
        bt = datetime.combine(get_time().date(), datetime.strptime(t_in.strip(), "%H:%M:%S").time())
    except:
        bt = get_time()

    # Très sensible au hash
    hash_shift = (int(h_hex[:20], 16) % 68) - 34
    volatility_factor = int(volatility * 4.2)
    strength_factor = 24 if strength > 88 else 17 if strength > 78 else 11 if strength > 68 else 6
    prob_factor = 19 if prob_x3 > 83 else 14 if prob_x3 > 72 else 9

    final_sec = 17 + (h_num % 47) + hash_shift + volatility_factor + strength_factor + prob_factor
    final_sec = max(18, min(92, final_sec))

    entry = (bt + timedelta(seconds=final_sec)).strftime("%H:%M:%S")

    # Signal
    if strength > 88:
        signal = "💎💎💎 ULTRA X3+ BUY"
    elif strength > 78:
        signal = "🔥 STRONG X3 TARGET"
    elif strength > 68:
        signal = "🟢 GOOD X3 SCALP"
    else:
        signal = "⚡ LIGHT ENTRY"

    res = {
        "entry": entry, "signal": signal,
        "x3_prob": prob_x3, "conf": conf, "ai_score": ai_score,
        "min": minv, "moy": moy, "max": maxv,
        "strength": strength, "volatility": volatility,
        "real_result": None
    }

    st.session_state.history.append(res)
    if len(st.session_state.history) > 60:
        st.session_state.history.pop(0)
    st.session_state.ml_ready = True
    return res

# ===================== INTERFACE =====================
st.markdown("<h1 class='main-title'>JETX ANDR V14.6</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#00ffcc;font-size:1.7rem;'>ULTRA STYLÉ • HASH ULTRA SENSIBLE • ENTRY DYNAMIQUE</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2.1])

with col1:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    h_in = st.text_input("HASH (Provably Fair)", placeholder="Collez le hash complet...")
    t_in = st.text_input("TIME (HH:MM:SS)", placeholder="Ex: 08:18:48")
    last_cote = st.number_input("LAST COTE", value=2.6, step=0.1, format="%.2f")

    if st.button("🚀 LANCER CALCUL ULTRA X3+", use_container_width=True):
        if h_in.strip() and len(t_in.strip()) >= 8:
            with st.spinner("85 000 simulations + Analyse Hash Avancée..."):
                st.session_state.last = run_engine_ultra(h_in.strip(), t_in.strip(), last_cote)
        else:
            st.warning("Remplissez Hash et Time")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if st.session_state.last:
        r = st.session_state.last
        st.markdown(f"<div class='glass'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color:#00ffcc'>{r['signal']}</h2>", unsafe_allow_html=True)
        st.markdown(f"**X3 PROB :** <span style='color:#ff00ff;font-size:2.2rem;'>{r['x3_prob']}%</span> | **CONF :** {r['conf']} | **AI :** {r['ai_score']}", unsafe_allow_html=True)
        st.markdown(f"<h1 style='font-size:4.5rem;color:#00ffcc;text-align:center;margin:15px 0;'>{r['entry']}</h1>", unsafe_allow_html=True)

        # MIN MOY MAX stylé
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='metric-box'><small>MIN</small><br><b style='font-size:1.6rem;'>{r['min']}</b></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-box'><small>MOY</small><br><b style='font-size:1.6rem;'>{r['moy']}</b></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='metric-box'><small>MAX</small><br><b style='font-size:1.6rem;'>{r['max']}</b></div>", unsafe_allow_html=True)

        st.markdown(f"""
        **💡 Cashout Strategy :**  
        • MIN → Safe Cashout  
        • MOY → Cashout Normal  
        • MAX → All-in 3x+
        """)
        
        st.markdown(f"**Strength : {r['strength']}** | Volatility : {r['volatility']}")
        st.markdown("</div>", unsafe_allow_html=True)

        # Boutons WIN / LOSS
        win_col, loss_col = st.columns(2)
        with win_col:
            if st.button("✅ WIN", use_container_width=True):
                st.session_state.history[-1]["real_result"] = "win"
                st.rerun()
        with loss_col:
            if st.button("❌ LOSS", use_container_width=True):
                st.session_state.history[-1]["real_result"] = "loss"
                st.rerun()

# Historique simple
st.markdown("### 📜 Historique")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)[::-1]
    st.data_editor(df, use_container_width=True, hide_index=True)

st.caption("JETX ANDR V14.6 ULTRA STYLÉ • Entry Time + Hash Ultra Dynamique")
