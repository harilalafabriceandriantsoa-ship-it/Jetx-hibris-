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
    st.markdown("<h1 style='text-align:center; font-size:4.8rem; background:linear-gradient(90deg,#00ffcc,#ff00ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>JETX ANDR</h1>", unsafe_allow_html=True)
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
# UI STYLÉE
# ==========================================
st.set_page_config(page_title="JETX ANDR V14 ULTRA", layout="wide")

st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #0a0a1f, #1a0033); color:#e0fbfc;}
    .main-title {font-family:'Orbitron'; font-size:4.3rem; font-weight:900; text-align:center;
                 background:linear-gradient(90deg,#00ffcc,#ff00ff,#00ccff); -webkit-background-clip:text;
                 -webkit-text-fill-color:transparent; text-shadow:0 0 35px #00ffcc;}
    .glass-card {background:rgba(15,15,40,0.85); border:1px solid rgba(0,255,204,0.6);
                 border-radius:25px; padding:30px; backdrop-filter:blur(25px);
                 box-shadow:0 10px 45px rgba(0,255,204,0.3);}
    .signal-ultra {color:#00ffcc; text-shadow:0 0 25px #00ffcc;}
    .signal-strong {color:#ff00ff; text-shadow:0 0 20px #ff00ff;}
    .stButton>button {background:linear-gradient(135deg,#00ff88,#ff00ff,#00ccff)!important;
                      color:#000!important; font-weight:700; border-radius:50px; height:70px;}
</style>
""", unsafe_allow_html=True)

# Session & fonctions (tsis y ovaina)
if "history" not in st.session_state: st.session_state.history = []
if "ml_clf" not in st.session_state: st.session_state.ml_clf = RandomForestClassifier(n_estimators=250, max_depth=9, random_state=42)
if "ml_reg" not in st.session_state: st.session_state.ml_reg = RandomForestRegressor(n_estimators=180, max_depth=8, random_state=42)
if "ml_ready" not in st.session_state: st.session_state.ml_ready = False
if "scaler" not in st.session_state: st.session_state.scaler = StandardScaler()

def get_time(): return datetime.now(pytz.timezone("Indian/Antananarivo"))

# ... (streak, ai, entry_calc, run_engine functions mitovy amin'ny teo aloha - tsy voasoratra intsony mba tsy lava)

# ==========================================
# MAIN UI
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
            with st.spinner("Calcul en cours..."):
                st.session_state.last = run_engine_ultra(h_in, t_in, last_cote)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if "last" in st.session_state:
        r = st.session_state.last
        st.markdown(f"""
        <div class="glass-card">
            <h2 class="{r['signal_class']}">{r['signal']}</h2>
            <h3>X3 PROB : <span style="color:#ff00ff;font-size:2rem;">{r['x3_prob']}%</span> | CONF : {r['conf']}</h3>
            <h1 style="font-size:4.5rem;color:#00ffcc;margin:15px 0;">{r['entry']}</h1>
            
            <div style="display:flex; gap:10px; margin:15px 0;">
                <div style="background:#00cc88; color:#000; padding:10px; border-radius:12px; flex:1; text-align:center;">
                    <small>MIN</small><br><b>{r['min']}</b>
                </div>
                <div style="background:#ffcc00; color:#000; padding:10px; border-radius:12px; flex:1; text-align:center;">
                    <small>MOY</small><br><b>{r['moy']}</b>
                </div>
                <div style="background:#ff3366; color:#fff; padding:10px; border-radius:12px; flex:1; text-align:center;">
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

        # Bouton WIN / LOSS stylé
        st.markdown("**Marque ce round :**")
        col_win, col_loss = st.columns(2)
        with col_win:
            if st.button("✅ WIN", use_container_width=True):
                if st.session_state.history:
                    st.session_state.history[-1]["real_result"] = "win"
                    st.success("✅ Marqué WIN")
                    st.rerun()
        with col_loss:
            if st.button("❌ LOSS", use_container_width=True):
                if st.session_state.history:
                    st.session_state.history[-1]["real_result"] = "loss"
                    st.success("❌ Marqué LOSS")
                    st.rerun()

# Historique (mbola misy)
st.markdown("### 📜 Historique complet")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)[::-1]
    edited = st.data_editor(df, column_config={"real_result": st.column_config.SelectboxColumn("Résultat", options=["win","loss",None])}, use_container_width=True)
    if st.button("💾 Sauvegarder & Réentraîner IA"):
        for i, row in edited.iterrows():
            orig_i = len(st.session_state.history) - 1 - i
            st.session_state.history[orig_i]["real_result"] = row["real_result"]
        train_ai_ultra()
        st.success("IA mise à jour !")
        st.rerun()

st.caption("JETX ANDR V14 ULTRA • Mot de passe protégé")
