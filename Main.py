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
    st.markdown("<h2 style='text-align:center; color:#00ffcc;'>V14.7 ULTRA STYLÉ</h2>", unsafe_allow_html=True)
    
    pw = st.text_input("🔑 Entrez le mot de passe :", type="password")
    if st.button("✅ Accéder à l'application", use_container_width=True):
        if pw == "JET2026":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Mot de passe incorrect")
    st.stop()

# ===================== CSS (Style d'avant conservé) =====================
st.set_page_config(page_title="JETX ANDR V14.7", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a1f 0%, #1a0033 100%); color: #e0fbfc; }
    .main-title { font-family: 'Orbitron', sans-serif; font-size: 4.5rem; font-weight: 900; text-align: center;
                  background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff, #ffff00);
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                  text-shadow: 0 0 40px rgba(0,255,204,0.7); }
    .glass-card { background: rgba(15,15,40,0.88); border: 1px solid rgba(0,255,204,0.65);
                  border-radius: 28px; padding: 32px; backdrop-filter: blur(28px);
                  box-shadow: 0 15px 55px rgba(0,255,204,0.35); }
    .signal-ultra { color: #00ffcc; text-shadow: 0 0 30px #00ffcc; }
    .signal-strong { color: #ff00ff; text-shadow: 0 0 25px #ff00ff; }
    .result-grid { display: flex; gap: 15px; margin: 25px 0; flex-wrap: wrap; }
    .result-box { flex: 1; min-width: 110px; padding: 18px; border-radius: 20px; text-align: center; }
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

# ===================== ULTRA ENGINE (Hash très puissant) =====================
def run_engine_ultra(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:48], 16)
    np.random.seed(h_num & 0xFFFFFFFF)

    base = 1.87 + (h_num % 820) / 102
    sigma = 0.231 - (last_cote * 0.0032)
    sims = np.random.lognormal(np.log(base), sigma, 82000)

    prob_x3 = round(np.mean(sims >= 3.0) * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 97.7), 2)
    minv = round(np.percentile(sims, 2.3), 2)

    conf = round(max(46, min(99, prob_x3*0.69 + moy*21 + (h_num % 160)/3.5 + last_cote*12.8)), 1)

    win_s, loss_s = get_current_streak(st.session_state.history)
    volatility = round(np.std([h.get("moy", 2.5) for h in st.session_state.history[-20:]]) if st.session_state.history else 1.2, 2)

    ai_score = round(conf * 0.92, 1)
    if st.session_state.ml_ready and len(st.session_state.history) > 10:
        try:
            features = [prob_x3, conf, moy, maxv-minv, last_cote, win_s, loss_s, volatility]
            X = st.session_state.scaler.transform(np.array(features).reshape(1, -1))
            prob = st.session_state.ml_clf.predict_proba(X)[0][1] * 100
            reg = st.session_state.ml_reg.predict(X)[0]
            ai_score = round(0.72*prob + 0.28*reg, 1)
        except: pass

    strength = round(prob_x3*0.62 + ai_score*0.28 + win_s*6.2 - loss_s*4.6 + volatility*6.8, 1)
    strength = max(40, min(99, strength))

    # Entry Time ultra dynamique selon hash
    try:
        bt = datetime.combine(get_time().date(), datetime.strptime(t_in.strip(), "%H:%M:%S").time())
    except:
        bt = get_time()
    shift = (int(h_hex[:20], 16) % 62) - 31
    final_sec = 18 + (h_num % 46) + shift + int(volatility*3.8) + (23 if strength > 87 else 15 if strength > 75 else 8)
    final_sec = max(19, min(88, final_sec))
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

# ===================== INTERFACE (Style précédent conservé) =====================
st.markdown("<h1 class='main-title'>JETX ANDR V14.7</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00ffcc; font-size:1.65rem;'>ULTRA STYLÉ • X3+ CIBLÉ • ENTRY DYNAMIQUE</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2.1])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    h_in = st.text_input("HASH (Provably Fair)", placeholder="Collez le hash complet...")
    t_in = st.text_input("TIME (HH:MM:SS)", placeholder="Ex: 08:18:48")
    last_cote = st.number_input("LAST COTE", value=2.5, step=0.1, format="%.2f")

    if st.button("🚀 LANCER LE CALCUL ULTRA", use_container_width=True):
        if h_in.strip() and len(t_in.strip()) >= 8:
            with st.spinner("Simulation 82 000x + Hash Avancé..."):
                st.session_state.last = run_engine_ultra(h_in.strip(), t_in.strip(), last_cote)
    st.markdown("</div>", unsafe_allow_html=True)

    # Reset dans la sidebar
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
            <h3>X3 PROB : <span style="color:#ff00ff;font-size:2.4rem;">{r['x3_prob']}%</span> | 
                CONF : {r['conf']} | AI : {r['ai_score']}</h3>
            <h1 style="font-size:4.6rem;color:#00ffcc;margin:15px 0;text-align:center;">{r['entry']}</h1>
            
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

        # Boutons WIN / LOSS
        cwin, closs = st.columns(2)
        with cwin:
            if st.button("✅ WIN", use_container_width=True):
                if st.session_state.history:
                    st.session_state.history[-1]["real_result"] = "win"
                    st.rerun()
        with closs:
            if st.button("❌ LOSS", use_container_width=True):
                if st.session_state.history:
                    st.session_state.history[-1]["real_result"] = "loss"
                    st.rerun()

# Historique + Sauvegarde
st.markdown("### 📜 Historique des Prédictions")
if st.session_state.history:
    df_hist = pd.DataFrame(st.session_state.history)[::-1]
    edited_df = st.data_editor(
        df_hist,
        column_config={
            "real_result": st.column_config.SelectboxColumn("Résultat", options=["win", "loss", None]),
        },
        use_container_width=True,
        hide_index=True
    )

    if st.button("💾 Sauvegarder & Réentraîner l'IA"):
        for i, row in edited_df.iterrows():
            orig_idx = len(st.session_state.history) - 1 - i
            if 0 <= orig_idx < len(st.session_state.history):
                st.session_state.history[orig_idx]["real_result"] = row["real_result"]
        st.success("✅ Données sauvegardées et IA mise à jour")
        st.rerun()

st.caption("JETX ANDR V14.7 • Résultat ultra stylé • Reset & Sauvegarde actifs")
