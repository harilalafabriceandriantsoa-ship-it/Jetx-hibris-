import streamlit as st
import numpy as np
import statistics
from datetime import datetime, timedelta

# ---------------- CONFIGURATION & STYLE ----------------
st.set_page_config(page_title="ANDR-X TERMINAL v1.4", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {background: #020202; color:#00ffcc; font-family: 'Orbitron', sans-serif;}
    
    /* Bloc Analyse Tokana */
    .terminal-box {
        background: linear-gradient(180deg, rgba(0, 255, 204, 0.15) 0%, rgba(0, 0, 0, 0.9) 100%);
        padding: 20px; border-radius: 20px;
        border: 2px solid #00ffcc; text-align: center;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.2);
    }
    
    .status-line { font-size: 11px; color: #888; margin-bottom: 10px; border-bottom: 1px solid #333; padding-bottom: 5px; }
    .label-mise { font-size: 13px; color: #fff; text-transform: uppercase; margin: 0; }
    .heure-big { font-size: 65px; font-weight: bold; color: #00ffcc; line-height: 1; margin: 5px 0; }
    .prob-text { font-size: 18px; color: #ffcc00; font-weight: bold; margin-bottom: 15px; }
    
    /* Grid ho an'ny Cotes */
    .cote-grid {
        display: grid; grid-template-columns: 1fr 1fr 1fr;
        gap: 8px; margin-top: 10px;
    }
    .cote-box { background: rgba(255,255,255,0.05); padding: 8px; border-radius: 10px; border: 1px solid #222; }
    .cote-lab { font-size: 10px; color: #00ffcc; display: block; }
    .cote-num { font-size: 15px; font-weight: bold; color: white; }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #00ffcc 0%, #0066ff 100%);
        color: white; border: none; border-radius: 10px; height: 45px; font-weight: bold; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- INITIALIZATION ----------------
if "history" not in st.session_state: st.session_state.history = []
if "logs" not in st.session_state: st.session_state.logs = []
if "auth" not in st.session_state: st.session_state.auth = False

# ---------------- LOGIN ----------------
if not st.session_state.auth:
    st.markdown("<br><h1 style='text-align:center;'>🔐 ACCESS CONTROL</h1>", unsafe_allow_html=True)
    pwd = st.text_input("SECURITY CODE:", type="password")
    if st.button("UNLOCK TERMINAL"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# ---------------- ENGINE ----------------
def get_analysis(data):
    avg = statistics.mean(data) if data else 1.8
    dev = statistics.stdev(data) if len(data) > 1 else 0.6
    sims = np.random.lognormal(mean=np.log(avg), sigma=dev * 0.4, size=15000)
    success = [s for s in sims if s >= 3.0]
    prob = (len(success) / len(sims)) * 100
    now = datetime.now()
    delay = 1 if (data and data[-1] < 2.0) else 2
    h_entree = (now + timedelta(minutes=delay)).strftime("%H:%M")
    
    return {
        "ora_izao": now.strftime("%H:%M:%S"),
        "ora_mise": h_entree,
        "prob": round(prob, 2),
        "ref": data[-1] if data else 0,
        "min": "2.00",
        "moy": round(statistics.mean(success), 2) if success else 3.0,
        "max": round(np.percentile(sims, 95), 2)
    }

# ---------------- UI ----------------
st.markdown("<h2 style='text-align:center;'>⚡ TERMINAL ANDR-X</h2>", unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🚀 ANALYSE", "📜 LOGS", "📖 GUIDE"])

with t1:
    val = st.number_input("Crash farany nivoaka:", min_value=1.0, step=0.01, format="%.2f")
    
    if st.button("EXECUTE PREDICTION"):
        st.session_state.history.append(val)
        res = get_analysis(st.session_state.history)
        st.session_state.logs.append(res)
        if len(st.session_state.history) > 15: st.session_state.history.pop(0)
        st.rerun()

    if st.session_state.logs:
        cur = st.session_state.logs[-1]
        st.markdown(f"""
            <div class='terminal-box'>
                <div class='status-line'>
                    TIME: {cur['ora_izao']} | REF CRASH: {cur['ref']}x
                </div>
                <p class='label-mise'>HEURE D'ENTRÉE (MISE)</p>
                <div class='heure-big'>{cur['ora_mise']}</div>
                <div class='prob-text'>VINTANA X3+: {cur['prob']}%</div>
                
                <div class='cote-grid'>
                    <div class='cote-box'>
                        <span class='cote-lab'>MIN</span>
                        <span class='cote-num'>{cur['min']}x</span>
                    </div>
                    <div class='cote-box'>
                        <span class='cote-lab'>MOYEN</span>
                        <span class='cote-num'>{cur['moy']}x</span>
                    </div>
                    <div class='cote-box'>
                        <span class='cote-lab'>MAX</span>
                        <span class='cote-num'>{cur['max']}x</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    if st.button("RESET MEMORY"):
        st.session_state.history = []
        st.session_state.logs = []
        st.rerun()

with t2:
    st.subheader("📜 Historique de Prédiction")
    if st.session_state.logs:
        for l in reversed(st.session_state.logs):
            st.markdown(f"""
            <div style='background:#111; padding:8px; border-radius:8px; margin-bottom:5px; border-left:3px solid #00ffcc;'>
                <small>{l['ora_izao']} | Ref: {l['ref']}x</small><br>
                <b>MISE: {l['ora_mise']}</b> | Prob: {l['prob']}% | Target: {l['moy']}x
            </div>
            """, unsafe_allow_html=True)

with t3:
    st.markdown("""
    ### 📖 Torolalana:
    1. **Input:** Ampidiro ny crash farany teo amin'ny JetX.
    2. **Analyse:** Ny 'Heure d'entrée' no ora hidiranao mise.
    3. **Target:** Mivoaha (Cashout) araka ny cotes **Min** na **Moyen**.
    4. **Logs:** Jereo ny tantaran'ny prédiction teo aloha.
    """)
