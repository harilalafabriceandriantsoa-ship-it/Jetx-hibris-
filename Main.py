import streamlit as st
import numpy as np
import statistics
from datetime import datetime, timedelta

# ---------------- CONFIGURATION & STYLE ----------------
st.set_page_config(page_title="HUBRIS V1: ANDR-X EDITION", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;500&display=swap');
    
    .stApp {background: #020202; color:#00ffcc; font-family: 'Orbitron', sans-serif;}
    
    /* Login Design */
    .login-card {
        background: rgba(0, 255, 204, 0.05);
        padding: 40px; border-radius: 20px;
        border: 2px solid #00ffcc; text-align: center;
        box-shadow: 0 0 30px rgba(0, 255, 204, 0.2);
    }

    /* Prediction Card */
    .main-card {
        background: linear-gradient(145deg, rgba(0, 255, 204, 0.15) 0%, rgba(0, 0, 0, 1) 100%);
        padding: 20px; border-radius: 20px;
        border: 1px solid #00ffcc; text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }

    /* History Style */
    .hist-item {
        background: #111; padding: 10px; border-radius: 10px;
        border-left: 4px solid #00ffcc; margin-bottom: 5px;
        font-family: 'Roboto', sans-serif; font-size: 13px;
    }

    .stButton>button {
        background: linear-gradient(135deg, #00ffcc 0%, #0066ff 100%);
        color: white; border: none; border-radius: 12px; height: 50px;
        font-weight: bold; width: 100%; transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 0 20px #00ffcc; }
    
    h1, h2, h3 {text-align: center; color: #00ffcc; text-transform: uppercase;}
</style>
""", unsafe_allow_html=True)

# ---------------- STATE MANAGEMENT ----------------
if "auth" not in st.session_state: st.session_state.auth = False
if "history" not in st.session_state: st.session_state.history = []
if "full_preds" not in st.session_state: st.session_state.full_preds = []

# ---------------- LOGIN SYSTEM ----------------
if not st.session_state.auth:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 2, 1])
    with col_log:
        st.markdown("<div class='login-card'><h1>⚡ HUBRIS V1</h1><p>ANDR-X SECURITY ACCESS</p></div><br>", unsafe_allow_html=True)
        pwd = st.text_input("PASSWORD:", type="password")
        if st.button("ACTIVATE SYSTEM"):
            if pwd == "2026":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Access Denied")
    st.stop()

# ---------------- ENGINE ----------------
def calculate_all(data):
    avg = statistics.mean(data) if data else 1.8
    dev = statistics.stdev(data) if len(data) > 1 else 0.6
    sims = np.random.lognormal(mean=np.log(avg), sigma=dev * 0.42, size=15000)
    
    target_sims = [s for s in sims if s >= 3.0]
    prob = (len(target_sims) / len(sims)) * 100
    
    now = datetime.now()
    delay = 1 if (data and data[-1] < 2.0) else 2
    h_entree = (now + timedelta(minutes=delay)).strftime("%H:%M")
    
    return {
        "heure": h_entree,
        "vintana": round(prob, 2),
        "moy": round(statistics.mean(target_sims), 2) if target_sims else 3.0,
        "max": round(np.percentile(sims, 95), 2),
        "ref": data[-1] if data else 0
    }

# ---------------- UI DASHBOARD ----------------
st.markdown("<h1>⚡ TERMINAL ANDR-X V1</h1>", unsafe_allow_html=True)

tab_main, tab_guide = st.tabs(["🚀 ANALYSEUR", "📖 GUIDE & INFO"])

with tab_main:
    c1, c2 = st.columns([1, 1.2])
    
    with c1:
        st.subheader("📡 INPUT")
        val = st.number_input("Crash tour farany:", min_value=1.0, step=0.01, format="%.2f")
        if st.button("RUN ANALYSIS"):
            st.session_state.history.append(val)
            res = calculate_all(st.session_state.history)
            # Tehirizina ny prédiction rehetra
            st.session_state.full_preds.append(res)
            
            if len(st.session_state.history) > 15: st.session_state.history.pop(0)
            if len(st.session_state.full_preds) > 10: st.session_state.full_preds.pop(0)
            st.rerun()
        
        if st.button("RESET MEMORY"):
            st.session_state.history = []
            st.session_state.full_preds = []
            st.rerun()

    with c2:
        st.subheader("🧠 RESULTATS")
        if st.session_state.full_preds:
            current = st.session_state.full_preds[-1]
            st.markdown(f"""
                <div class='main-card'>
                    <p style='color:#00ffcc; font-size:12px; margin:0;'>ORA IZAO: {datetime.now().strftime("%H:%M:%S")}</p>
                    <p style='color:#aaa; font-size:11px; margin:0;'>REFERENCE COTE: {current['ref']}x</p>
                    <p style='color:white; margin:10px 0 0 0;'>HEURE D'ENTRÉE PREVUE</p>
                    <h1 style='font-size:60px; margin:0;'>{current['heure']}</h1>
                    <p style='color:#ffcc00; font-size:22px;'>PROBABILITÉ X3+: <b>{current['vintana']}%</b></p>
                </div>
            """, unsafe_allow_html=True)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("MIN", "2.00x")
            m2.metric("MOYEN", f"{current['moy']}x")
            m3.metric("MAX", f"{current['max']}x")
        else:
            st.info("Miandry data hanombohana ny analyse...")

    st.write("---")
    st.subheader("📜 HISTORIQUE DES PRÉDICTIONS")
    if st.session_state.full_preds:
        # Asehoy ny 5 farany
        for p in reversed(st.session_state.full_preds):
            st.markdown(f"""
            <div class='hist-item'>
                <b>Ora: {p['heure']}</b> | Vintana: {p['vintana']}% | Ref: {p['ref']}x | Target: {p['moy']}x
            </div>
            """, unsafe_allow_html=True)

with tab_guide:
    st.markdown("""
    ### 📘 GUIDE D'UTILISATION
    1. **Ampidiro ny Crash:** Soraty eo amin'ny 'Input' ny isa nivoaka farany eo amin'ny lalao.
    2. **Tsindrio Run:** Isaky ny manindry ianao dia misy analyse vaovao miforona.
    3. **Heure d'entrée:** Io no ora tokony hidiranao (Mise). Miandrasa vao miova io minitra io ny findainao.
    4. **Cote Reference:** Io no nampiasain'ny AI hanaovana ny kajy farany.
    5. **Historique:** Azonao jerena eo ambany ny tantaran'ny prédiction rehetra nataonao mba hahitana ny "Trend".
    """)

# Sidebar
st.sidebar.markdown(f"**USER:** ANDR-X  \n**VERSION:** 1.1.0  \n**STATUS:** ONLINE")
