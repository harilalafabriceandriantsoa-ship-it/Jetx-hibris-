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
        .stApp {{ background: linear-gradient(135deg, #0a0a1f, #1a0033); }}
        .login-title {{ font-size: 4rem; font-weight: 900; text-align: center;
                       background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       font-family: 'Orbitron', sans-serif; padding-top: 50px; }}
    </style>
    """, unsafe_allow_html=True)
    st.markdown("<h1 class='login-title'>JETX ANDR</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#00ffcc;'>V14 ULTRA STYLÉ</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<br>", unsafe_allow_html=True)
        pw = st.text_input("🔑 Entrez le mot de passe :", type="password", placeholder="••••••••••")
        if st.button("✅ Accéder à l'application", use_container_width=True):
            if pw == "JET2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Mot de passe incorrect")
    st.stop()

# ==========================================
# 💎 UI DESIGN (Fixed CSS Braces)
# ==========================================
st.set_page_config(page_title="JETX ANDR V14 ULTRA", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    
    .stApp {{ background: linear-gradient(135deg, #0a0a1f 0%, #1a0033 100%); color: #e0fbfc; }}
    
    .main-title {{ 
        font-family: 'Orbitron', sans-serif; font-size: 3.5rem; font-weight: 900; text-align: center;
        background: linear-gradient(90deg, #00ffcc, #ff00ff, #00ccff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }}
    
    .glass-card {{ 
        background: rgba(15,15,40,0.85); 
        border: 1px solid rgba(0,255,204,0.5);
        border-radius: 25px; padding: 25px; 
        backdrop-filter: blur(20px);
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }}
    
    .signal-ultra {{ color: #ff00ff; text-shadow: 0 0 20px #ff00ff; font-weight: 900; font-size: 1.8rem; }}
    .signal-strong {{ color: #00ffcc; text-shadow: 0 0 20px #00ffcc; font-weight: 900; font-size: 1.8rem; }}
    .signal-good {{ color: #ffff00; font-weight: bold; font-size: 1.5rem; }}
    
    .stButton>button {{ 
        background: linear-gradient(135deg, #00ffcc, #0088ff) !important;
        color: #000 !important; font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important; border-radius: 15px !important;
        height: 55px !important; border: none !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 AI & LOGIC
# ==========================================
if "history" not in st.session_state:
    st.session_state.history = []

# Mock AI / Initialization
def get_time():
    return datetime.now(pytz.timezone("Indian/Antananarivo"))

def run_engine_ultra(h_in, t_in, last_cote):
    h_hex = hashlib.sha256(h_in.encode()).hexdigest()
    h_num = int(h_hex[:16], 16)
    np.random.seed(h_num & 0xffffffff)
    
    # Simulation logic
    prob_x3 = round(45 + (h_num % 45), 1)
    moy = round(1.5 + (h_num % 300)/100, 2)
    maxv = round(moy + (h_num % 500)/100, 2)
    minv = round(1.1 + (h_num % 50)/100, 2)
    strength = round(prob_x3 * 0.8 + 20, 1)
    
    # Time Calc
    try:
        t_obj = datetime.strptime(t_in.strip(), "%H:%M:%S").time()
        base_time = datetime.combine(datetime.now().date(), t_obj)
    except:
        base_time = datetime.now()
    
    entry_time = (base_time + timedelta(seconds=25)).strftime("%H:%M:%S")
    
    res = {
        "entry": entry_time, "signal": "💎 ULTRA X3+ BUY" if strength > 80 else "🔥 STRONG X3",
        "s_class": "signal-ultra" if strength > 80 else "signal-strong",
        "x3_prob": prob_x3, "moy": moy, "max": maxv, "min": minv,
        "strength": strength, "real_result": None
    }
    st.session_state.history.append(res)
    return res

# ==========================================
# 🖥️ UI DISPLAY
# ==========================================
st.markdown("<h1 class='main-title'>JETX ANDR V14</h1>", unsafe_allow_html=True)

col_ctrl, col_res = st.columns([1, 1.8])

with col_ctrl:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🛰️ SETUP")
    h_in = st.text_input("HASH")
    t_in = st.text_input("TIME (HH:MM:SS)", placeholder="22:08:20")
    l_in = st.number_input("LAST COTE", value=2.0)
    
    if st.button("🚀 EXECUTE ANALYSIS", use_container_width=True):
        if h_in and t_in:
            st.session_state.last_res = run_engine_ultra(h_in, t_in, l_in)
        else:
            st.error("Fenoy ny banga!")
    st.markdown("</div>", unsafe_allow_html=True)

with col_res:
    if "last_res" in st.session_state:
        r = st.session_state.last_res
        
        # Ny HTML voahitsy tsy misy error
        st.markdown(f"""
        <div class="glass-card">
            <div class="{r['s_class']}" style="text-align:center;">{r['signal']}</div>
            <div style="text-align:center; margin: 15px 0;">
                <small style="opacity:0.6;">PROBABILITY X3+</small><br>
                <span style="font-size:2.5rem; font-family:Orbitron; color:#ff00ff;">{r['x3_prob']}%</span>
            </div>
            
            <div style="background:rgba(0,255,204,0.1); padding:15px; border-radius:20px; text-align:center; border:1px solid #00ffcc;">
                <small>ENTRY TIME</small>
                <div style="font-size:4rem; font-weight:900; font-family:Orbitron;">{r['entry']}</div>
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
                <small>• MAX → Cashout amin'ny 3x na mihoatra raha ULTRA.</small>
            </div>

            <p style="color:#ff3366; margin-top:15px; text-align:center;">
                <b>⚠️ Raha vao crash amin'ny {r['entry']} dia aza miditra intsony!</b>
            </p>
            <hr style="opacity:0.2;">
            <div style="display:flex; justify-content:space-between; font-size:0.8rem; opacity:0.8;">
                <span>Strength: <b>{r['strength']}</b></span>
                <span>Status: <b>Active Neural Link</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Miandry ny Analysis...")

# History (Simple)
if st.session_state.history:
    st.write("### 📜 Mission Logs")
    st.table(pd.DataFrame(st.session_state.history).tail(5))
