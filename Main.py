import streamlit as st
import numpy as np
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import pytz

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# ==========================================
# 🔐 PASSWORD (tsy miseho)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align:center;font-size:4.8rem;background:linear-gradient(90deg,#00ffcc,#ff00ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>JETX ANDR</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#00ffcc;'>V14 ULTRA STYLÉ</h2>", unsafe_allow_html=True)
    pw = st.text_input("🔑 Mot de passe :", type="password", placeholder="••••••••••")
    if st.button("✅ Accéder", use_container_width=True):
        if pw == "JET2026":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect")
    st.stop()

# ==========================================
# UI ULTRA STYLÉE + PREDICTION MATANJAKA
# ==========================================
st.set_page_config(page_title="JETX ANDR V14 ULTRA", layout="wide")

st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #0a0a1f, #1a0033); color:#e0fbfc;}
    .main-title {font-family:'Orbitron'; font-size:4.4rem; font-weight:900; text-align:center;
                 background:linear-gradient(90deg,#00ffcc,#ff00ff,#00ccff); -webkit-background-clip:text;
                 -webkit-text-fill-color:transparent; text-shadow:0 0 40px #00ffcc;}
    .glass-card {background:rgba(15,15,40,0.88); border:1px solid rgba(0,255,204,0.65);
                 border-radius:28px; padding:32px; backdrop-filter:blur(28px);
                 box-shadow:0 15px 50px rgba(0,255,204,0.3);}
    .signal-ultra {color:#00ffcc; text-shadow:0 0 30px #00ffcc; font-size:2rem;}
    .signal-strong {color:#ff00ff; text-shadow:0 0 25px #ff00ff;}
    .history-table {border-radius:20px; overflow:hidden;}
    .stButton>button {background:linear-gradient(135deg,#00ff88,#ff00ff,#00ccff)!important;
                      color:#000!important; font-weight:700; border-radius:50px; height:72px; font-size:1.35rem;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION & FONCTIONS (PREDICTION MATANJAKA)
# ==========================================
if "history" not in st.session_state: st.session_state.history = []
if "ml_clf" not in st.session_state: st.session_state.ml_clf = RandomForestClassifier(n_estimators=300, max_depth=10, random_state=42)
if "ml_reg" not in st.session_state: st.session_state.ml_reg = RandomForestRegressor(n_estimators=200, max_depth=9, random_state=42)
if "ml_ready" not in st.session_state: st.session_state.ml_ready = False
if "scaler" not in st.session_state: st.session_state.scaler = StandardScaler()

def get_time(): return datetime.now(pytz.timezone("Indian/Antananarivo"))

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

def entry_calc_fixed(hash_val, spread, t_in, strength, x3_prob):
    now = get_time()
    try:
        t_obj = datetime.strptime(t_in.strip(), "%H:%M:%S").time()
        base_time = datetime.combine(now.date(), t_obj)
    except:
        base_time = now
    h_int = int(hash_val[:12], 16)
    hash_shift = (h_int % 23) - 11
    base_delay = 14 + (h_int % 9)
    prob_factor = 9 if x3_prob > 72 else (5 if x3_prob > 52 else 1)
    final_seconds = int(base_delay + (spread * 0.42) + hash_shift + prob_factor)
    final_seconds = max(17, min(53, final_seconds))
    base_time = base_time.replace(microsecond=0)
    return (base_time + timedelta(seconds=final_seconds)).strftime("%H:%M:%S")

def run_engine_ultra(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:20], 16)
    np.random.seed(h_num & 0xffffffff)

    last_cote = min(last_cote, 7.0)
    if last_cote > 4.8: last_cote = (last_cote + 3.0) / 2

    # PREDICTION MATANJAKA BE (30 000 simulations)
    base = 1.22 + (h_num % 920) / 98
    sigma = 0.325 - (last_cote * 0.009)
    sims = np.random.lognormal(np.log(base), sigma, 30000)

    prob_x3 = round(np.mean(sims >= 3.0) * 100, 1)
    moy = round(np.mean(sims), 2)
    maxv = round(np.percentile(sims, 96), 2)
    minv = round(np.percentile(sims, 4), 2)
    spread = round(maxv - minv, 2)

    conf = round(max(30, min(98, prob_x3 * 0.65 + moy * 19 + last_cote * 8)), 1)

    win_s, loss_s, _ = get_current_streak(st.session_state.history)
    vols = [h.get("moy", 2.5) for h in st.session_state.history[-12:]]
    volatility = round(np.std(vols) if len(vols) > 4 else 1.2, 2)

    ai_score = ai_predict_ultra([prob_x3, conf, moy, spread, last_cote, conf, win_s, loss_s, volatility])

    base_strength = prob_x3 * 0.56 + (ai_score or conf) * 0.44
    streak_adj = win_s * 2.8 - loss_s * 2.6
    strength = round(base_strength + streak_adj + (volatility * 2.2), 1)
    strength = max(25, min(98, strength))

    entry = entry_calc_fixed(h_hex, spread, t_in, strength, prob_x3)

    if strength > 83:
        signal = "💎💎💎 ULTRA X3+ BUY"
        signal_class = "signal-ultra"
    elif strength > 72:
        signal = "🔥 STRONG X3 TARGET"
        signal_class = "signal-strong"
    elif strength > 58:
        signal = "🟢 GOOD X3 SCALP"
        signal_class = "signal-good"
    elif strength > 44:
        signal = "⚡ LIGHT ENTRY"
        signal_class = "signal-light"
    else:
        signal = "⚠️ SKIP - Low X3 Chance"
        signal_class = "signal-skip"

    res = {
        "entry": entry, "signal": signal, "signal_class": signal_class,
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
# INTERFACE
# ==========================================
st.markdown("<h1 class='main-title'>JETX ANDR V14</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2.1])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    h_in = st.text_input("HASH (Provably Fair)", placeholder="Collez le hash complet...")
    t_in = st.text_input("TIME (HH:MM:SS)", placeholder="Ex: 21:36:16")
    last_cote = st.number_input("LAST COTE", value=2.3, step=0.1, format="%.2f")

    if st.button("🚀 LANCER LE CALCUL ULTRA", use_container_width=True):
        if h_in and len(t_in) >= 8:
            with st.spinner("Simulation 30 000x + IA en cours..."):
                st.session_state.last = run_engine_ultra(h_in, t_in, last_cote)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if "last" in st.session_state:
        r = st.session_state.last
        st.markdown(f"""
        <div class="glass-card">
            <h2 class="{r['signal_class']}">{r['signal']}</h2>
            <h3>X3 PROB : <span style="color:#ff00ff;font-size:2.1rem;">{r['x3_prob']}%</span> | CONF : {r['conf']}</h3>
            <h1 style="font-size:4.6rem;color:#00ffcc;margin:15px 0;">{r['entry']}</h1>
            
            <div style="display:flex; gap:12px; margin:20px 0;">
                <div style="background:#00cc88;color:#000;padding:12px;border-radius:15px;flex:1;text-align:center;">
                    <small>MIN</small><br><b>{r['min']}</b>
                </div>
                <div style="background:#ffcc00;color:#000;padding:12px;border-radius:15px;flex:1;text-align:center;">
                    <small>MOY</small><br><b>{r['moy']}</b>
                </div>
                <div style="background:#ff3366;color:#fff;padding:12px;border-radius:15px;flex:1;text-align:center;">
                    <small>MAX</small><br><b>{r['max']}</b>
                </div>
            </div>

            <p><b>💡 Cashout :</b><br>
            • MIN → cashout voalohany (safe)<br>
            • MOY → cashout mahazatra<br>
            • MAX → cashout amin'ny 3x na mihoatra raha ULTRA</p>
            
            <p style="color:#ff3366;"><b>⚠️ Raha crash amin'ny ora {r['entry']} dia aza miditra intsony!</b></p>
            
            <small>Strength: <b>{r['strength']}</b> | Win Streak: {r['win_streak']} | Loss Streak: {r['loss_streak']}</small>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Marque ce round :**")
        col_win, col_loss = st.columns(2)
        with col_win:
            if st.button("✅ WIN", use_container_width=True):
                if st.session_state.history:
                    st.session_state.history[-1]["real_result"] = "win"
                    st.success("✅ WIN enregistré")
                    st.rerun()
        with col_loss:
            if st.button("❌ LOSS", use_container_width=True):
                if st.session_state.history:
                    st.session_state.history[-1]["real_result"] = "loss"
                    st.success("❌ LOSS enregistré")
                    st.rerun()

# ==========================================
# HISTORIQUE STYLÉ
# ==========================================
st.markdown("### 📜 Historique des Prédictions")
if st.session_state.history:
    df_hist = pd.DataFrame(st.session_state.history)[::-1]
    styled_df = df_hist.style.background_gradient(cmap='RdYlGn', subset=['strength', 'x3_prob'])\
                           .format({'x3_prob': '{:.1f}%', 'strength': '{:.1f}'})
    
    edited_df = st.data_editor(
        styled_df,
        column_config={
            "real_result": st.column_config.SelectboxColumn("✅ Résultat", options=["win", "loss", None]),
            "signal": st.column_config.TextColumn("Signal"),
            "entry": st.column_config.TextColumn("Heure d'entrée"),
            "x3_prob": st.column_config.NumberColumn("X3 %"),
            "strength": st.column_config.NumberColumn("Strength")
        },
        hide_index=True,
        use_container_width=True,
        key="history_styled"
    )

    if st.button("💾 Sauvegarder & Réentraîner l'IA Ultra"):
        for d_idx, row in edited_df.iterrows():
            orig_idx = len(st.session_state.history) - 1 - d_idx
            if orig_idx < len(st.session_state.history):
                st.session_state.history[orig_idx]["real_result"] = row["real_result"]
        train_ai_ultra()
        st.success("✅ IA Ultra mise à jour – prediction encore plus matanjaka!")
        st.rerun()

st.caption("JETX ANDR V14 ULTRA • Prediction 30 000 simulations • Mot de passe protégé")
