import streamlit as st
import numpy as np
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import pytz
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import time

# ==========================================
# 🔐 PASSWORD PROTECTION
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #0a0a1f, #1a0033); }
        .login-title { font-size: 4.5rem; font-weight: 900; text-align: center;
                       background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       font-family: 'Orbitron', sans-serif; }
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
# 💎 UI TRÈS STYLÉE (Custom CSS)
# ==========================================
st.set_page_config(page_title="JETX ANDR V14 ULTRA", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a1f 0%, #1a0033 100%); color: #e0fbfc; }
    .main-title { font-family: 'Orbitron', sans-serif; font-size: 4.2rem; font-weight: 900; text-align: center;
                  background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff, #ffff00);
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                  text-shadow: 0 0 40px rgba(0,255,204,0.7); margin-bottom: 8px; }
    .glass-card { background: rgba(15,15,40,0.88); border: 1px solid rgba(0,255,204,0.65);
                  border-radius: 28px; padding: 32px; backdrop-filter: blur(28px);
                  box-shadow: 0 15px 55px rgba(0,255,204,0.35); margin-bottom: 20px; }
    
    /* Signals Colors */
    .signal-ultra { color: #ff00ff; text-shadow: 0 0 30px #ff00ff; font-weight: bold; }
    .signal-strong { color: #00ffcc; text-shadow: 0 0 25px #00ffcc; font-weight: bold; }
    .signal-good { color: #ffff00; font-weight: bold; }
    .signal-light { color: #00ccff; font-weight: bold; }
    .signal-skip { color: #ff4444; font-weight: bold; }

    .stButton>button { background: linear-gradient(135deg, #00ff88, #ff00ff, #00ccff) !important;
                       color: #000 !important; font-family: 'Orbitron', sans-serif !important;
                       font-weight: 700 !important; border-radius: 50px !important; height: 60px !important;
                       font-size: 1.2rem !important; box-shadow: 0 0 30px rgba(0,255,204,0.6); margin-top:10px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 MACHINE LEARNING LOGIC
# ==========================================
if "history" not in st.session_state:
    st.session_state.history = []

# Initialize ML Models
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
# 🚀 ULTRA CORE ENGINE (X3+)
# ==========================================
def run_engine_ultra(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:20], 16)
    np.random.seed(h_num & 0xffffffff)

    last_cote_limit = min(last_cote, 7.0)
    if last_cote_limit > 4.8:
        last_cote_limit = (last_cote_limit + 3.0) / 2

    base = 1.52 + (h_num % 780) / 92
    sigma = 0.29 - (last_cote_limit * 0.006)

    sims = np.random.lognormal(np.log(base), sigma, 30000)

    prob_x3 = round(np.mean(sims >= 3.0) * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 96.5), 2)
    minv = round(np.percentile(sims, 3.5), 2)
    spread = round(maxv - minv, 2)

    conf = round(max(35, min(98, prob_x3 * 0.70 + moy * 19 + last_cote_limit * 9)), 1)

    win_s, loss_s, _ = get_current_streak(st.session_state.history)
    vols = [h.get("moy", 2.5) for h in st.session_state.history[-12:]]
    volatility = round(np.std(vols) if len(vols) > 4 else 1.2, 2)

    ai_score = ai_predict_ultra([prob_x3, conf, moy, spread, last_cote_limit, conf, win_s, loss_s, volatility])

    base_strength = prob_x3 * 0.59 + (ai_score or conf) * 0.41
    streak_adj = win_s * 3.2 - loss_s * 2.8
    strength = round(base_strength + streak_adj + (volatility * 2.5), 1)
    strength = max(28, min(98, strength))

    now = get_time()
    try:
        t_obj = datetime.strptime(t_in.strip(), "%H:%M:%S").time()
        base_time = datetime.combine(now.date(), t_obj)
    except:
        base_time = now

    h_int = int(h_hex[:14], 16)
    hash_shift = (h_int % 29) - 14
    base_delay = 15 + (h_int % 12)
    prob_factor = 13 if prob_x3 > 78 else (8 if prob_x3 > 60 else 3)
    strength_factor = 5 if strength > 82 else (3 if strength > 68 else 1)

    final_seconds = int(base_delay + (spread * 0.35) + hash_shift + prob_factor + strength_factor)
    final_seconds = max(18, min(58, final_seconds))

    base_time = base_time.replace(microsecond=0)
    entry_time = (base_time + timedelta(seconds=final_seconds)).strftime("%H:%M:%S")

    if strength > 83:
        signal, s_class = "💎💎💎 ULTRA X3+ BUY", "signal-ultra"
    elif strength > 72:
        signal, s_class = "🔥 STRONG X3 TARGET", "signal-strong"
    elif strength > 58:
        signal, s_class = "🟢 GOOD X3 SCALP", "signal-good"
    elif strength > 44:
        signal, s_class = "⚡ LIGHT ENTRY", "signal-light"
    else:
        signal, s_class = "⚠️ SKIP - Low X3 Chance", "signal-skip"

    res = {
        "entry": entry_time, "signal": signal, "signal_class": s_class,
        "x3_prob": prob_x3, "conf": conf, "moy": moy, "max": maxv, "min": minv,
        "spread": spread, "last_cote_used": round(last_cote, 2),
        "ai_score": ai_score, "strength": strength,
        "win_streak": win_s, "loss_streak": loss_s, "volatility": volatility,
        "real_result": None
    }

    st.session_state.history.append(res)
    if len(st.session_state.history) > 40: st.session_state.history.pop(0)
    train_ai_ultra()
    return res

# ==========================================
# 🖥️ MAIN INTERFACE
# ==========================================
st.markdown("<h1 class='main-title'>JETX ANDR V14</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00ffcc; font-size:1.4rem; font-family:Rajdhani;'>ULTRA STYLÉ • X3+ CIBLÉ • ENTRY ULTRA PUISSANTE</p>", unsafe_allow_html=True)

col_input, col_res = st.columns([1, 2.1])

with col_input:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 🛰️ CONFIGURATION")
    h_in = st.text_input("HASH (Provably Fair)", placeholder="Paste hash here...")
    t_in = st.text_input("TIME (HH:MM:SS)", placeholder="Ex: 22:08:20")
    last_val = st.number_input("LAST COTE", value=2.3, step=0.1, format="%.2f")

    if st.button("🚀 LANCER LE CALCUL ULTRA", use_container_width=True):
        if h_in and len(t_in) >= 8:
            with st.spinner("Processing neural links..."):
                st.session_state.last = run_engine_ultra(h_in, t_in, last_val)
        else:
            st.error("Format Hash na Lera diso!")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.sidebar.button("🔄 Reset All Data"):
        st.session_state.history = []
        if "last" in st.session_state: del st.session_state.last
        st.rerun()

with col_res:
    if "last" in st.session_state:
        r = st.session_state.last
        st.markdown(f"""
        <div class="glass-card">
            <h2 class="{r['signal_class']}">{r['signal']}</h2>
            <h3 style="font-family:Rajdhani;">X3 PROB : <span style="color:#ff00ff;font-size:2.1rem;">{r['x3_prob']}%</span> | CONF : {r['conf']}%</h3>
            <h1 style="font-size:5rem;color:#00ffcc;margin:10px 0; font-family:Orbitron; text-align:center;">{r['entry']}</h1>
            
            <div style="display:flex; gap:12px; margin:20px 0;">
                <div style="background:#00cc88;color:#000;padding:14px;border-radius:15px;flex:1;text-align:center;">
                    <small>MIN (Safe)</small><br><b style="font-size:1.5rem;">{r['min']}</b>
                </div>
                <div style="background:#ffcc00;color:#000;padding:14px;border-radius:15px;flex:1;text-align:center;">
                    <small>MOYENNE</small><br><b style="font-size:1.5rem;">{r['moy']}</b>
                </div>
                <div style="background:#ff3366;color:#fff;padding:14px;border-radius:15px;flex:1;text-align:center;">
                    <small>MAX (X3+)</small><br><b style="font-size:1.5rem;">{r['max']}</b>
                </div>
            </div>

            <div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:15px;">
                <p style="margin-bottom:5px;"><b>💡 Cashout Strategies :</b></p>
                <small>• MIN → Cashout voalohany mba tsy ho resy.</small><br>
                <small>• MOY → Tanjona mahazatra (Moderate risk).</small><br>
                <small>• MAX → Cashout amin'ny 3x na mihoatra raha ULTRA ny signal.</small>
            </div>
            
            <p style="color:#ff3366; margin-top:15px; text-align:center;">
                <b>⚠️ Raha vao crash amin'ny {r['entry']} dia aza miditra intsony!</b>
            </p>
            <hr style="opacity:0.2;">
            <div style="display:flex; justify-content:space-between; font-size:0.8rem; opacity:0.8;">
                <span>Strength: <b>{r['strength']}</b></span>
                <span>Win Streak: {r['win_streak']}</span>
                <span>Volatility: {r['volatility']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Marque ce round :**")
        c_w, c_l = st.columns(2)
        with c_w:
            if st.button("✅ WIN", use_container_width=True):
                if st.session_state.history:
                    st.session_state.history[-1]["real_result"] = "win"
                    st.toast("Result saved: WIN")
                    st.rerun()
        with c_l:
            if st.button("❌ LOSS", use_container_width=True):
                if st.session_state.history:
                    st.session_state.history[-1]["real_result"] = "loss"
                    st.toast("Result saved: LOSS")
                    st.rerun()

# ==========================================
# 📂 HISTORY & RETRAINING
# ==========================================
st.markdown("---")
st.markdown("### 📜 Historique des Prédictions")
if st.session_state.history:
    df_hist = pd.DataFrame(st.session_state.history)[::-1]
    
    # Cleaning columns for display
    display_cols = ["entry", "signal", "x3_prob", "strength", "moy", "real_result"]
    
    edited_df = st.data_editor(
        df_hist[display_cols],
        column_config={
            "real_result": st.column_config.SelectboxColumn("✅ Résultat", options=["win", "loss", None]),
            "signal": st.column_config.TextColumn("Signal"),
            "entry": st.column_config.TextColumn("Heure d'entrée"),
            "x3_prob": st.column_config.NumberColumn("X3 %", format="%.1f%%"),
            "strength": st.column_config.NumberColumn("Strength", format="%.1f"),
            "moy": st.column_config.NumberColumn("MOY")
        },
        hide_index=True,
        use_container_width=True,
        key="history_editor"
    )

    if st.button("💾 Sauvegarder & Réentraîner l'IA Ultra"):
        # Map edits back to session state
        for d_idx, row in edited_df.iterrows():
            orig_idx = len(st.session_state.history) - 1 - d_idx
            if 0 <= orig_idx < len(st.session_state.history):
                st.session_state.history[orig_idx]["real_result"] = row["real_result"]
        train_ai_ultra()
        st.success("✅ IA mise à jour – X3+ ultra ciblé!")
        time.sleep(1)
        st.rerun()

st.caption("JETX ANDR V14 ULTRA • Engineered for X3+ Targets • AI-Powered Entry Points")
