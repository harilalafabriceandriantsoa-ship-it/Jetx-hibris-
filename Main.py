import streamlit as st
import numpy as np
import statistics
from datetime import datetime, timedelta

# ---------------- CONFIGURATION & STYLE ----------------
st.set_page_config(page_title="ANDR-X TERMINAL v1.8", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {background: #000000; color:#00ffcc; font-family: 'Orbitron', sans-serif;}
    
    /* Bloc tokana ho an'ny valiny rehetra */
    .terminal-card {
        background: linear-gradient(180deg, rgba(0, 255, 204, 0.15) 0%, rgba(0, 0, 0, 0.9) 100%);
        padding: 20px; border-radius: 20px; border: 2px solid #00ffcc;
        text-align: center; margin-bottom: 15px;
        box-shadow: 0 0 25px rgba(0, 255, 204, 0.3);
    }
    
    .main-time { font-size: 50px; font-weight: bold; color: #fff; line-height: 1; margin: 10px 0; }
    .status-line { font-size: 11px; color: #aaa; text-transform: uppercase; margin-bottom: 10px; border-bottom: 1px solid #333; padding-bottom: 5px; }
    .note-box { background: rgba(255, 0, 0, 0.15); border: 1px solid #ff4444; color: #ff4444; padding: 10px; border-radius: 10px; font-size: 13px; margin-top: 10px; font-weight: bold; }
    
    .grid-container { display: flex; justify-content: space-around; margin-top: 20px; gap: 10px; }
    .grid-item { background: rgba(255, 255, 255, 0.08); padding: 12px; border-radius: 12px; flex: 1; border: 1px solid #333; }
    .label-x { font-size: 10px; color: #00ffcc; display: block; margin-bottom: 5px; }
    .val-x { font-size: 18px; font-weight: bold; color: white; }

    .stButton>button {
        background: linear-gradient(135deg, #00ffcc 0%, #0066ff 100%);
        color: white; border: none; border-radius: 12px; font-weight: bold; width: 100%; height: 50px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- INITIALIZATION ----------------
if "pred_log" not in st.session_state: st.session_state.pred_log = []
if "auth" not in st.session_state: st.session_state.auth = False

# ---------------- LOGIN (SECURITY CODE) ----------------
if not st.session_state.auth:
    st.markdown("<br><br><h1 style='text-align:center;'>⚡ ANDR-X SYSTEM</h1>", unsafe_allow_html=True)
    pwd = st.text_input("SECURITY CODE:", type="password") # Araka ny sary v1.8
    if st.button("ACTIVATE"):
        if pwd == "2026": # Tenimiafina raikitra
            st.session_state.auth = True
            st.rerun()
    st.stop()

# ---------------- ENGINE ----------------
def run_prediction(crash, h_tour, ref_val):
    try:
        t_obj = datetime.strptime(h_tour, "%H:%M:%S")
    except:
        t_obj = datetime.now()
        
    # Algorithm Predictive (Simple Ref)
    base_val = (crash * ref_val) + 1.3
    sims = np.random.lognormal(mean=np.log(base_val), sigma=0.42, size=15000)
    success_3x = [s for s in sims if s >= 3.0]
    
    # Fanamarihana (Note Box)
    note = ""
    if crash < 1.2: 
        note = "⚠️ FAMPITANDREMANA: Crash lava be (Serie Rouge). Miandrasa cycle manaraka!"
    elif crash > 10: 
        note = "🚀 CRASH AVO: Mety hisy 'Correction' na 'Rupture' ny cycle."
    else: 
        note = "✅ CYCLE ARA-DALANA: Afaka manaraka ny vinavina."

    # Kajy Heure d'entrée
    delay = 65 if crash < 2.0 else 115
    h_entree = (t_obj + timedelta(seconds=delay)).strftime("%H:%M:%S")
    
    return {
        "h_act": h_tour,
        "h_ent": h_entree,
        "ref": ref_val,
        "crash": crash,
        "prob": round((len(success_3x)/15000)*100, 1),
        "note": note,
        "min": "2.00",
        "moy": round(statistics.mean(sims), 2),
        "max": round(np.percentile(sims, 95), 2)
    }

# ---------------- INTERFACE ----------------
st.markdown("<h1 style='text-align:center;'>🚀 NEURAL TERMINAL v1.8</h1>", unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🚀 ANALYSE", "📜 HISTORIQUE", "📖 GUIDE"])

with t1:
    c1, c2, c3 = st.columns(3)
    with c1:
        c_in = st.number_input("Crash tour:", value=1.50, step=0.01)
    with c2:
        h_in = st.text_input("Ora (HH:mm:ss):", value=datetime.now().strftime("%H:%M:%S"))
    with c3:
        r_in = st.number_input("Référence:", value=1.50, step=0.01)
    
    if st.button("EXECUTER ANALYSE"):
        res = run_prediction(c_in, h_in, r_in)
        st.session_state.pred_log.append(res)
        st.rerun()

    if st.session_state.pred_log:
        curr = st.session_state.pred_log[-1]
        st.markdown(f"""
            <div class='terminal-card'>
                <div class='status-line'>TOUR: {curr['h_act']} | REF: {curr['ref']} | CRASH: {curr['crash']}x</div>
                <p style='color:#aaa; font-size:12px; margin:0;'>HEURE D'ENTRÉE PRÉVUE</p>
                <div class='main-time'>{curr['h_ent']}</div>
                <div style='color:#ffcc00; font-weight:bold; font-size:18px;'>PROBABILITÉ X3+: {curr['prob']}%</div>
                <div class='note-box'>{curr['note']}</div>
                
                <div class='grid-container'>
                    <div class='grid-item'><span class='label-x'>MIN</span><span class='val-x'>{curr['min']}x</span></div>
                    <div class='grid-item'><span class='label-x'>MOYEN</span><span class='val-x'>{curr['moy']}x</span></div>
                    <div class='grid-item'><span class='label-x'>MAX</span><span class='val-x'>{curr['max']}x</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

with t2:
    if st.session_state.pred_log:
        for p in reversed(st.session_state.pred_log):
            st.markdown(f"🕒 **{p['h_ent']}** | Crash: {p['crash']}x | {p['note']}")
    else: st.info("Tsy misy tantara.")

with t3:
    st.write("1. Ampidiro ny **Crash** farany.  \n2. Soraty ny **Ora** (HH:mm:ss).  \n3. Ampidiro ny **Référence** tokana.  \n4. Jereo ny **Note Box** mena raha misy loza.")

st.sidebar.markdown(f"**USER**: ANDR-X  \n**STATUS**: ONLINE  \n**VERSION**: 1.8")
