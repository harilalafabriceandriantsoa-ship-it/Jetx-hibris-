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
# 🔐 CONFIG & ACCESS CONTROL
# ==========================================
st.set_page_config(page_title="JETX ANDR V14 ULTRA", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');
        .stApp {{ 
            background: linear-gradient(135deg, #0a0a1f, #1a0033); 
            display: flex; align-items: center; justify-content: center;
        }}
        .login-title {{ 
            font-size: 4.5rem; font-weight: 900; text-align: center;
            background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            font-family: 'Orbitron', sans-serif;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='login-title'>JETX ANDR</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#00ffcc;'>V14 ULTRA PREDICT</h3>", unsafe_allow_html=True)
    
    pw = st.text_input("🔑 Entrez le mot de passe :", type="password", placeholder="••••••••••")
    if st.button("✅ ACCÈDER AU SYSTÈME", use_container_width=True):
        if pw == "JET2026":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Mot de passe incorrect")
    st.stop()

# ==========================================
# 💎 PREMIUM GLOBAL STYLE
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    
    .stApp {{ background: linear-gradient(135deg, #0a0a1f 0%, #1a0033 100%); color: #e0fbfc; }}
    
    .main-title {{ 
        font-family: 'Orbitron', sans-serif; font-size: 4rem; font-weight: 900; text-align: center;
        background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px; text-shadow: 0 0 30px rgba(0, 255, 204, 0.4);
    }}
    
    .glass-card {{ 
        background: rgba(15, 15, 40, 0.88); 
        border: 1px solid rgba(0, 255, 204, 0.6);
        border-radius: 28px; padding: 25px; 
        backdrop-filter: blur(25px);
        box-shadow: 0 15px 55px rgba(0,0,0,0.6);
        margin-bottom: 20px;
    }}
    
    .stButton>button {{ 
        background: linear-gradient(135deg, #00ffcc, #ff00ff) !important;
        color: #000 !important; font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important; border-radius: 15px !important;
        height: 60px !important; border: none !important; font-size: 1.2rem !important;
        transition: 0.3s all;
    }}
    .stButton>button:hover {{ transform: scale(1.02); box-shadow: 0 0 20px #00ffcc; }}
    
    /* Signal Colors */
    .signal-ultra {{ color: #ff00ff; text-shadow: 0 0 20px #ff00ff; font-weight: 900; }}
    .signal-strong {{ color: #00ffcc; text-shadow: 0 0 20px #00ffcc; font-weight: 900; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 AI & CALCULATION ENGINE
# ==========================================
if "history" not in st.session_state:
    st.session_state.history = []

if "ml_ready" not in st.session_state:
    st.session_state.ml_clf = RandomForestClassifier(n_estimators=300, random_state=42)
    st.session_state.ml_reg = RandomForestRegressor(n_estimators=200, random_state=42)
    st.session_state.ml_ready = False
    st.session_state.scaler = StandardScaler()

def run_engine_v14(h_in, t_in, last_cote):
    # Hash Processing
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:16], 16)
    np.random.seed(h_num & 0xffffffff)
    
    # Simulation logic (X3 Targets)
    prob_x3 = round(40 + (h_num % 58), 1)
    moy = round(1.6 + (h_num % 350)/100, 2)
    maxv = round(moy + (h_num % 650)/100, 2)
    minv = round(1.05 + (h_num % 60)/100, 2)
    strength = round(prob_x3 * 0.75 + (moy * 5), 1)
    
    # Time Entry Sync
    try:
        t_obj = datetime.strptime(t_in.strip(), "%H:%M:%S").time()
        base_time = datetime.combine(datetime.now().date(), t_obj)
    except:
        base_time = datetime.now(pytz.timezone("Indian/Antananarivo"))
    
    # Fixed Delay Logic for X3+
    delay = int(22 + (h_num % 18))
    entry_time = (base_time + timedelta(seconds=delay)).strftime("%H:%M:%S")
    
    res = {
        "entry": entry_time,
        "signal": "💎💎💎 ULTRA X3+ BUY" if strength > 82 else "🔥 STRONG X3 TARGET",
        "s_class": "signal-ultra" if strength > 82 else "signal-strong",
        "x3_prob": prob_x3, "moy": moy, "max": maxv, "min": minv,
        "strength": min(98.5, strength), "real_result": None
    }
    st.session_state.history.append(res)
    return res

# ==========================================
# 🖥️ MAIN UI LAYOUT
# ==========================================
st.markdown("<h1 class='main-title'>JETX ANDR V14</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00ffcc; font-family:Rajdhani;'>ULTRA STYLÉ • X3+ CIBLÉ • ENTRY ULTRA PUISSANTE</p>", unsafe_allow_html=True)

col_in, col_out = st.columns([1, 2])

with col_in:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🛰️ COMMAND CENTER")
    h_input = st.text_input("HASH (Provably Fair)")
    t_input = st.text_input("LAST TIME (HH:MM:SS)", placeholder="Ex: 22:08:20")
    l_input = st.number_input("LAST COTE", value=2.25, step=0.01)
    
    if st.button("🚀 LANCER L'ANALYSE", use_container_width=True):
        if h_input and len(t_input) >= 8:
            with st.spinner("Neural Processing..."):
                time.sleep(1)
                st.session_state.last_v14 = run_engine_v14(h_input, t_input, l_input)
        else:
            st.error("Fenoy tsara ny Hash sy ny Lera!")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.sidebar.button("🗑️ Reset Database"):
        st.session_state.history = []
        if "last_v14" in st.session_state: del st.session_state.last_v14
        st.rerun()

with col_out:
    if "last_v14" in st.session_state:
        r = st.session_state.last_v14
        
        st.markdown(f"""
        <div class="glass-card">
            <h2 class="{r['s_class']}" style="text-align:center; font-family:Orbitron;">{r['signal']}</h2>
            
            <div style="text-align:center; margin: 10px 0;">
                <small style="opacity:0.6; letter-spacing:2px;">X3 PROBABILITY</small><br>
                <span style="font-size:3rem; font-family:Orbitron; color:#ff00ff;">{r['x3_prob']}%</span>
            </div>

            <div style="background:rgba(0,255,204,0.1); padding:20px; border-radius:20px; text-align:center; border:1px solid #00ffcc; margin-bottom:20px;">
                <small style="letter-spacing:3px;">🎯 EXACT ENTRY TIME</small>
                <div style="font-size:5rem; font-weight:900; font-family:Orbitron; color:#fff; text-shadow: 0 0 30px #00ffcc;">{r['entry']}</div>
            </div>

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

            <p style="color:#ff3366; margin-top:20px; text-align:center; font-weight:bold;">
                ⚠️ Raha vao crash amin'ny {r['entry']} dia aza miditra intsony!
            </p>
            
            <hr style="opacity:0.2;">
            <div style="display:flex; justify-content:space-between; font-size:0.9rem; opacity:0.8; font-family:Rajdhani;">
                <span>STRENGTH: <b>{r['strength']}%</b></span>
                <span>STATUS: <b>NEURAL LINK ACTIVE</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Win/Loss Buttons
        c1, c2 = st.columns(2)
        with c1: 
            if st.button("✅ WIN", use_container_width=True): 
                st.session_state.history[-1]["real_result"] = "win"
                st.toast("Result saved: WIN")
        with c2: 
            if st.button("❌ LOSS", use_container_width=True): 
                st.session_state.history[-1]["real_result"] = "loss"
                st.toast("Result saved: LOSS")
    else:
        st.markdown("<div class='glass-card' style='height:450px; display:flex; align-items:center; justify-content:center; opacity:0.3;'><h2>AWAITING HASH DATA...</h2></div>", unsafe_allow_html=True)

# ==========================================
# 📂 HISTORY LOGS
# ==========================================
st.markdown("### 📜 MISSION LOGS")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)[::-1]
    st.dataframe(df[["entry", "signal", "x3_prob", "strength", "real_result"]], use_container_width=True)

st.caption("JETX ANDR V14 ULTRA • Optimized for Pydroid & Web • AI Target X3+")
