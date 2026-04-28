import streamlit as st
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytz
import json
from pathlib import Path

st.set_page_config(page_title="JETX V20 BAYES", layout="wide", initial_sidebar_state="collapsed")

try:
    DATA_DIR = Path(__file__).parent / "jetx_v20_data"
except:
    DATA_DIR = Path.cwd() / "jetx_v20_data"
DATA_DIR.mkdir(exist_ok=True, parents=True)
HISTORY_FILE = DATA_DIR / "history.json"
STATS_FILE   = DATA_DIR / "stats.json"

def save_json(p,d):
    try:
        with open(p,"w",encoding="utf-8") as f: json.dump(d,f,indent=2)
    except: pass

def load_json(p,d):
    try:
        if p.exists():
            with open(p,"r",encoding="utf-8") as f: return json.load(f)
    except: pass
    return d

TZ = pytz.timezone("Indian/Antananarivo")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');

/* Fototra sy loko matanjaka ho an'ny soratra */
.stApp {
    background: radial-gradient(ellipse at 50% 0%,#1a0033 0%,#000008 60%,#001a1a 100%);
    color: #ffffff !important;
    font-family: 'Rajdhani', sans-serif;
}

.ttl {
    font-family: 'Orbitron';
    font-size: clamp(1.8rem, 7vw, 3rem);
    font-weight: 900;
    text-align: center;
    background: linear-gradient(90deg, #ff0066, #00ffcc, #ff0066);
    background-size: 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: sh 3s ease infinite;
    margin-bottom: 2px;
}

@keyframes sh { 0%, 100% { background-position: 0% } 50% { background-position: 100% } }

.glass {
    background: rgba(10,0,25,0.95); 
    border: 2px solid rgba(255,0,102,0.6);
    border-radius: 18px;
    padding: clamp(12px, 4vw, 22px);
    backdrop-filter: blur(15px);
    margin-bottom: 16px;
    color: #ffffff !important;
}

.entry {
    font-family: 'Orbitron';
    font-size: clamp(3rem, 12vw, 5rem);
    font-weight: 900;
    text-align: center;
    color: #ff0066;
    text-shadow: 0 0 35px #ff0066, 0 0 5px #ffffff;
    margin: 16px 0;
}

.prob {
    font-size: clamp(2.5rem, 10vw, 4rem);
    font-weight: 900;
    font-family: 'Orbitron';
    text-align: center;
    color: #00ffcc;
    text-shadow: 0 0 20px #00ffcc;
    margin: 10px 0;
}

.tbox { background: rgba(255,255,255,0.1); border-radius: 14px; padding: 14px; text-align:center; margin:4px; }
.tv { font-size: clamp(1.4rem, 5vw, 2.2rem); font-weight: 900; font-family: 'Orbitron'; color: #ffffff !important; }
.mbox { background: rgba(255,0,102,0.15); border: 1px solid rgba(255,0,102,0.4); border-radius: 10px; padding: 10px; text-align: center; margin: 4px 0; }
.mv { font-size: 1.4rem; font-weight: 900; font-family: 'Orbitron'; color: #ff0066; }

/* INPUT FIELD: Natao mazava tsara ny soratra fa tsy mangarahara */
.stTextInput input, .stNumberInput input {
    background: #000000 !important;
    border: 2px solid #ff0066 !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    border-radius: 11px !important;
    opacity: 1 !important; /* Mba tsy ho transparent ny soratra */
}

/* Natao mazava ny placeholder */
::placeholder {
    color: rgba(255, 255, 255, 0.5) !important;
    opacity: 1 !important;
}

.stButton>button {
    background: linear-gradient(135deg,#ff0066,#ff3399)!important;
    color: #ffffff !important;
    font-weight: 900 !important;
    text-shadow: 0px 1px 5px rgba(0,0,0,0.5);
    border-radius: 11px !important;
    height: 52px !important;
    width: 100% !important;
}

label p { color: #ffffff !important; font-weight: 700 !important; font-size: 1rem !important; }
</style>
""", unsafe_allow_html=True)

for k,v in [("auth",False),("history",load_json(HISTORY_FILE,[])),
            ("stats",load_json(STATS_FILE,{"total":0,"wins":0,"losses":0})),
            ("result",None),("ck",0)]:
    if k not in st.session_state: st.session_state[k]=v

# ============================================================
# MARKOV CHAIN
# ============================================================
STATES=["COLD","NORMAL","WARM","HOT"]

def cote_to_state(c):
    if c<1.5: return "COLD"
    if c<2.5: return "NORMAL"
    if c<3.5: return "WARM"
    return "HOT"

def build_markov(history):
    trans={s:{s2:1 for s2 in STATES} for s in STATES}
    cotes=[h.get("last_cote",2.0) for h in history if h.get("last_cote")]
    for i in range(len(cotes)-1):
        s1=cote_to_state(cotes[i]); s2=cote_to_state(cotes[i+1])
        trans[s1][s2]+=1
    return {s:{s2:trans[s][s2]/sum(trans[s].values()) for s2 in STATES} for s in STATES}

def markov_predict(history, last_cote):
    matrix=build_markov(history)
    cur=cote_to_state(last_cote)
    p=matrix[cur]
    hot_p=p.get("HOT",0)+p.get("WARM",0)
    return hot_p, cur

# ============================================================
# BAYESIAN
# ============================================================
def bayesian_update(history, base_prob):
    labeled=[h for h in history if h.get("res") in ["WIN","LOSS"]]
    if len(labeled)<3: return base_prob
    recent=labeled[-20:]
    hits=sum(1 for h in recent if h.get("res")=="WIN")
    total=len(recent)
    likelihood=(hits+1)/(total+2)
    prior=base_prob/100
    posterior=(likelihood*prior)/((likelihood*prior)+((1-likelihood)*(1-prior))+1e-9)
    return round(min(95,max(30,posterior*100)),1)

# ============================================================
# ENGINE
# ============================================================
def run_engine(hash_in, time_in, last_cote):
    h_hex=hashlib.sha512(hash_in.encode()).hexdigest()
    h_num=int(h_hex[:16],16)
    seed_val=int((h_num&0xFFFFFFFFFFFFFFFF)+int(last_cote*10000))
    np.random.seed(seed_val%(2**32))

    if last_cote<1.5:   base,sigma=2.12,0.24
    elif last_cote<2.5: base,sigma=2.06,0.21
    elif last_cote<3.5: base,sigma=2.00,0.19
    else:               base,sigma=1.96,0.18
    base+=(h_num%180)/1200; sigma-=last_cote*0.0022

    sims=np.random.lognormal(np.log(base),max(0.14,sigma),350_000)
    p3=round(float(np.mean(sims>=3.0))*100,2)
    p3_5=round(float(np.mean(sims>=3.5))*100,2)
    p4=round(float(np.mean(sims>=4.0))*100,2)
    tmin=max(2.00,round(float(np.percentile(sims,30)),2))
    tmoy=max(2.60,round(float(np.percentile(sims,50)),2))
    sx3=sims[sims>=3.0]
    tmax=max(3.00,round(float(np.percentile(sx3,85)),2)) if len(sx3)>0 else 3.80

    hot_p,cur=markov_predict(st.session_state.history,last_cote)
    markov_boost=(hot_p-0.5)*20
    bayes_p=bayesian_update(st.session_state.history,p3+markov_boost)

    strength=round(bayes_p*0.50+p3_5*0.20+p4*0.10+(h_num%200)/12+hot_p*15,1)
    strength=max(30.0,min(99.0,strength))

    now_mg=datetime.now(TZ)
    shift=max(20,min(110,48+(h_num%90)-45+int(strength*0.35)+int(last_cote*4)-int((48-bayes_p)*0.45)))
    entry=(now_mg+timedelta(seconds=shift)).strftime("%H:%M:%S")

    if strength>=88 and bayes_p>=44:   sig,sc="💎 ULTRA X3+","sig-u"
    elif strength>=76 and bayes_p>=36: sig,sc="🔥 STRONG X3+","sig-s"
    elif strength>=62 and bayes_p>=28: sig,sc="🟢 GOOD X3+","sig-s"
    else:                              sig,sc="⚠️ SKIP","sig-w"

    return {"hash":hash_in[:14]+"...","time":time_in,"last_cote":last_cote,
            "entry":entry,"signal":sig,"sig_class":sc,
            "p3":bayes_p,"p3_5":p3_5,"p4":p4,"strength":strength,
            "cur_state":cur,"hot_p":round(hot_p*100,1),
            "tmin":tmin,"tmoy":tmoy,"tmax":tmax,
            "hist_idx":len(st.session_state.history),"res":"PENDING"}

# ============================================================
# LOGIN
# ============================================================
if not st.session_state.auth:
    st.markdown("<div class='ttl'>🚀 JETX V20 BAYES</div>", unsafe_allow_html=True)
    _,cb,_=st.columns([1,1.2,1])
    with cb:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        pw=st.text_input("🔑 PASSWORD",type="password",placeholder="JET2026")
        if st.button("ACTIVER",use_container_width=True):
            if pw=="JET2026": st.session_state.auth=True; st.rerun()
            else: st.error("❌ Password diso")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# SIDEBAR
with st.sidebar:
    st.markdown("### 📊 STATS")
    s=st.session_state.stats
    tot,w,l=s.get("total",0),s.get("wins",0),s.get("losses",0)
    wr=round(w/tot*100,1) if tot>0 else 0
    st.markdown(f"<div class='mbox'><div class='mv'>{wr}%</div><div style='font-size:.6rem;color:#fff4'>WIN RATE</div></div>",unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1: st.markdown(f"<div class='mbox'><div class='mv'>{w}</div><div style='font-size:.58rem;color:#fff3'>WINS</div></div>",unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='mbox'><div class='mv'>{l}</div><div style='font-size:.58rem;color:#fff3'>LOSS</div></div>",unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🗑️ RESET",use_container_width=True):
        st.session_state.history=[]; st.session_state.stats={"total":0,"wins":0,"losses":0}
        st.session_state.result=None
        for f in [HISTORY_FILE,STATS_FILE]:
            try:
                if f.exists(): f.unlink()
            except: pass
        st.success("✅ Reset!"); st.rerun()

# MAIN
st.markdown("<div class='ttl'>🚀 JETX V20 BAYES</div>", unsafe_allow_html=True)

ci,co=st.columns([1,2],gap="medium")

with ci:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### 📥 INPUT DATA")
    # Novana ny Placeholder eto
    h_in=st.text_input("🔐 HASH SHA512", placeholder="ADIKAO_NY_HASH_SERVER_ETO")
    t_in=st.text_input("⏰ TIME (HH:MM:SS)", placeholder="SORATY_NY_ORA_ETO")
    lc=st.number_input("📊 LAST COTE", value=1.88, step=0.01, format="%.2f")
    
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("🚀 ANALYSER",use_container_width=True):
        if h_in and t_in:
            r=run_engine(h_in.strip(),t_in.strip(),lc)
            st.session_state.result=r
            st.session_state.history.append(dict(r))
            if len(st.session_state.history)>200: st.session_state.history.pop(0)
            save_json(HISTORY_FILE,st.session_state.history)
            st.session_state.ck+=1; st.rerun()
        else: st.error("HASH et TIME obligatoires")

with co:
    r=st.session_state.result
    if r:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown(f"<div class='{r['sig_class']}' style='font-size:2rem; font-weight:900;'>{r['signal']}</div>",unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#ffffff; margin-top:16px;'>▸ ENTRY TIME</p>",unsafe_allow_html=True)
        st.markdown(f"<div class='entry'>{r['entry']}</div>",unsafe_allow_html=True)
        st.markdown(f"<div class='prob'>{r['p3']}%</div>",unsafe_allow_html=True)
        
        c1,c2,c3=st.columns(3)
        with c1: st.markdown(f"<div class='tbox'><div style='color:#ffffff;'>MIN</div><div class='tv'>{r['tmin']}×</div></div>",unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='tbox'><div style='color:#ffffff;'>MOYEN</div><div class='tv'>{r['tmoy']}×</div></div>",unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='tbox'><div style='color:#ffffff;'>MAX</div><div class='tv'>{r['tmax']}×</div></div>",unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        cw,cl2=st.columns(2)
        with cw:
            if st.button("✅ WIN",use_container_width=True,key="bw"):
                idx=r.get("hist_idx",-1)
                if 0<=idx<len(st.session_state.history): st.session_state.history[idx]["res"]="WIN"; save_json(HISTORY_FILE,st.session_state.history)
                st.session_state.stats["total"]+=1; st.session_state.stats["wins"]+=1; save_json(STATS_FILE,st.session_state.stats); st.rerun()
        with cl2:
            if st.button("❌ LOSS",use_container_width=True,key="bl"):
                idx=r.get("hist_idx",-1)
                if 0<=idx<len(st.session_state.history): st.session_state.history[idx]["res"]="LOSS"; save_json(HISTORY_FILE,st.session_state.history)
                st.session_state.stats["total"]+=1; st.session_state.stats["losses"]+=1; save_json(STATS_FILE,st.session_state.stats); st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)
    else:
        st.markdown("""<div class='glass' style='min-height:380px;display:flex;align-items:center;justify-content:center;'>
        <div style='text-align:center;'><div style='font-size:3rem;'>🚀</div>
        <div style='color:#ffffff; font-family:Orbitron; margin-top:12px;'>EN ATTENTE...</div></div></div>""",unsafe_allow_html=True)

if st.session_state.history:
    st.markdown("---"); st.markdown("### 📜 LOGS")
    df=pd.DataFrame([{"Entry":h.get("entry",""),"X3%":h.get("p3",""),"State":h.get("cur_state",""),"Hot%":h.get("hot_p",""),"Res":h.get("res","PENDING")} for h in reversed(st.session_state.history[-10:])])
    st.dataframe(df,use_container_width=True,hide_index=True)

st.markdown("<div style='text-align:center;margin-top:30px;color:#fff1;font-size:.58rem;'>JETX V20 • MARKOV + BAYESIAN • 350K SIMS</div>",unsafe_allow_html=True)
