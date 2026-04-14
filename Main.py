import streamlit as st
import numpy as np
import statistics
from datetime import datetime, timedelta

# ---------------- CONFIGURATION & STYLE ----------------
st.set_page_config(page_title="ANDR-X TERMINAL v1.6", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {background: #000000; color:#00ffcc; font-family: 'Orbitron', sans-serif;}
    
    /* Box lehibe iray ho an'ny valiny rehetra */
    .terminal-card {
        background: linear-gradient(180deg, rgba(0, 255, 204, 0.15) 0%, rgba(0, 0, 0, 0.9) 100%);
        padding: 20px; border-radius: 20px; border: 2px solid #00ffcc;
        text-align: center; margin-bottom: 15px;
        box-shadow: 0 0 25px rgba(0, 255, 204, 0.3);
    }
    
    .main-time { font-size: 50px; font-weight: bold; color: #fff; margin: 10px 0; line-height: 1; }
    .status-line { font-size: 11px; color: #aaa; text-transform: uppercase; margin-bottom: 10px; border-bottom: 1px solid #222; padding-bottom: 5px; }
    
    .grid-container { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 15px; }
    .grid-item { background: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 10px; }
    .label-x { font-size: 10px; color: #00ffcc; display: block; margin-bottom: 2px; }
    .val-x { font-size: 16px; font-weight: bold; color: white; }

    .stButton>button {
        background: linear-gradient(135deg, #00ffcc 0%, #0066ff 100%);
        color: white; border: none; border-radius: 12px; font-weight: bold; width: 100%; height: 50px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- INITIALIZATION ----------------
if "pred_log" not in st.session_state: st.session_state.pred_log = []
if "auth" not in st.session_state: st.session_state.auth = False

# ---------------- LOGIN (HIDDEN PASSWORD) ----------------
if not st.session_state.auth:
    st.markdown("<br><br><h1 style='text-align:center;'>⚡ ANDR-X SYSTEM</h1>", unsafe_allow_html=True)
    pwd = st.text_input("SECURITY CODE:", type="password") # Tsisy 'Enter 2026' intsony
    if st.button("ACTIVATE"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# ---------------- ENGINE (DYNAMIQUE) ----------------
def run_prediction(crash, h_tour, r_min, r_max):
    try:
        t_obj = datetime.strptime(h_tour, "%H:%M:%S")
    except:
        t_obj = datetime.strptime(h_tour, "%H:%M")
        
    # Algorithm Monte Carlo (Simulation 15,000)
    # Mikajy ny elanelana sy ny herin'ny reference
    base_val = (crash * (r_max - r_min)) + 1.6
    sims = np.random.lognormal(mean=np.log(base_val), sigma=0.38, size=15000)
    success_3x = [s for s in sims if s >= 3.0]
    
    # Kajy Heure d'entrée (Delay dynamique)
    delay_sec = 45 if crash < 1.5 else 95
    h_entree = (t_obj + timedelta(seconds=delay_sec)).strftime("%H:%M:%S")
    
    return {
        "h_act": h_tour,
        "h_ent": h_entree,
        "ref": f"{r_min:.2f}-{r_max:.2f}",
        "crash": crash,
        "prob": round((len(success_3x)/15000)*100, 1),
        "min": "2.00",
        "moy": round(statistics.mean(success_3x), 2) if success_3x else 3.0,
        "max": round(np.percentile(sims, 95), 2)
    }

# ---------------- INTERFACE ----------------
st.markdown("<h1 style='text-align:center;'>🚀 NEURAL TERMINAL</h1>", unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🚀 ANALYSE", "📜 HISTORIQUE", "📖 GUIDE"])

with t1:
    col_a, col_b = st.columns(2)
    with col_a:
        c_in = st.number_input("Crash tour farany:", value=1.50, step=0.01)
        h_in = st.text_input("Ora (HH:mm:ss):", value=datetime.now().strftime("%H:%M:%S"))
    with col_b:
        r_lo = st.number_input("Ref Min:", value=1.00)
        r_hi = st.number_input("Ref Max:", value=1.99)
    
    if st.button("EXECUTER ANALYSE"):
        res = run_prediction(c_in, h_in, r_lo, r_hi)
        st.session_state.pred_log.append(res)
        st.rerun()

    if st.session_state.pred_log:
        c = st.session_state.pred_log[-1]
        st.markdown(f"""
            <div class='terminal-card'>
                <div class='status-line'>TOUR: {c['h_act']} | REF: {c['ref']} | CRASH: {c['crash']}x</div>
                <p style='color:#aaa; font-size:12px; margin:0;'>HEURE D'ENTRÉE PRÉVUE</p>
                <div class='main-time'>{c['h_ent']}</div>
                <div style='color:#ffcc00; font-weight:bold; font-size:18px;'>PROBABILITÉ X3+: {c['prob']}%</div>
                
                <div class='grid-container'>
                    <div class='grid-item'><span class='label-x'>MIN</span><span class='val-x'>{c['min']}x</span></div>
                    <div class='grid-item'><span class='label-x'>MOYEN</span><span class='val-x'>{c['moy']}x</span></div>
                    <div class='grid-item'><span class='label-x'>MAX</span><span class='val-x'>{c['max']}x</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

with t2:
    st.subheader("📜 Tantara Rehetra")
    if st.session_state.pred_log:
        for p in reversed(st.session_state.pred_log):
            st.markdown(f"""
            <div style='border-left:3px solid #00ffcc; padding-left:10px; margin-bottom:10px; background:rgba(255,255,255,0.05); padding:8px; border-radius:5px;'>
                <b>ENTRÉE: {p['h_ent']}</b> (Tour: {p['h_act']})<br>
                <small>Prob: {p['prob']}% | Crash: {p['crash']}x | Target: {p['moy']}x</small>
            </div>
            """, unsafe_allow_html=True)
    else: st.info("Tsy misy tantara.")

with t3:
    st.markdown("""
    ### 📖 Guide d'Utilisation
    1. **Input Data**: Ampidiro ny *Crash* farany, ny *Ora* (HH:mm:ss), ary ny *Cote Référence* [1.00 - 1.99].
    2. **Analyse**: Ny AI dia mikajy ny ora fidirana (Heure d'entrée) miaraka amin'ny segondra.
    3. **Cotes**:
        * **Min**: 2.00x ho an'ny fiarovana.
        * **Moyen**: Tanjona araka ny fikajiana RTP.
        * **Max**: Ny fara-tampony mety ho tratra.
    4. **Historique**: Azonao jerena eo amin'ny tab faha-2 ny prédiction rehetra teo aloha.
    """)

st.sidebar.markdown(f"**USER**: ANDR-X  \n**STATUS**: ONLINE  \n**VERSION**: 1.6")
