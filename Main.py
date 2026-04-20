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
        .login-title {
            font-size: 4.8rem; font-weight: 900; text-align: center;
            background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .login-subtitle { text-align: center; color: #00ffcc; font-size: 1.6rem; margin-bottom: 40px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='login-title'>JETX ANDR</h1>", unsafe_allow_html=True)
    st.markdown("<p class='login-subtitle'>V14 ULTRA STYLÉ</p>", unsafe_allow_html=True)

    password = st.text_input("🔑 Entrez le mot de passe :", 
                             type="password", 
                             placeholder="••••••••••",
                             label_visibility="hidden")

    if st.button("✅ Accéder à l'application", use_container_width=True):
        if password == "JET2026":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Mot de passe incorrect")
    st.stop()

# ==========================================
# 💎 UI CONFIG & STYLE
# ==========================================
st.set_page_config(page_title="JETX ANDR V14 ULTRA", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a1f 0%, #1a0033 100%); color: #e0fbfc; }
    .main-title {
        font-family: 'Orbitron', sans-serif; font-size: 4.2rem; font-weight: 900; text-align: center;
        background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-shadow: 0 0 35px rgba(0, 255, 204, 0.6); margin-bottom: 8px;
    }
    .glass-card {
        background: rgba(15, 15, 40, 0.82); border: 1px solid rgba(0, 255, 204, 0.55);
        border-radius: 25px; padding: 32px; backdrop-filter: blur(25px);
        box-shadow: 0 10px 45px rgba(0, 255, 204, 0.25);
    }
    .signal-ultra { color: #00ffcc; text-shadow: 0 0 25px #00ffcc; }
    .signal-strong { color: #ff00ff; text-shadow: 0 0 20px #ff00ff; }
    .signal-good  { color: #00ccff; }
    .signal-light { color: #ffff00; }
    .signal-skip  { color: #ff3366; }
    .stButton>button {
        background: linear-gradient(135deg, #00ff88, #ff00ff, #00ccff) !important;
        color: #000 !important; font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important; border-radius: 50px !important; height: 72px !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CORE LOGIC & AI
# ==========================================
if "history" not in st.session_state: st.session_state.history = []
if "ml_clf" not in st.session_state: st.session_state.ml_clf = RandomForestClassifier(n_estimators=250, max_depth=9, random_state=42)
if "ml_reg" not in st.session_state: st.session_state.ml_reg = RandomForestRegressor(n_estimators=180, max_depth=8, random_state=42)
if "ml_ready" not in st.session_state: st.session_state.ml_ready = False
if "scaler" not in st.session_state: st.session_state.scaler = StandardScaler()

def get_time(): return datetime.now(pytz.timezone("Indian/Antananarivo"))

def get_current_streak(history):
    marked = [h.get("real_result") for h in history if h.get("real_result") in ["win", "loss"]]
    if not marked: return 0, 0, None
    s_win = s_loss = 0
    last = marked[-1]
    for res in reversed(marked):
        if res == last:
            if res == "win": s_win += 1
            else: s_loss += 1
        else: break
    return s_win, s_loss, last

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
    X, y = df.iloc[:, :-1], df.iloc[:, -1]
    X_scaled = st.session_state.scaler.fit_transform(X)
    st.session_state.ml_clf.fit(X_scaled, y)
    st.session_state.ml_reg.fit(X_scaled, X.iloc[:, 0])
    st.session_state.ml_ready = True

def ai_predict_ultra(features):
    if not st.session_state.ml_ready: return None
    try:
        X_scaled = st.session_state.scaler.transform(np.array(features).reshape(1, -1))
        p_win = st.session_state.ml_clf.predict_proba(X_scaled)[0][1] * 100
        ref = st.session_state.ml_reg.predict(X_scaled)[0]
        return round(0.65 * p_win + 0.35 * ref, 1)
    except: return None

def run_engine_ultra(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:20], 16)
    np.random.seed(h_num & 0xffffffff)
    lc = min(last_cote, 7.0)
    if lc > 4.8: lc = (lc + 3.0) / 2
    
    sims = np.random.lognormal(np.log(1.18 + (h_num % 950) / 105), 0.34 - (lc * 0.008), 22000)
    prob_x3, moy = round(np.mean(sims >= 3.0) * 100, 1), round(np.mean(sims), 2)
    maxv, minv = round(np.percentile(sims, 95.5), 2), round(np.percentile(sims, 4.5), 2)
    spread = round(maxv - minv, 2)
    conf = round(max(28, min(97, prob_x3 * 0.62 + moy * 17 + lc * 7)), 1)
    
    win_s, loss_s, _ = get_current_streak(st.session_state.history)
    vols = [h.get("moy", 2.5) for h in st.session_state.history[-12:]]
    vol = round(np.std(vols) if len(vols) > 4 else 1.2, 2)
    
    ai_score = ai_predict_ultra([prob_x3, conf, moy, spread, lc, conf, win_s, loss_s, vol])
    strength = round(max(22, min(96, (prob_x3 * 0.53 + (ai_score or conf) * 0.42) + (win_s * 2.1 - loss_s * 2.4) + (vol * 1.8))), 1)

    # Entry Calc
    now = get_time()
    try: base_time = datetime.combine(now.date(), datetime.strptime(t_in.strip(), "%H:%M:%S").time())
    except: base_time = now
    h_int = int(h_hex[:12], 16)
    final_sec = max(18, min(52, int(14 + (h_int % 9) + (spread * 0.45) + ((h_int % 23) - 11) + (8 if prob_x3 > 70 else 0))))
    entry = (base_time + timedelta(seconds=final_sec)).strftime("%H:%M:%S")

    s_map = [(82, "💎💎💎 ULTRA X3+ BUY", "signal-ultra"), (71, "🔥 STRONG X3 TARGET", "signal-strong"), 
             (56, "🟢 GOOD X3 SCALP", "signal-good"), (43, "⚡ LIGHT ENTRY", "signal-light")]
    signal, s_class = next(((s, c) for v, s, c in s_map if strength > v), ("⚠️ SKIP", "signal-skip"))

    res = {"entry": entry, "signal": signal, "signal_class": s_class, "x3_prob": prob_x3, "conf": conf, 
           "moy": moy, "max": maxv, "min": minv, "strength": strength, "win_streak": win_s, 
           "loss_streak": loss_s, "real_result": None, "last_cote_used": lc}
    
    st.session_state.history.append(res)
    if len(st.session_state.history) > 35: st.session_state.history.pop(0)
    train_ai_ultra()
    return res

# ==========================================
# MAIN UI
# ==========================================
st.markdown("<h1 class='main-title'>JETX ANDR V14</h1>", unsafe_allow_html=True)
col1, col2 = st.columns([1, 2.1])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    h_in = st.text_input("HASH", placeholder="Hash...")
    t_in = st.text_input("TIME", placeholder="HH:MM:SS")
    last_cote = st.number_input("LAST COTE", value=2.3)
    if st.button("🚀 LANCER LE CALCUL", use_container_width=True):
        if h_in and len(t_in) >= 8: st.session_state.last = run_engine_ultra(h_in, t_in, last_cote)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.sidebar.button("🔄 RESET ALL DATA"):
        st.session_state.history = []
        if "last" in st.session_state: del st.session_state.last
        st.rerun()

with col2:
    if "last" in st.session_state:
        r = st.session_state.last
        st.markdown(f"""<div class="glass-card">
            <h2 class="{r['signal_class']}">{r['signal']}</h2>
            <h3>X3 PROB : <span style="color:#ff00ff;">{r['x3_prob']}%</span> | CONF : {r['conf']}</h3>
            <h1 style="font-size:4.5rem; color:#00ffcc; text-align:center;">{r['entry']}</h1>
            <p>MIN: {r['min']} | MOY: {r['moy']} | MAX: {r['max']}</p>
            <small>Strength: {r['strength']} | Streak: W:{r['win_streak']} L:{r['loss_streak']}</small>
        </div>""", unsafe_allow_html=True)
        
        cw, cl = st.columns(2)
        if cw.button("✅ WIN", use_container_width=True):
            st.session_state.history[-1]["real_result"] = "win"
            train_ai_ultra(); st.rerun()
        if cl.button("❌ LOSS", use_container_width=True):
            st.session_state.history[-1]["real_result"] = "loss"
            train_ai_ultra(); st.rerun()

if st.session_state.history:
    st.markdown("### 📜 Historique & Apprentissage")
    df = pd.DataFrame(st.session_state.history)[::-1]
    edited = st.data_editor(df, column_config={"real_result": st.column_config.SelectboxColumn("Résultat", options=["win", "loss", None])}, use_container_width=True, hide_index=True)
    
    if st.button("💾 SAUVEGARDER & ENTRAÎNER L'IA"):
        for i, row in edited.iterrows():
            idx = len(st.session_state.history) - 1 - i
            st.session_state.history[idx]["real_result"] = row["real_result"]
        train_ai_ultra(); st.success("IA mise à jour !"); st.rerun()
