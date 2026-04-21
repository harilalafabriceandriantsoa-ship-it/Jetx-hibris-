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
    st.markdown("<h1 style='text-align:center;font-size:5rem;background:linear-gradient(90deg,#00ffcc,#ff00ff,#00ccff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>JETX ANDR</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#00ffcc;'>V15.2 ULTRA COULEUR</h2>", unsafe_allow_html=True)
    
    pw = st.text_input("🔑 Mot de passe", type="password")
    if st.button("✅ Accéder"):
        if pw == "JET2026":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Mot de passe incorrect")
    st.stop()

# ===================== CSS + COULEUR TSARA =====================
st.set_page_config(page_title="JETX ANDR V15.2", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a1f, #1a0033); color: #e0fbfc; }
    .main-title { font-family: 'Orbitron', sans-serif; font-size: 4.5rem; font-weight: 900; text-align: center;
                  background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff); -webkit-background-clip: text;
                  -webkit-text-fill-color: transparent; text-shadow: 0 0 50px #00ffcc; }
    .glass-card { background: rgba(15,15,40,0.92); border: 1px solid rgba(0,255,204,0.7);
                  border-radius: 24px; padding: 28px; box-shadow: 0 15px 50px rgba(0,255,204,0.35); }
    .signal-ultra { color: #00ffcc; text-shadow: 0 0 30px #00ffcc; }
    .signal-strong { color: #ff00ff; text-shadow: 0 0 25px #ff00ff; }
    
    .res-min { background: linear-gradient(135deg, #00ff88, #00cc66); color: #000; box-shadow: 0 8px 25px rgba(0,255,136,0.4); }
    .res-moy { background: linear-gradient(135deg, #ffd700, #ffaa00); color: #000; box-shadow: 0 8px 25px rgba(255,215,0,0.4); }
    .res-max { background: linear-gradient(135deg, #ff3366, #cc1133); color: #fff; box-shadow: 0 8px 25px rgba(255,51,102,0.5); }
    
    .mini-box { padding: 18px; border-radius: 18px; text-align: center; margin: 6px; font-weight: bold; }
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

# ===================== ULTRA ENGINE V15.2 =====================
def run_engine_ultra(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:48], 16)
    np.random.seed(h_num & 0xFFFFFFFF)

    base = 1.93 + (h_num % 980) / 118
    sigma = 0.226 - (last_cote * 0.0028)
    sims = np.random.lognormal(np.log(base), sigma, 98000)

    prob_x3 = round(np.mean(sims >= 3.0) * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 98.0), 2)
    minv = round(np.percentile(sims, 2.0), 2)

    conf = round(max(48, min(99, prob_x3*0.73 + moy*23.5 + (h_num % 210)/3 + last_cote*14.2)), 1)

    win_s, loss_s = get_current_streak(st.session_state.history)
    volatility = round(np.std([h.get("moy", 2.5) for h in st.session_state.history[-25:]]) if st.session_state.history else 1.26, 2)

    ai_score = round(conf * 0.91, 1)
    if st.session_state.ml_ready and len(st.session_state.history) > 12:
        try:
            features = [prob_x3, conf, moy, maxv-minv, last_cote, win_s, loss_s, volatility]
            X = st.session_state.scaler.transform(np.array(features).reshape(1, -1))
            prob = st.session_state.ml_clf.predict_proba(X)[0][1] * 100
            reg = st.session_state.ml_reg.predict(X)[0]
            ai_score = round(0.75*prob + 0.25*reg, 1)
        except: pass

    strength = round(prob_x3*0.66 + ai_score*0.24 + win_s*7.5 - loss_s*5.3 + volatility*7.8, 1)
    strength = max(40, min(99, strength))

    # Entry Time
    try:
        bt = datetime.combine(get_time().date(), datetime.strptime(t_in.strip(), "%H:%M:%S").time())
    except:
        bt = get_time()
    shift = (int(h_hex[:20], 16) % 72) - 36
    final_sec = 16 + (h_num % 53) + shift + int(volatility*4.5) + (26 if strength > 87 else 17 if strength > 75 else 10)
    final_sec = max(19, min(96, final_sec))
    entry = (bt + timedelta(seconds=final_sec)).strftime("%H:%M:%S")

    if strength > 87:
        signal = "💎💎💎 ULTRA X3+ BUY"
        sig_class = "signal-ultra"
    elif strength > 76:
        signal = "🔥 STRONG X3 TARGET"
        sig_class = "signal-strong"
    else:
        signal = "🟢 GOOD X3 SCALP"
        sig_class = "signal-strong"

    res = {
        "entry": entry, "signal": signal, "signal_class": sig_class,
        "x3_prob": prob_x3, "conf": conf, "ai_score": ai_score,
        "min": minv, "moy": moy, "max": maxv,
        "strength": strength, "volatility": volatility,
        "real_result": None
    }

    st.session_state.history.append(res)
    if len(st.session_state.history) > 60: st.session_state.history.pop(0)
    st.session_state.ml_ready = True
    return res

# ===================== INTERFACE =====================
st.markdown("<h1 class='main-title'>JETX ANDR V15.2</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00ffcc; font-size:1.65rem;'>ULTRA PUISSANTE • COULEUR TSARA</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    h_in = st.text_input("HASH (Provably Fair)", placeholder="Collez le hash complet...")
    t_in = st.text_input("TIME (HH:MM:SS)", placeholder="Ex: 08:18:48")
    last_cote = st.number_input("LAST COTE", value=2.5, step=0.1, format="%.2f")

    if st.button("🚀 LANCER LE CALCUL ULTRA", use_container_width=True):
        if h_in.strip() and len(t_in.strip()) >= 8:
            with st.spinner("Simulation 98 000x..."):
                st.session_state.last = run_engine_ultra(h_in.strip(), t_in.strip(), last_cote)
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
            <h2 class="{r['signal_class']}">{r['signal']}</h2>
            <h3>X3 PROB : <span style="color:#ff00ff;font-size:2.3rem;">{r['x3_prob']}%</span> | 
                CONF : {r['conf']} | AI : {r['ai_score']}</h3>
            <h1 style="font-size:4.5rem;color:#00ffcc;text-align:center;margin:12px 0;">{r['entry']}</h1>
        </div>
        """, unsafe_allow_html=True)

        # === COULEUR TSARA + MOBILE FRIENDLY ===
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="mini-box res-min"><small>MIN</small><br><b style="font-size:1.6rem;">{r["min"]}</b></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="mini-box res-moy"><small>MOY</small><br><b style="font-size:1.6rem;">{r["moy"]}</b></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="mini-box res-max"><small>MAX</small><br><b style="font-size:1.6rem;">{r["max"]}</b></div>', unsafe_allow_html=True)

        st.markdown(f"""
        **💡 Cashout Strategy :**  
        • MIN → Safe Cashout  
        • MOY → Cashout Normal  
        • MAX → All-in 3x+
        """)
        
        st.markdown(f"**Strength : {r['strength']}** | Volatility : {r['volatility']}")

        col_win, col_loss = st.columns(2)
        with col_win:
            if st.button("✅ WIN", use_container_width=True):
                st.session_state.history[-1]["real_result"] = "win"
                st.rerun()
        with col_loss:
            if st.button("❌ LOSS", use_container_width=True):
                st.session_state.history[-1]["real_result"] = "loss"
                st.rerun()

# Historique
st.markdown("### 📜 Historique")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)[::-1]
    st.data_editor(df, use_container_width=True, hide_index=True)

st.caption("JETX ANDR V15.2 • Couleur Améliorée • Très Ultra Puissante")
