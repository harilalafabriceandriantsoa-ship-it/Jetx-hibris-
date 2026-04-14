import streamlit as st
import numpy as np
import statistics
from datetime import datetime, timedelta
import plotly.express as px

# ---------------- IDENTITY & CONFIG ----------------
st.set_page_config(page_title="HUBRIS V1: ANDR-X", layout="wide")

# ---------------- NEON PREMIUM STYLE ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {background: #050505; color:#00ffcc; font-family: 'Orbitron', sans-serif;}
    .metric-card {
        background: rgba(0, 255, 204, 0.07);
        padding: 20px; border-radius: 15px;
        border: 2px solid #00ffcc; text-align: center;
        box-shadow: 0 0 15px rgba(0, 255, 204, 0.2);
        margin-bottom: 20px;
    }
    .guide-box {
        background: #111; padding: 15px; border-radius: 10px;
        border-left: 5px solid #0066ff; margin-bottom: 10px; font-size: 14px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #00ffcc 0%, #0066ff 100%);
        color: white; border: none; width: 100%; height: 50px; 
        font-weight: bold; border-radius: 10px; transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0 0 20px #00ffcc; transform: scale(1.02); }
    h1, h2, h3 {text-align: center; color: #00ffcc; text-transform: uppercase;}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN SYSTEM ----------------
if "login_success" not in st.session_state:
    st.session_state.login_success = False

if not st.session_state.login_success:
    st.markdown("<h1>🔐 HUBRIS V1 ACCESS</h1>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        pwd = st.text_input("PASSWORD SYSTEM:", type="password")
        if st.button("ACTIVATE ANDR-X"):
            if pwd == "2026":
                st.session_state.login_success = True
                st.rerun()
            else:
                st.error("Access Denied: Password incorrect.")
    st.stop()

# ---------------- INITIALIZATION ----------------
if "jetx_history" not in st.session_state:
    st.session_state.jetx_history = []

# ---------------- CORE ENGINE (ULTRA V1) ----------------
def get_prediction(history):
    if len(history) < 3: return None
    avg = statistics.mean(history)
    dev = statistics.stdev(history) if len(history) > 1 else 0.5
    sims = np.random.lognormal(mean=np.log(avg), sigma=dev * 0.45, size=20000)
    success = [s for s in sims if s >= 3.0]
    prob = (len(success) / len(sims)) * 100
    
    # Timing Dynamic
    now = datetime.now()
    delay = 1 if history[-1] < 2.0 else 2
    h_entree = (now + timedelta(minutes=delay)).strftime("%H:%M")
    
    return {
        "h": h_entree, 
        "p": round(prob, 2), 
        "m": round(statistics.mean(success), 2) if success else 3.0,
        "max": round(np.percentile(sims, 95), 2)
    }

# ---------------- APP HEADER ----------------
st.markdown("<h1>⚡ HUBRIS V1 <span style='color:white;'>| ANDR-X</span></h1>", unsafe_allow_html=True)
st.write("---")

# ---------------- TABS SYSTEM ----------------
tab_app, tab_hist, tab_guide = st.tabs(["🚀 NEURAL TERMINAL", "📜 HISTORIQUE", "📖 GUIDE"])

with tab_app:
    c1, c2 = st.columns([1, 1.2])
    
    with c1:
        st.subheader("📡 INPUT DATA")
        val = st.number_input("Crash farany nivoaka:", min_value=1.0, step=0.01, format="%.2f")
        if st.button("RUN ANALYSIS"):
            st.session_state.jetx_history.append(val)
            if len(st.session_state.jetx_history) > 15: st.session_state.jetx_history.pop(0)
            st.rerun()
        
        if st.button("RESET MEMORY"):
            st.session_state.jetx_history = []
            st.rerun()

    with c2:
        st.subheader("🧠 AI PREDICTION")
        if len(st.session_state.jetx_history) >= 3:
            res = get_prediction(st.session_state.jetx_history)
            
            # Prediction Card
            st.markdown(f"""
                <div class='metric-card'>
                    <p style='color:#aaa; font-size:12px;'>ORA IZAO: {datetime.now().strftime("%H:%M:%S")}</p>
                    <p style='color:white; margin:0;'>HEURE D'ENTRÉE PREVUE</p>
                    <h1 style='font-size:55px; margin:0;'>{res['h']}</h1>
                    <p style='color:#00ffcc;'>VINTANA X3+: <b>{res['p']}%</b></p>
                </div>
            """, unsafe_allow_html=True)
            
            # Metrics Row
            m1, m2, m3 = st.columns(3)
            m1.metric("MIN (SECURE)", "2.00x")
            m2.metric("MOYEN (TARGET)", f"{res['m']}x")
            m3.metric("MAX (EXPLOSION)", f"{res['max']}x")
            
            if res['p'] > 35:
                st.success("🔥 SIGNAL ULTRA: Midira amin'io ora io!")
            else:
                st.warning("⚖️ MIANDRASY: Mbola tsy ampy ny serie mena.")
        else:
            st.info(f"Mbola mila isa {3 - len(st.session_state.jetx_history)} ianao vao hiseho ny vokatra feno.")

with tab_hist:
    st.subheader("Tantaran'ny Rounds")
    if st.session_state.jetx_history:
        col_list, col_graph = st.columns([1, 2])
        with col_list:
            for i, v in enumerate(reversed(st.session_state.jetx_history)):
                color = "#00ffcc" if v >= 2.0 else "#ff4b4b"
                st.markdown(f"Round {len(st.session_state.jetx_history)-i}: <b style='color:{color};'>{v}x</b>", unsafe_allow_html=True)
        with col_graph:
            fig = px.line(y=st.session_state.jetx_history, markers=True, title="Trend Analysis")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#00ffcc")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Tsy misy tantara azo jerena.")

with tab_guide:
    st.markdown("""
    ### 📘 GUIDE D'UTILISATION (ANDR-X)
    <div class='guide-box'><b>1. Login:</b> Ampiasao ny <b>2026</b> raha hampiakatra ny rafitra.</div>
    <div class='guide-box'><b>2. Reference:</b> Miandrasa serie mena (1.00x - 1.99x) farafahakeliny isa 3.</div>
    <div class='guide-box'><b>3. Input:</b> Ampidiro tsirairay ireo isa ireo ao amin'ny 'Input Data' ary tsindrio 'Run Analysis'.</div>
    <div class='guide-box'><b>4. Prediction:</b> Rehefa mipoitra ny <b>Heure d'entrée</b>, miomàna hiditra (Mise) amin'io minitra io.</div>
    <div class='guide-box'><b>5. Cashout:</b> Mivoaha amin'ny <b>X2.00 (Min)</b> na <b>X3.00 (Moyen)</b> araka ny fahasahianao.</div>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR INFO ----------------
st.sidebar.markdown(f"""
### 📊 STATUS SESSION
- **USER:** ANDR-X
- **VERSION:** 1.0.2 (Ultra)
- **DATABASE:** {len(st.session_state.jetx_history)} pts
""")
