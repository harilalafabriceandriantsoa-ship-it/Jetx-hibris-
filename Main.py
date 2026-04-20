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
        .stApp {{ background: linear-gradient(135deg, #0a0a1f, #1a0033); }}
        .login-title {{ font-size: 5rem; font-weight: 900; text-align: center;
                       background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    </style>
    """, unsafe_allow_html=True)
    st.markdown("<h1 class='login-title'>JETX ANDR</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#00ffcc; margin-bottom:40px;'>V14 ULTRA STYLÉ</h2>", unsafe_allow_html=True)
    
    pw = st.text_input("🔑 Entrez le mot de passe :", type="password", placeholder="••••••••••")
    if st.button("✅ Accéder à l'application", use_container_width=True):
        if pw == "JET2026":
            st.session_state.authenticated = True
            st.success("✅ Accès autorisé !")
            st.rerun()
        else:
            st.error("❌ Mot de passe incorrect")
    st.stop()

# ==========================================
# 💎 UI CONFIG & GLOBAL STYLE
# ==========================================
st.set_page_config(page_title="JETX ANDR V14 ULTRA", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    .stApp {{ background: linear-gradient(135deg, #0a0a1f 0%, #1a0033 100%); color: #e0fbfc; }}
    .main-title {{ font-family: 'Orbitron', sans-serif; font-size: 4.5rem; font-weight: 900; text-align: center;
                  background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff, #ffff00);
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                  text-shadow: 0 0 40px rgba(0,255,204,0.7); margin-bottom: 8px; }}
    .glass-card {{ background: rgba(15,15,40,0.88); border: 1px solid rgba(0,255,204,0.65);
                  border-radius: 28px; padding: 32px; backdrop-filter: blur(28px);
                  box-shadow: 0 15px 55px rgba(0,255,204,0.35); }}
    .signal-ultra {{ color: #00ffcc; text-shadow: 0 0 30px #00ffcc; }}
    .signal-strong {{ color: #ff00ff; text-shadow: 0 0 25px #ff00ff; }}
    .stButton>button {{ background: linear-gradient(135deg, #00ff88, #ff00ff, #00ccff) !important;
                       color: #000 !important; font-family: 'Orbitron', sans-serif !important;
                       font-weight: 700 !important; border-radius: 50px !important; height: 72px !important;
                       font-size: 1.4rem !important; box-shadow: 0 0 40px rgba(0,255,204,0.8); }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 AI & SESSION STATE LOGIC
# ==========================================
if "history" not in st.session_state:
    st.session_state.history = []

if "ml_clf" not in st.session_state:
    st.session_state.ml_clf = RandomForestClassifier(n_estimators=300, max_depth=10, random_state=42)
if "ml_reg" not in st.session_state:
    st.session_state.ml_reg = RandomForestRegressor(n_estimators=200, max_depth=9, random_state=42)
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
        vols = [p.get("moy", 2.5) for p in prev[-12:]]
        volatility = round(np.std(vols) if len(vols) > 4 else 1.2, 2)
        features = [h.get("x3_prob", 50), h.get("conf", 50), h.get("moy", 2.5),
                    h.get("spread", 3.0), h.get("last_cote_used", 2.0),
                    h.get("strength", 50), win_s, loss_s, volatility]
        label = 1 if h.get("real_result") == "win" else (1 if h.get("strength", 0) > 68 else 0)
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
        return round(0.68 * prob_win + 0.32 * refined, 1)
    except:
        return None

# ==========================================
# 🛰️ ENGINE X3+ & ENTRY TIME
# ==========================================
def run_engine_ultra(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:20], 16)
    np.random.seed(h_num & 0xffffffff)

    base = 1.48 + (h_num % 780) / 92
    sigma = 0.295 - (last_cote * 0.006)
    sims = np.random.lognormal(np.log(base), sigma, 30000)

    prob_x3 = round(np.mean(sims >= 3.0) * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 96.5), 2)
    minv = round(np.percentile(sims, 3.5), 2)
    spread = round(maxv - minv, 2)

    conf = round(max(35, min(98, prob_x3 * 0.70 + moy * 19 + last_cote * 9)), 1)
    win_s, loss_s, _ = get_current_streak(st.session_state.history)
    vols = [h.get("moy", 2.5) for h in st.session_state.history[-12:]]
    volatility = round(np.std(vols) if len(vols) > 4 else 1.2, 2)

    ai_score = ai_predict_ultra([prob_x3, conf, moy, spread, last_cote, conf, win_s, loss_s, volatility])
    base_strength = prob_x3 * 0.59 + (ai_score or conf) * 0.41
    strength = round(max(28, min(98, base_strength + (win_s * 3.2) - (loss_s * 2.8))), 1)

    now = get_time()
    try:
        t_obj = datetime.strptime(t_in.strip(), "%H:%M:%S").time()
        base_time = datetime.combine(now.date(), t_obj)
    except:
        base_time = now

    h_int = int(h_hex[:14], 16)
    final_seconds = int(22 + (h_int % 18) + (strength / 12))
    entry = (base_time + timedelta(seconds=final_seconds)).strftime("%H:%M:%S")

    s_class = "signal-ultra" if strength > 83 else "signal-strong"
    signal = "💎 ULTRA X3+ BUY" if strength > 83 else "🔥 STRONG X3 TARGET"

    res = {
        "entry": entry, "signal": signal, "signal_class": s_class,
        "x3_prob": prob_x3, "conf": conf, "moy": moy, "max": maxv, "min": minv,
        "strength": strength, "win_streak": win_s, "volatility": volatility,
        "real_result": None
    }
    st.session_state.history.append(res)
    train_ai_ultra()
    return res

# ==========================================
# 🖥️ INTERFACE MAIN
# ==========================================
st.markdown("<h1 class='main-title'>JETX ANDR V14</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00ffcc; font-size:1.6rem;'>ULTRA STYLÉ • X3+ CIBLÉ • ENTRY ULTRA PUISSANTE</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2.1])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    h_in = st.text_input("HASH (Provably Fair)")
    t_in = st.text_input("TIME (HH:MM:SS)", placeholder="Ex: 22:07:55")
    last_c = st.number_input("LAST COTE", value=2.0)
    if st.button("🚀 LANCER LE CALCUL ULTRA", use_container_width=True):
        if h_in and t_in:
            with st.spinner("Processing Neural Data..."):
                st.session_state.last = run_engine_ultra(h_in, t_in, last_c)
    
    if st.sidebar.button("🔄 Reset Data"):
        st.session_state.history = []
        if "last" in st.session_state: del st.session_state.last
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if "last" in st.session_state:
        r = st.session_state.last
        # NY STYLE VOAHITSY TSY MISY ERROR
        st.markdown(f"""
        <div class="glass-card">
            <h2 class="{r['signal_class']}" style="text-align:center;">{r['signal']}</h2>
            <h3 style="text-align:center;">X3 PROB : <span style="color:#ff00ff;font-size:2.1rem;">{r['x3_prob']}%</span> | CONF : {r['conf']}</h3>
            <h1 style="font-size:4.6rem;color:#00ffcc;margin:15px 0;text-align:center;font-family:Orbitron;">{r['entry']}</h1>
            
            <div style="display:flex; gap:12px; margin:20px 0;">
                <div style="background:#00cc88;color:#000;padding:14px;border-radius:15px;flex:1;text-align:center;">
                    <small>MIN</small><br><b style="font-size:1.5rem;">{r['min']}</b>
                </div>
                <div style="background:#ffcc00;color:#000;padding:14px;border-radius:15px;flex:1;text-align:center;">
                    <small>MOY</small><br><b style="font-size:1.5rem;">{r['moy']}</b>
                </div>
                <div style="background:#ff3366;color:#fff;padding:14px;border-radius:15px;flex:1;text-align:center;">
                    <small>MAX</small><br><b style="font-size:1.5rem;">{r['max']}</b>
                </div>
            </div>

            <p><b>💡 Cashout :</b><br>
            • MIN → cashout voalohany (safe)<br>
            • MOY → cashout mahazatra<br>
            • MAX → cashout amin'ny 3x na mihoatra raha ULTRA</p>
            
            <p style="color:#ff3366; font-weight:bold; text-align:center;">
                ⚠️ Raha crash amin'ny ora {r['entry']} dia aza miditra intsony!
            </p>
            
            <div style="margin-top:20px; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px; display:flex; justify-content:space-between; opacity:0.8;">
                <small>Strength: <b>{r['strength']}</b></small>
                <small>Win Streak: <b>{r['win_streak']}</b></small>
                <small>Volatility: <b>{r['volatility']}</b></small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Win/Loss Buttons
        c_w, c_l = st.columns(2)
        with c_w:
            if st.button("✅ WIN", use_container_width=True):
                st.session_state.history[-1]["real_result"] = "win"
                st.rerun()
        with c_l:
            if st.button("❌ LOSS", use_container_width=True):
                st.session_state.history[-1]["real_result"] = "loss"
                st.rerun()

# Historique
st.markdown("### 📜 Historique des Prédictions")
if st.session_state.history:
    df_hist = pd.DataFrame(st.session_state.history)[::-1]
    st.dataframe(df_hist[["entry", "signal", "x3_prob", "strength", "real_result"]], use_container_width=True)

st.caption("JETX ANDR V14 ULTRA • Optimized for Pydroid & Streamlit • AI Powered")
