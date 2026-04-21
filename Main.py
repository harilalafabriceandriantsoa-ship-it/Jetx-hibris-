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
        .login-title { font-size: 5rem; font-weight: 900; text-align: center;
                       background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("<h1 class='login-title'>JETX ANDR</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#00ffcc; margin-bottom:40px;'>V14 ULTRA STYLÉ</h2>", unsafe_allow_html=True)
    
    pw = st.text_input("🔑 Entrez le mot de passe :", type="password")
    if st.button("✅ Accéder à l'application", use_container_width=True):
        if pw == "JET2026":
            st.session_state.authenticated = True
            st.success("✅ Accès autorisé !")
            st.rerun()
        else:
            st.error("❌ Mot de passe incorrect")
    st.stop()

# ==========================================
# 💎 UI + CSS CORRIGÉ
# ==========================================
st.set_page_config(page_title="JETX ANDR V14 ULTRA", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0a1f 0%, #1a0033 100%); color: #e0fbfc; }
    .main-title { font-family: 'Orbitron', sans-serif; font-size: 4.5rem; font-weight: 900; text-align: center;
                  background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff, #ffff00);
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                  text-shadow: 0 0 40px rgba(0,255,204,0.7); margin-bottom: 8px; }
    .glass-card { background: rgba(15,15,40,0.88); border: 1px solid rgba(0,255,204,0.65);
                  border-radius: 28px; padding: 32px; backdrop-filter: blur(28px);
                  box-shadow: 0 15px 55px rgba(0,255,204,0.35); }
    
    .signal-ultra { color: #00ffcc; text-shadow: 0 0 30px #00ffcc; }
    .signal-strong { color: #ff00ff; text-shadow: 0 0 25px #ff00ff; }
    .signal-good { color: #00ff88; text-shadow: 0 0 25px #00ff88; }
    .signal-light { color: #ffff00; text-shadow: 0 0 20px #ffff00; }
    .signal-skip { color: #ff6666; text-shadow: 0 0 20px #ff6666; }
    
    .stButton>button { background: linear-gradient(135deg, #00ff88, #ff00ff, #00ccff) !important;
                       color: #000 !important; font-family: 'Orbitron', sans-serif !important;
                       font-weight: 700 !important; border-radius: 50px !important; height: 72px !important;
                       font-size: 1.4rem !important; box-shadow: 0 0 40px rgba(0,255,204,0.8); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE
# ==========================================
if "history" not in st.session_state:
    st.session_state.history = []
if "last" not in st.session_state:
    st.session_state.last = None

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

# (Les autres fonctions restent identiques : get_current_streak, prepare_ml_data, train_ai_ultra, ai_predict_ultra, run_engine_ultra)
# Je ne les recopie pas ici pour gagner de la place, garde exactement les mêmes que tu avais.

# ==========================================
# CALCUL (inchangé)
# ==========================================
def run_engine_ultra(h_in, t_in, last_cote):
    # ... tout ton code de run_engine_ultra reste IDENTIQUE ...
    # (je ne le recopie pas, garde-le tel quel)
    pass  # ← Remplace par ton ancienne fonction complète

# ==========================================
# INTERFACE
# ==========================================
st.markdown("<h1 class='main-title'>JETX ANDR V14</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00ffcc; font-size:1.6rem;'>ULTRA STYLÉ • X3+ CIBLÉ • ENTRY ULTRA PUISSANTE</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2.1])

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    h_in = st.text_input("HASH (Provably Fair)", placeholder="Collez le hash complet...")
    t_in = st.text_input("TIME (HH:MM:SS)", placeholder="Ex: 07:53:28")
    last_cote = st.number_input("LAST COTE", value=2.3, step=0.1, format="%.2f")

    if st.button("🚀 LANCER LE CALCUL ULTRA", use_container_width=True):
        if h_in.strip() and len(t_in.strip()) >= 8:
            with st.spinner("Simulation X3+ 40 000x ultra puissante..."):
                try:
                    result = run_engine_ultra(h_in.strip(), t_in.strip(), last_cote)
                    st.session_state.last = result
                    st.success("✅ Calcul terminé !")
                except Exception as e:
                    st.error(f"Erreur calcul : {e}")
        else:
            st.warning("Veuillez remplir Hash et Time correctement")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.sidebar.button("🔄 Reset All Data"):
        st.session_state.history = []
        st.session_state.last = None
        st.rerun()

# ==================== AFFICHAGE RÉSULTATS ====================
with col2:
    if st.session_state.last:
        r = st.session_state.last
        st.markdown(f"""
        <div class="glass-card">
            <h2 class="{r.get('signal_class', 'signal-strong')}">{r.get('signal', 'Signal')}</h2>
            <h3>X3 PROB : <span style="color:#ff00ff;font-size:2.1rem;">{r.get('x3_prob', 0)}%</span> | 
                CONF : {r.get('conf', 0)} | AI : {r.get('ai_score', 'N/A')}</h3>
            <h1 style="font-size:4.6rem;color:#00ffcc;margin:15px 0;">{r.get('entry', '--:--:--')}</h1>
            
            <div style="display:flex; gap:12px; margin:20px 0;">
                <div style="background:#00cc88;color:#000;padding:14px;border-radius:15px;flex:1;text-align:center;">
                    <small>MIN</small><br><b>{r.get('min', 0)}</b>
                </div>
                <div style="background:#ffcc00;color:#000;padding:14px;border-radius:15px;flex:1;text-align:center;">
                    <small>MOY</small><br><b>{r.get('moy', 0)}</b>
                </div>
                <div style="background:#ff3366;color:#fff;padding:14px;border-radius:15px;flex:1;text-align:center;">
                    <small>MAX</small><br><b>{r.get('max', 0)}</b>
                </div>
            </div>

            <p><b>💡 Cashout :</b><br>
            • MIN → cashout voalohany (safe)<br>
            • MOY → cashout mahazatra<br>
            • MAX → cashout amin'ny 3x na mihoatra</p>
            
            <p style="color:#ff3366;"><b>⚠️ Raha crash amin'ny ora {r.get('entry')} dia aza miditra intsony!</b></p>
            
            <small>Strength: <b>{r.get('strength', 0)}</b> | Win Streak: {r.get('win_streak', 0)} | Loss Streak: {r.get('loss_streak', 0)}</small>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Marque ce round :**")
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

# Historique (inchangé)
st.markdown("### 📜 Historique des Prédictions")
if st.session_state.history:
    df_hist = pd.DataFrame(st.session_state.history)[::-1]
    edited_df = st.data_editor(
        df_hist,
        column_config={
            "real_result": st.column_config.SelectboxColumn("✅ Résultat", options=["win", "loss", None]),
            "entry": st.column_config.TextColumn("Heure"),
            "x3_prob": st.column_config.NumberColumn("X3 %", format="%.1f"),
            "strength": st.column_config.NumberColumn("Strength", format="%.1f"),
            "moy": st.column_config.NumberColumn("MOY"),
        },
        hide_index=True,
        use_container_width=True
    )

    if st.button("💾 Sauvegarder & Réentraîner l'IA"):
        for d_idx, row in edited_df.iterrows():
            orig_idx = len(st.session_state.history) - 1 - d_idx
            if 0 <= orig_idx < len(st.session_state.history):
                st.session_state.history[orig_idx]["real_result"] = row["real_result"]
        train_ai_ultra()
        st.success("✅ IA mise à jour !")
        st.rerun()

st.caption("JETX ANDR V14 ULTRA • Fixé & Amélioré")
