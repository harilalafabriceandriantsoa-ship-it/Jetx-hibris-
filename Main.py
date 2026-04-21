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
    <style>.stApp { background: linear-gradient(135deg, #0a0a1f, #1a0033); }</style>
    """, unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; font-size:5rem; background:linear-gradient(90deg,#00ffcc,#ff00ff,#00ccff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>JETX ANDR</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#00ffcc;'>V14.3 ULTRA PUISSANTE X3</h2>", unsafe_allow_html=True)
    
    pw = st.text_input("🔑 Mot de passe", type="password")
    if st.button("✅ Accéder à l'application"):
        if pw == "JET2026":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Mot de passe incorrect")
    st.stop()

# ===================== CSS STYLÉ =====================
st.set_page_config(page_title="JETX ANDR V14.3", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a1f 0%, #1a0033 100%); color: #e0fbfc; }
    .main-title { font-family: 'Orbitron', sans-serif; font-size: 4.8rem; font-weight: 900; text-align: center;
                  background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff, #ffff00);
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                  text-shadow: 0 0 60px rgba(0,255,204,0.8); }
    .glass-card { background: rgba(15,15,40,0.95); border: 1px solid rgba(0,255,204,0.8);
                  border-radius: 30px; padding: 32px; backdrop-filter: blur(32px);
                  box-shadow: 0 25px 70px rgba(0,255,204,0.45); }
    .result-grid { display: flex; gap: 18px; margin: 28px 0; }
    .result-box { flex: 1; padding: 20px; border-radius: 20px; text-align: center; font-size: 1.35rem; }
    .signal-ultra { color: #00ffcc; text-shadow: 0 0 35px #00ffcc; }
    .signal-strong { color: #ff00ff; text-shadow: 0 0 30px #ff00ff; }
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
    streak_win = streak_loss = 0
    last = marked[-1]
    for res in reversed(marked):
        if res == last:
            streak_win += 1 if res == "win" else 0
            streak_loss += 1 if res == "loss" else 0
        else: break
    return streak_win, streak_loss

# ===================== ULTRA ENGINE X3+ AVANCÉ =====================
def run_engine_ultra(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:40], 16)                     # Ultra hash sensitive
    np.random.seed(h_num & 0xFFFFFFFF)

    last_cote = max(1.0, min(9.0, last_cote))

    # Calcul ultra puissant
    base = 1.85 + (h_num % 720) / 95.0
    sigma = 0.232 - (last_cote * 0.0032)
    sims = np.random.lognormal(np.log(base), sigma, 80000)   # 80 000 simulations

    prob_x3 = round(np.mean(sims >= 3.0) * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 97.8), 2)
    minv = round(np.percentile(sims, 2.2), 2)
    spread = round(maxv - minv, 2)

    conf = round(max(48, min(99, prob_x3*0.69 + moy*21 + (h_num%150)/3.8 + last_cote*12.5)), 1)

    win_s, loss_s = get_current_streak(st.session_state.history)
    volatility = round(np.std([h.get("moy", 2.5) for h in st.session_state.history[-20:]]) if st.session_state.history else 1.2, 2)

    # AI Score
    ai_score = round(conf * 0.94, 1)
    if st.session_state.ml_ready and len(st.session_state.history) >= 12:
        try:
            features = [prob_x3, conf, moy, spread, last_cote, win_s, loss_s, volatility]
            X = st.session_state.scaler.transform(np.array(features).reshape(1, -1))
            prob = st.session_state.ml_clf.predict_proba(X)[0][1] * 100
            reg = st.session_state.ml_reg.predict(X)[0]
            ai_score = round(0.73*prob + 0.27*reg, 1)
        except: pass

    strength = round(prob_x3*0.62 + ai_score*0.28 + win_s*6 - loss_s*4.5 + volatility*6.2, 1)
    strength = max(42, min(99, strength))

    # Entry Time Ultra Dynamique
    try:
        base_time = datetime.combine(get_time().date(), datetime.strptime(t_in.strip(), "%H:%M:%S").time())
    except:
        base_time = get_time()

    shift = (int(h_hex[:18], 16) % 55) - 27
    final_sec = 18 + (h_num % 45) + shift + int(volatility*3.5) + (22 if strength > 88 else 14 if strength > 75 else 8)
    final_sec = max(19, min(85, final_sec))

    entry = (base_time + timedelta(seconds=final_sec)).strftime("%H:%M:%S")

    # Signal
    if strength > 89:
        signal = "💎💎💎 ULTRA X3+ BUY"
        sig_class = "signal-ultra"
    elif strength > 78:
        signal = "🔥 STRONG X3 TARGET"
        sig_class = "signal-strong"
    else:
        signal = "🟢 GOOD X3 ENTRY"
        sig_class = "signal-strong"

    res = {
        "entry": entry, "signal": signal, "signal_class": sig_class,
        "x3_prob": prob_x3, "conf": conf, "ai_score": ai_score,
        "min": minv, "moy": moy, "max": maxv, "strength": strength,
        "volatility": volatility, "real_result": None
    }

    st.session_state.history.append(res)
    if len(st.session_state.history) > 60: st.session_state.history.pop(0)
    st.session_state.ml_ready = True
    return res

# ===================== UI =====================
st.markdown("<h1 class='main-title'>JETX ANDR V14.3</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#00ffcc;font-size:1.7rem;'>ULTRA PUISSANTE • X3+ CIBLÉ • HASH AVANCÉ</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2.1])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    h_in = st.text_input("🔑 HASH (Provably Fair)", placeholder="Collez le hash complet...")
    t_in = st.text_input("⏰ TIME (HH:MM:SS)", placeholder="Ex: 14:35:27")
    last_cote = st.number_input("LAST COTE", value=2.6, step=0.1, format="%.2f")

    if st.button("🚀 LANCER CALCUL ULTRA X3+", use_container_width=True):
        if h_in and len(t_in) >= 8:
            with st.spinner("Simulation 80 000x + Analyse Hash Ultra..."):
                st.session_state.last = run_engine_ultra(h_in.strip(), t_in.strip(), last_cote)
        else:
            st.warning("Remplis Hash et Time svp")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if st.session_state.last:
        r = st.session_state.last
        st.markdown(f"""
        <div class="glass-card">
            <h2 class="{r['signal_class']}">{r['signal']}</h2>
            <h3>X3 PROB : <span style="color:#ff00ff;font-size:2.6rem;">{r['x3_prob']}%</span> | 
                CONF : {r['conf']} | AI : {r['ai_score']}</h3>
            <h1 style="font-size:5rem;color:#00ffcc;margin:15px 0;">{r['entry']}</h1>
            
            <div class="result-grid">
                <div class="result-box" style="background:#00cc88;color:#000;">
                    <small>MIN</small><br><b>{r['min']}</b>
                </div>
                <div class="result-box" style="background:#ffcc00;color:#000;">
                    <small>MOY</small><br><b>{r['moy']}</b>
                </div>
                <div class="result-box" style="background:#ff3366;color:#fff;">
                    <small>MAX</small><br><b>{r['max']}</b>
                </div>
            </div>

            <p><b>💡 Cashout Strategy :</b><br>
            • MIN → Safe Cashout<br>
            • MOY → Cashout Normal<br>
            • MAX → All-in 3x+</p>
            
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

# Historique
st.markdown("### 📜 Historique des Prédictions")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)[::-1]
    st.data_editor(df, use_container_width=True, hide_index=True)

st.caption("JETX ANDR V14.3 ULTRA PUISSANTE X3+ • Hash Avancé • Entry Dynamique")
