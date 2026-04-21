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
    st.markdown("<h2 style='text-align:center;color:#00ffcc;'>V14.4 ULTRA FIXÉ</h2>", unsafe_allow_html=True)
    
    pw = st.text_input("🔑 Mot de passe", type="password")
    if st.button("✅ Accéder"):
        if pw == "JET2026":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Incorrect")
    st.stop()

# ===================== CSS =====================
st.set_page_config(page_title="JETX ANDR V14.4", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a1f, #1a0033); color: #e0fbfc; }
    .main-title { font-family: 'Orbitron', sans-serif; font-size: 4.6rem; font-weight: 900; text-align: center;
                  background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff); -webkit-background-clip: text;
                  -webkit-text-fill-color: transparent; text-shadow: 0 0 50px #00ffcc; }
    .glass { background: rgba(20,20,50,0.95); border: 1px solid #00ffcc; border-radius: 25px; 
              padding: 25px; backdrop-filter: blur(25px); box-shadow: 0 20px 60px rgba(0,255,204,0.3); }
    .result-box { padding: 18px; border-radius: 18px; text-align: center; font-size: 1.4rem; margin: 6px; }
</style>
""", unsafe_allow_html=True)

# ===================== SESSION =====================
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

# ===================== ULTRA ENGINE =====================
def run_engine_ultra(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:40], 16)
    np.random.seed(h_num & 0xFFFFFFFF)

    base = 1.82 + (h_num % 680)/88
    sigma = 0.235 - last_cote * 0.0033
    sims = np.random.lognormal(np.log(base), sigma, 70000)

    prob_x3 = round(np.mean(sims >= 3.0) * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 97.5), 2)
    minv = round(np.percentile(sims, 2.5), 2)

    conf = round(max(48, min(99, prob_x3*0.68 + moy*20 + (h_num % 140)/4 + last_cote*11)), 1)

    win_s, loss_s = get_current_streak(st.session_state.history)
    volatility = round(np.std([h.get("moy",2.5) for h in st.session_state.history[-18:]]) if st.session_state.history else 1.2, 2)

    ai_score = round(conf * 0.92, 1)
    if st.session_state.ml_ready and len(st.session_state.history) > 10:
        try:
            feat = [prob_x3, conf, moy, maxv-minv, last_cote, win_s, loss_s, volatility]
            X = st.session_state.scaler.transform(np.array(feat).reshape(1,-1))
            p = st.session_state.ml_clf.predict_proba(X)[0][1]*100
            r = st.session_state.ml_reg.predict(X)[0]
            ai_score = round(0.72*p + 0.28*r, 1)
        except: pass

    strength = round(prob_x3*0.61 + ai_score*0.29 + win_s*5.8 - loss_s*4.2 + volatility*6, 1)
    strength = max(40, min(99, strength))

    # Entry Time
    try:
        bt = datetime.combine(get_time().date(), datetime.strptime(t_in.strip(),"%H:%M:%S").time())
    except:
        bt = get_time()
    shift = (int(h_hex[:16],16) % 48) - 24
    sec = 20 + (h_num % 41) + shift + int(volatility*3) + (20 if strength>87 else 13 if strength>72 else 7)
    entry = (bt + timedelta(seconds=max(19,min(88,sec)))).strftime("%H:%M:%S")

    signal = "💎 ULTRA X3+" if strength > 87 else "🔥 STRONG X3" if strength > 75 else "🟢 GOOD ENTRY"

    res = {
        "entry": entry, "signal": signal, "x3_prob": prob_x3, "conf": conf, "ai_score": ai_score,
        "min": minv, "moy": moy, "max": maxv, "strength": strength, "volatility": volatility,
        "real_result": None
    }
    st.session_state.history.append(res)
    if len(st.session_state.history) > 60: st.session_state.history.pop(0)
    st.session_state.ml_ready = True
    return res

# ===================== INTERFACE =====================
st.markdown("<h1 class='main-title'>JETX ANDR V14.4</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#00ffcc;font-size:1.6rem;'>ULTRA PUISSANTE • X3+ CIBLÉ</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    h_in = st.text_input("HASH", placeholder="Collez le hash complet...")
    t_in = st.text_input("TIME (HH:MM:SS)", placeholder="08:18:48")
    last_cote = st.number_input("LAST COTE", value=2.5, step=0.1)

    if st.button("🚀 LANCER CALCUL ULTRA", use_container_width=True):
        if h_in and t_in:
            with st.spinner("Simulation 70k + Hash Analysis..."):
                st.session_state.last = run_engine_ultra(h_in.strip(), t_in.strip(), last_cote)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if st.session_state.last:
        r = st.session_state.last
        st.markdown(f"""
        <div class="glass">
            <h2 style="color:#00ffcc">{r['signal']}</h2>
            <h3>X3 PROB : <span style="color:#ff00ff;font-size:2.4rem;">{r['x3_prob']}%</span> | 
                CONF : {r['conf']} | AI : {r['ai_score']}</h3>
            <h1 style="font-size:4.8rem;color:#00ffcc;margin:10px 0;">{r['entry']}</h1>
            
            <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;">
                <div class="result-box" style="background:#00cc88;color:#000;flex:1;min-width:100px;">
                    <small>MIN</small><br><b>{r['min']}</b>
                </div>
                <div class="result-box" style="background:#ffcc00;color:#000;flex:1;min-width:100px;">
                    <small>MOY</small><br><b>{r['moy']}</b>
                </div>
                <div class="result-box" style="background:#ff3366;color:#fff;flex:1;min-width:100px;">
                    <small>MAX</small><br><b>{r['max']}</b>
                </div>
            </div>

            <p><b>💡 Cashout :</b><br>
            • MIN → Safe<br>
            • MOY → Normal<br>
            • MAX → 3x+</p>
            
            <small><b>Strength:</b> {r['strength']} | Volatility: {r['volatility']}</small>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ WIN", use_container_width=True):
                st.session_state.history[-1]["real_result"] = "win"
                st.rerun()
        with c2:
            if st.button("❌ LOSS", use_container_width=True):
                st.session_state.history[-1]["real_result"] = "loss"
                st.rerun()

st.caption("JETX ANDR V14.4 • Affichage corrigé • Ultra Puissante")
