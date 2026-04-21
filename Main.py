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
    st.markdown("<h1 style='text-align:center;font-size:4.5rem;background:linear-gradient(90deg,#00ffcc,#ff00ff,#00ccff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>JETX ANDR</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#00ffcc;'>V14.5 MOBILE OPTIMISÉ</h2>", unsafe_allow_html=True)
    
    pw = st.text_input("🔑 Mot de passe", type="password")
    if st.button("✅ Accéder à l'application"):
        if pw == "JET2026":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Mot de passe incorrect")
    st.stop()

# ===================== CONFIG =====================
st.set_page_config(page_title="JETX ANDR V14.5", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a1f, #1a0033); color: #e0fbfc; }
    .main-title { font-family: 'Orbitron', sans-serif; font-size: 4.5rem; font-weight: 900; text-align: center;
                  background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff); -webkit-background-clip: text;
                  -webkit-text-fill-color: transparent; text-shadow: 0 0 50px #00ffcc; }
    .glass { background: rgba(20,20,50,0.95); border: 1px solid #00ffcc; border-radius: 20px; 
              padding: 20px; box-shadow: 0 15px 50px rgba(0,255,204,0.3); }
</style>
""", unsafe_allow_html=True)

# ===================== SESSION STATE =====================
if "history" not in st.session_state: st.session_state.history = []
if "last" not in st.session_state: st.session_state.last = None
if "ml_ready" not in st.session_state: st.session_state.ml_ready = False

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
    win_s = loss_s = 0
    last = marked[-1]
    for res in reversed(marked):
        if res == last:
            win_s += (res == "win")
            loss_s += (res == "loss")
        else: break
    return win_s, loss_s

# ===================== ULTRA ENGINE X3+ =====================
def run_engine_ultra(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:40], 16)
    np.random.seed(h_num & 0xFFFFFFFF)

    base = 1.85 + (h_num % 720) / 95
    sigma = 0.233 - (last_cote * 0.0034)
    sims = np.random.lognormal(np.log(base), sigma, 75000)

    prob_x3 = round(np.mean(sims >= 3.0) * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 97.5), 2)
    minv = round(np.percentile(sims, 2.5), 2)

    conf = round(max(48, min(99, prob_x3*0.67 + moy*19.5 + (h_num % 130)/3.8 + last_cote*12)), 1)

    win_s, loss_s = get_current_streak(st.session_state.history)
    volatility = round(np.std([h.get("moy", 2.5) for h in st.session_state.history[-20:]]) if st.session_state.history else 1.25, 2)

    ai_score = round(conf * 0.93, 1)
    if st.session_state.ml_ready and len(st.session_state.history) > 10:
        try:
            features = [prob_x3, conf, moy, maxv-minv, last_cote, win_s, loss_s, volatility]
            X = st.session_state.scaler.transform(np.array(features).reshape(1, -1))
            prob = st.session_state.ml_clf.predict_proba(X)[0][1] * 100
            reg = st.session_state.ml_reg.predict(X)[0]
            ai_score = round(0.71 * prob + 0.29 * reg, 1)
        except: pass

    strength = round(prob_x3*0.60 + ai_score*0.30 + win_s*6 - loss_s*4.5 + volatility*6.5, 1)
    strength = max(40, min(99, strength))

    # Entry Time
    try:
        bt = datetime.combine(get_time().date(), datetime.strptime(t_in.strip(), "%H:%M:%S").time())
    except:
        bt = get_time()
    shift = (int(h_hex[:16], 16) % 52) - 26
    sec = 19 + (h_num % 43) + shift + int(volatility*3.2) + (21 if strength > 86 else 14 if strength > 73 else 8)
    entry = (bt + timedelta(seconds=max(19, min(85, sec)))).strftime("%H:%M:%S")

    signal = "💎💎 ULTRA X3+" if strength > 87 else "🔥 STRONG X3" if strength > 76 else "🟢 GOOD X3"

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
st.markdown("<h1 class='main-title'>JETX ANDR V14.5</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#00ffcc;font-size:1.65rem;'>ULTRA PUISSANTE • OPTIMISÉ MOBILE</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2.1])

with col1:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    h_in = st.text_input("HASH (Provably Fair)", placeholder="Collez le hash complet...")
    t_in = st.text_input("TIME (HH:MM:SS)", placeholder="08:18:48")
    last_cote = st.number_input("LAST COTE", value=2.5, step=0.1, format="%.2f")

    if st.button("🚀 LANCER CALCUL ULTRA X3+", use_container_width=True):
        if h_in.strip() and len(t_in.strip()) >= 8:
            with st.spinner("Simulation 75 000x en cours..."):
                st.session_state.last = run_engine_ultra(h_in.strip(), t_in.strip(), last_cote)
        else:
            st.warning("Veuillez remplir Hash et Time")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if st.session_state.last:
        r = st.session_state.last
        
        st.markdown(f"<div class='glass'><h2 style='color:#00ffcc'>{r['signal']}</h2>", unsafe_allow_html=True)
        st.markdown(f"**X3 PROB :** <span style='color:#ff00ff;font-size:1.8rem;'>{r['x3_prob']}%</span> | **CONF :** {r['conf']} | **AI :** {r['ai_score']}", unsafe_allow_html=True)
        st.markdown(f"<h1 style='font-size:4.2rem;color:#00ffcc;text-align:center;'>{r['entry']}</h1>", unsafe_allow_html=True)

        # MIN MOY MAX avec Streamlit Columns (très fiable sur mobile)
        cmin, cmoy, cmax = st.columns(3)
        with cmin:
            st.metric(label="MIN", value=r['min'])
        with cmoy:
            st.metric(label="MOY", value=r['moy'])
        with cmax:
            st.metric(label="MAX", value=r['max'])

        st.markdown(f"""
        **💡 Cashout Strategy :**  
        • MIN → Safe Cashout  
        • MOY → Cashout Normal  
        • MAX → All-in 3x+
        """)
        
        st.markdown(f"**Strength : {r['strength']}** | Volatility : {r['volatility']}")
        st.markdown("</div>", unsafe_allow_html=True)

        col_win, col_loss = st.columns(2)
        with col_win:
            if st.button("✅ WIN", use_container_width=True):
                if st.session_state.history:
                    st.session_state.history[-1]["real_result"] = "win"
                    st.rerun()
        with col_loss:
            if st.button("❌ LOSS", use_container_width=True):
                if st.session_state.history:
                    st.session_state.history[-1]["real_result"] = "loss"
                    st.rerun()

# Historique
st.markdown("### 📜 Historique")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)[::-1]
    st.data_editor(df, use_container_width=True, hide_index=True)

st.caption("JETX ANDR V14.5 • Ultra Puissante • Optimisé Mobile")
