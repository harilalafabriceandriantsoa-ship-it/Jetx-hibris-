import streamlit as st
import numpy as np
import statistics
from datetime import datetime, timedelta
import plotly.express as px

# ---------------- IDENTITY & CONFIG ----------------
st.set_page_config(page_title="HUBRIS V1: ANDR-X EDITION", layout="wide")

# ---------------- DESIGN NEON PREMIUM ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {background: #030303; color:#00ffcc; font-family: 'Orbitron', sans-serif;}
    
    /* Login Card */
    .login-box {
        background: rgba(0, 255, 204, 0.05);
        padding: 30px; border-radius: 20px;
        border: 2px solid #00ffcc; text-align: center;
        box-shadow: 0 0 25px rgba(0, 255, 204, 0.3);
    }
    
    /* Metric Card */
    .metric-card {
        background: linear-gradient(180deg, rgba(0, 255, 204, 0.1) 0%, rgba(0, 0, 0, 0) 100%);
        padding: 20px; border-radius: 15px;
        border: 1px solid #00ffcc; text-align: center;
        box-shadow: 0 0 15px rgba(0, 255, 204, 0.1);
        margin-bottom: 15px;
    }
    
    /* Historique Box */
    .hist-box {
        background: #111; padding: 12px; border-radius: 10px;
        border: 1px solid #333; margin-bottom: 8px;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #00ffcc 0%, #0066ff 100%);
        color: white; border: none; width: 100%; height: 50px; 
        font-weight: bold; border-radius: 12px; transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0 0 30px #00ffcc; transform: scale(1.02); }
    
    h1, h2, h3 {text-align: center; color: #00ffcc; text-transform: uppercase; letter-spacing: 2px;}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION MANAGEMENT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "jetx_history" not in st.session_state:
    st.session_state.jetx_history = []
if "pred_history" not in st.session_state:
    st.session_state.pred_history = []

# ---------------- LOGIN PAGE ----------------
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c_log1, c_log2, c_log3 = st.columns([1, 2, 1])
    with c_log2:
        st.markdown("""
        <div class='login-box'>
            <h1>⚡ HUBRIS V1</h1>
            <p style='color:white;'>SYSTEM ACCESS - ANDR-X EDITION</p>
        </div>
        """, unsafe_allow_html=True)
        pwd = st.text_input("PASSWORD:", type="password", placeholder="Enter 2026")
        if st.button("ACTIVATE SYSTEM"):
            if pwd == "2026":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Access Denied: Invalid Security Code.")
    st.stop()

# ---------------- ALGORITHM ENGINE ----------------
def run_simulation(history):
    # Instant calculation base
    avg = statistics.mean(history) if history else 1.8
    dev = statistics.stdev(history) if len(history) > 1 else 0.7
    
    # Monte Carlo simulation (15k rounds)
    sims = np.random.lognormal(mean=np.log(avg), sigma=dev * 0.4, size=15000)
    success_3x = [s for s in sims if s >= 3.0]
    prob = (len(success_3x) / len(sims)) * 100
    
    now = datetime.now()
    # Dynamic timing: delays based on last crash
    delay = 1 if (history and history[-1] < 2.0) else 2
    h_entree = (now + timedelta(minutes=delay)).strftime("%H:%M")
    
    return {
        "heure": h_entree,
        "prob": round(prob, 2),
        "target": round(statistics.mean(success_3x), 2) if success_3x else 3.0,
        "max": round(np.percentile(sims, 95), 2),
        "ref": history[-1] if history else 0
    }

# ---------------- MAIN DASHBOARD ----------------
st.markdown("<h1>⚡ ANDR-X <span style='color:white;'>TERMINAL</span></h1>", unsafe_allow_html=True)
st.write("---")

tab_terminal, tab_history, tab_guide = st.tabs(["🚀 ANALYSEUR", "📜 HISTORIQUE", "📖 GUIDE CLIENT"])

with tab_terminal:
    col_in, col_out = st.columns([1, 1.2])
    
    with col_in:
        st.subheader("📡 INPUT DATA")
        crash_val = st.number_input("Crash du tour farany:", min_value=1.0, step=0.01, format="%.2f")
        
        if st.button("RUN PREDICTION"):
            st.session_state.jetx_history.append(crash_val)
            # Save to prediction history
            new_pred = run_simulation(st.session_state.jetx_history)
            st.session_state.pred_history.append(new_pred)
            
            if len(st.session_state.jetx_history) > 12: st.session_state.jetx_history.pop(0)
            if len(st.session_state.pred_history) > 6: st.session_state.pred_history.pop(0)
            st.rerun()
            
        if st.button("RESET MEMORY"):
            st.session_state.jetx_history = []
            st.session_state.pred_history = []
            st.rerun()

    with col_out:
        st.subheader("🧠 RESULTATS")
        if st.session_state.jetx_history:
            res = run_simulation(st.session_state.jetx_history)
            
            st.markdown(f"""
                <div class='metric-card'>
                    <p style='color:#00ffcc; font-size:14px; margin:0;'>ORA IZAO: {datetime.now().strftime("%H:%M:%S")}</p>
                    <p style='color:white; margin:5px 0 0 0;'>HEURE D'ENTRÉE</p>
                    <h1 style='font-size:55px; margin:0;'>{res['heure']}</h1>
                    <p style='color:#ffcc00; font-size:22px; font-weight:bold;'>PROBABILITÉ: {res['prob']}%</p>
                    <p style='color:#aaa; font-size:12px;'>Réf. Crash: {res['ref']}x</p>
                </div>
            """, unsafe_allow_html=True)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("MIN", "2.00x")
            m2.metric("MOYEN", f"{res['target']}x")
            m3.metric("MAX", f"{res['max']}x")
            
            if res['prob'] > 40:
                st.success("🔥 SIGNAL FORT: Cycle favorable ho an'ny X3+")
            elif res['prob'] > 25:
                st.info("⚖️ PRUDENCE: Cycle instable, mivoaha amin'ny X2")
            else:
                st.warning("⚠️ ATTENTE: Miandrasa serie mena latsaky ny 1.50x")
        else:
            st.info("Ampidiro ny crash nivoaka farany hanombohana ny kajy.")

with tab_history:
    st.subheader("Tantaran'ny faminany (Predictions)")
    if st.session_state.pred_history:
        for p in reversed(st.session_state.pred_history):
            st.markdown(f"""
            <div class='hist-box'>
                <span style='color:#00ffcc;'>Ora: {p['heure']}</span> | 
                <span style='color:white;'>Vintana: {p['prob']}%</span> | 
                <span style='color:#aaa;'>Ref: {p['ref']}x</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("Tsy misy tantara azo aseho.")

with tab_guide:
    st.markdown("""
    ### 📖 TORO-LALANA HO AN'NY MPANJIFA (GUIDE CLIENT)
    
    **1. Fidirana (Login):**
    Ampidiro ny teny miafina **2026** mba hanombohana ny rafitra.
    
    **2. Ny fomba fiasa (Analyse):**
    Isaky ny misy "Crash" mipoitra eo amin'ny JetX, ampidiro ao amin'ny 'Input Data' ilay isa ary tsindrio 'Run Prediction'.
    
    **3. Ny ora fidirana (Heure d'entrée):**
    Ny AI dia manome ora (ohatra: **12:45**). Rehefa vao miova ho 45 ny minitra eo amin'ny findainao, dia apetraho ny "Mise".
    
    **4. Ny tanjona (Target):**
    - **MIN (2.00x):** Ho an'ireo te hahazo vola azo antoka.
    - **MOYEN (X3+):** Ny tanjona kendren'ny ANDR-X.
    - **MAX:** Ho an'ireo sahy manao "Risque" avo.
    
    **5. Ny tsiambaratelo (Pro Tip):**
    Ny fotoana tsara indrindra idirana dia rehefa nisy isa mena (latsaky ny 1.50x) nivoaka in-2 na in-3 nisesy.
    """)

# ---------------- SIDEBAR ----------------
st.sidebar.markdown(f"""
### 🛠️ SYSTEM INFO
- **VERSION:** 1.1 (Ultra-Fast)
- **ENGINE:** Monte Carlo 15k
- **USER:** ANDR-X CLIENT
- **TIME:** {datetime.now().strftime("%H:%M")}
""")
