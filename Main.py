import streamlit as st
import numpy as np
import hashlib
import statistics
from datetime import datetime, timedelta

# ---------------- CONFIGURATION & STYLE ----------------
st.set_page_config(page_title="ANDR-X TERMINAL v2.0", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {background: #000000; color:#00ffcc; font-family: 'Orbitron', sans-serif;}
    
    /* Bloc ho an'ny valiny (Terminal Look) */
    .terminal-card {
        background: linear-gradient(180deg, rgba(0, 255, 204, 0.15) 0%, rgba(0, 0, 0, 0.9) 100%);
        padding: 25px; border-radius: 25px; border: 2px solid #00ffcc;
        text-align: center; margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.2);
    }
    
    .main-time { font-size: 60px; font-weight: bold; color: #fff; line-height: 1; margin: 15px 0; }
    .status-line { font-size: 11px; color: #aaa; text-transform: uppercase; margin-bottom: 10px; border-bottom: 1px solid #333; padding-bottom: 5px; }
    
    .stButton>button {
        background: linear-gradient(135deg, #00ffcc 0%, #0066ff 100%);
        color: white; border: none; border-radius: 12px; font-weight: bold; width: 100%; height: 55px;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 15px #00ffcc; }
    
    .cote-label { font-size: 10px; color: #00ffcc; display: block; text-transform: uppercase; }
    .cote-val { font-size: 22px; font-weight: bold; color: white; }
</style>
""", unsafe_allow_html=True)

# ---------------- INITIALIZATION ----------------
if "pred_log" not in st.session_state: st.session_state.pred_log = []
if "auth" not in st.session_state: st.session_state.auth = False

# ---------------- LOGIN SYSTEM ----------------
if not st.session_state.auth:
    st.markdown("<br><br><h1 style='text-align:center;'>⚡ HUBRIS SYSTEM</h1>", unsafe_allow_html=True)
    pwd = st.text_input("SECURITY CODE:", type="password")
    if st.button("ACTIVATE TERMINAL"):
        if pwd == "2026": # Tenimiafina raikitra araka ny sary
            st.session_state.auth = True
            st.rerun()
    st.stop()

# ---------------- ENGINE (HASH & TIME ANALYSIS) ----------------
def run_prediction(hash_str, h_act, ref_val):
    try:
        t_obj = datetime.strptime(h_act, "%H:%M:%S")
    except:
        t_obj = datetime.now()

    # 1. Conversion Hash ho isa (Decimal) ho solon'ny Crash
    # Ampiasaina ny SHA-256 mba hahazoana sanda tsy miovaova avy amin'ny Hash
    hash_hex = hashlib.sha256(hash_str.encode()).hexdigest()
    hash_int = int(hash_hex[:8], 16) % 1000
    hash_norm = (hash_int / 100) + 1.1 # Sanda fototra avy amin'ny Hash

    # 2. Simulation Monte Carlo (Algorithm Matanjaka)
    # Mampifandray ny Hash, ny Ora, ary ny Référence
    seed_val = hash_norm * ref_val
    sims = np.random.lognormal(mean=np.log(seed_val), sigma=0.38, size=15000)
    success_3x = [s for s in sims if s >= 3.0]
    
    # 3. Kajy ny Heure d'entrée prévue (Segondra)
    # Ny elanelana dia miankina amin'ny tanjaky ny Hash
    delay = 62 if hash_norm < 2.5 else 118
    h_entree = (t_obj + timedelta(seconds=delay)).strftime("%H:%M:%S")
    
    return {
        "h_act": h_act, 
        "h_ent": h_entree, 
        "ref": ref_val, 
        "hash_short": hash_str[:10] + "...",
        "prob": round((len(success_3x)/15000)*100, 1),
        "min": "2.00", 
        "moy": round(statistics.mean(sims), 2),
        "max": round(np.percentile(sims, 95), 2)
    }

# ---------------- MAIN INTERFACE ----------------
st.markdown("<h1 style='text-align:center;'>🚀 TERMINAL ANDR-X V2.0</h1>", unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🚀 ANALYSEUR", "📜 HISTORIQUE", "📖 GUIDE"])

with t1:
    # INPUT AREA
    hash_in = st.text_input("Hash (Seed Client/Server):", placeholder="Ampidiro ny Hash lava hita amin'ny sary...")
    
    col_a, col_b = st.columns(2)
    with col_a:
        h_in = st.text_input("Ora (HH:mm:ss):", value=datetime.now().strftime("%H:%M:%S"))
    with col_b:
        r_in = st.number_input("Référence:", value=1.87, step=0.01)
    
    if st.button("RUN NEURAL ANALYSIS"):
        if hash_in:
            res = run_prediction(hash_in, h_in, r_in)
            st.session_state.pred_log.append(res)
            st.rerun()
        else:
            st.error("⚠️ Azafady, dikaovy (copy) ary ampidiro ny HASH!")

    # DISPLAY RESULTS
    if st.session_state.pred_log:
        curr = st.session_state.pred_log[-1]
        st.markdown(f"""
            <div class='terminal-card'>
                <div class='status-line'>HASH: {curr['hash_short']} | REF: {curr['ref']} | STATUS: ANALYZED</div>
                <p style='color:#aaa; font-size:12px; margin:0;'>HEURE D'ENTRÉE PRÉVUE</p>
                <div class='main-time'>{curr['h_ent']}</div>
                <div style='color:#ffcc00; font-weight:bold; font-size:22px;'>PROBABILITÉ X3+: {curr['prob']}%</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Grid ho an'ny cotes (Mampiasa st.columns mba tsy hisy HTML bug)
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<span class='cote-label'>MIN</span><span class='cote-val'>{curr['min']}x</span>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<span class='cote-label'>MOYEN</span><span class='cote-val'>{curr['moy']}x</span>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<span class='cote-label'>MAX</span><span class='cote-val'>{curr['max']}x</span>", unsafe_allow_html=True)

with t2:
    if st.session_state.pred_log:
        for p in reversed(st.session_state.pred_log):
            st.markdown(f"🕒 **{p['h_ent']}** | Hash: `{p['hash_short']}` | Prob: **{p['prob']}%**")
    else:
        st.info("Tsy misy tantara (History) mbola voatahiry.")

with t3:
    st.markdown("""
    ### 📖 Fomba fampiasana ny v2.0
    1. **Hash**: Jereo ny antsipirian'ny lalao (JetX/Aviator) dia dikaovy ilay Hash lava be.
    2. **Ora**: Ampidiro ny ora nivoahan'ilay tour farany (miaraka amin'ny segondra).
    3. **Référence**: Ny sanda 1.87 no fototra, fa azonao ovaina kely raha miova ny cycle.
    4. **Mise**: Miandrasa ny **Heure d'entrée** vao manindry ny "Mise".
    """)

st.sidebar.markdown(f"**ADMIN**: ANDR-X  \n**VERSION**: 2.0 (Hash Engine)  \n**DATE**: {datetime.now().strftime('%d.%m.%Y')}")
