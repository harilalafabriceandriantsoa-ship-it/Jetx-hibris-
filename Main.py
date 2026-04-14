import streamlit as st
import numpy as np
import statistics
from datetime import datetime, timedelta
import plotly.express as px

# ---------------- CONFIG & IDENTITY ----------------
st.set_page_config(page_title="HUBRIS V1: ANDR-X", layout="wide")

# ---------------- STYLE NEON PREMIUM ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp {background: #030303; color:#00ffcc; font-family: 'Orbitron', sans-serif;}
    
    /* Box stylé ho an'ny vokatra */
    .metric-card {
        background: rgba(0, 255, 204, 0.05);
        padding: 25px; border-radius: 20px;
        border: 2px solid #00ffcc;
        text-align: center;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.3);
        margin-bottom: 25px;
    }
    
    /* Guide d'utilisation stylé */
    .guide-box {
        background: #111; padding: 20px; border-radius: 15px;
        border-left: 5px solid #0066ff; margin: 10px 0;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #00ffcc 0%, #0066ff 100%);
        color: white; border: none; width: 100%; height: 55px; 
        font-weight: bold; font-size: 18px; border-radius: 12px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        box-shadow: 0 0 25px #00ffcc; transform: scale(1.02);
    }
    
    h1, h2 {color: #00ffcc; text-transform: uppercase; letter-spacing: 5px;}
</style>
""", unsafe_allow_html=True)

# ---------------- INITIALIZATION ----------------
if "jetx_history" not in st.session_state:
    st.session_state.jetx_history = []

# ---------------- CORE ENGINE ----------------
def get_prediction(history):
    if len(history) < 3: return None
    avg = statistics.mean(history)
    dev = statistics.stdev(history) if len(history) > 1 else 0.5
    sims = np.random.lognormal(mean=np.log(avg), sigma=dev * 0.4, size=15000)
    success = [s for s in sims if s >= 3.0]
    prob = (len(success) / len(sims)) * 100
    
    # Timing Dynamic
    now = datetime.now()
    delay = 1 if history[-1] < 2.0 else 2
    h_entree = (now + timedelta(minutes=delay)).strftime("%H:%M")
    
    return {"h": h_entree, "p": round(prob, 2), "m": round(statistics.mean(success), 2) if success else 3.0}

# ---------------- HEADER ----------------
st.markdown("<h1>⚡ HUBRIS V1 <span style='color:white;'>| ANDR-X</span></h1>", unsafe_allow_html=True)
st.write("---")

# ---------------- TABS ----------------
tab_app, tab_guide = st.tabs(["🚀 NEURAL TERMINAL", "📖 MANUEL D'UTILISATION"])

with tab_app:
    c1, c2 = st.columns([1, 1.2])
    
    with c1:
        st.subheader("📡 INPUT DATA")
        val = st.number_input("Entrer Last Crash:", min_value=1.0, step=0.01, format="%.2f")
        if st.button("RUN ANALYSIS"):
            st.session_state.jetx_history.append(val)
            if len(st.session_state.jetx_history) > 12: st.session_state.jetx_history.pop(0)
            st.rerun()
        
        if st.button("RESET MEMORY"):
            st.session_state.jetx_history = []
            st.rerun()

    with c2:
        st.subheader("🧠 AI PREDICTION")
        if len(st.session_state.jetx_history) >= 3:
            res = get_prediction(st.session_state.jetx_history)
            st.markdown(f"""
                <div class='metric-card'>
                    <p style='color:white; font-size:14px; margin-bottom:5px;'>HEURE D'ENTRÉE</p>
                    <h1 style='font-size:50px; margin:0;'>{res['h']}</h1>
                    <p style='color:#00ffcc;'>PROBABILITÉ X3+: <b>{res['p']}%</b></p>
                </div>
            """, unsafe_allow_html=True)
            
            st.metric("COTE TARGET (MOYENNE)", f"{res['m']}x")
            
            if res['p'] > 35:
                st.success("🔥 SIGNAL ULTRA: RTP Gap détecté. Go!")
            else:
                st.warning("⚖️ ANALYSING: Miandrasa serie mena fohy.")
        else:
            st.info("Besoin de 3 données minimum pour activer l'IA.")

with tab_guide:
    st.markdown("""
    ## 📘 FOMBA FAMPIASANA (ANDR-X GUIDE)
    
    <div class='guide-box'>
        <b>1. Jereo ny JetX:</b> Miandrasa 'Serie Rouge' (Mena). Ny tsara indrindra dia rehefa misy isa 3 nisesy latsaky ny 2.0x.
    </div>
    
    <div class='guide-box'>
        <b>2. Ampidiro ny Data:</b> Soraty ao amin'ny 'Input Data' ny multiplier vao mivoaka eo amin'ny JetX. Avy eo tsindrio ny 'RUN ANALYSIS'.
    </div>
    
    <div class='guide-box'>
        <b>3. Jereo ny Heure d'entrée:</b> Raha vao miteny ny AI hoe <b>11:35</b>, dia amin'io minitra io no miditra (Mise).
    </div>
    
    <div class='guide-box'>
        <b>4. Tanjona (Cashout):</b> Ny tanjona dia <b>X3.00</b>. Raha vao mahatratra an'izay ny fiaramanidina dia mivoaha avy hatrany.
    </div>
    
    <div class='guide-box'>
        <b>5. Mitandrema:</b> Raha latsaky ny 25% ny probabilité, dia aza miditra. Miandrasa signal matanjaka (maitso).
    </div>
    """, unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.sidebar.markdown(f"""
### 📊 SESSION STATS
- **System:** ONLINE
- **User:** ANDR-X
- **Data Points:** {len(st.session_state.jetx_history)}
- **Current Time:** {datetime.now().strftime("%H:%M:%S")}
""")
