import streamlit as st
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytz, json
from pathlib import Path

st.set_page_config(page_title="JETX SNIPER X4", layout="wide", initial_sidebar_state="collapsed")
try:
    D = Path(__file__).parent / "jx_sniper_data"
except:
    D = Path.cwd() / "jx_sniper_data"
D.mkdir(exist_ok=True, parents=True)
HF = D/"h.json"; SF = D/"s.json"

def sj(p,d):
    try:
        with open(p,"w") as f: json.dump(d,f,indent=2)
    except: pass

def lj(p,d):
    try:
        if p.exists():
            with open(p) as f: return json.load(f)
    except: pass
    return d

TZ = pytz.timezone("Indian/Antananarivo")

# 💎 CSS TRÈS STYLÉ (Glassmorphism + Neon UI)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap');

/* Manafina ny header sy footer an'ny Streamlit mba ho madio ny app */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stApp {
    background: radial-gradient(circle at 50% 10%, #1a001a 0%, #05000a 60%, #000000 100%);
    color: #ffe8ff;
    font-family: 'Rajdhani', sans-serif;
}

/* Lohateny mietsika (Animated Gradient) */
.ttl {
    font-family: 'Orbitron';
    font-size: clamp(2rem, 8vw, 3.5rem);
    font-weight: 900;
    text-align: center;
    background: linear-gradient(90deg, #ff00ff, #ff0066, #ff6600, #ff00ff);
    background-size: 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: sh 3s linear infinite;
    margin-bottom: 0px;
    filter: drop-shadow(0px 4px 15px rgba(255, 0, 255, 0.4));
}
@keyframes sh {0%{background-position:0%} 100%{background-position:100%}}

.sub {
    text-align: center;
    color: #ff00ff;
    font-size: 0.9rem;
    letter-spacing: 0.4em;
    font-weight: 700;
    margin-bottom: 2rem;
    text-shadow: 0 0 10px rgba(255,0,255,0.5);
}

/* Glassmorphism Cards */
.card {
    background: linear-gradient(145deg, rgba(25, 0, 35, 0.6), rgba(10, 0, 15, 0.8));
    border: 1px solid rgba(255, 0, 255, 0.2);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(255,0,255,0.05);
    border-radius: 24px;
    padding: clamp(18px, 4vw, 26px);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #ff00ff, #ff6600, transparent);
    opacity: 0.7;
}

.etime {
    font-family: 'Orbitron';
    font-size: clamp(3.5rem, 12vw, 5.5rem);
    font-weight: 900;
    text-align: center;
    color: #ffffff;
    text-shadow: 0 0 20px #ff00ff, 0 0 40px #ff00ff, 0 0 80px #ff0066;
    margin: 10px 0;
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {0%,100%{transform:scale(1);} 50%{transform:scale(1.02);}}

.pct {
    font-size: clamp(3rem, 10vw, 4.5rem);
    font-weight: 900;
    font-family: 'Orbitron';
    text-align: center;
    color: #ff6600;
    text-shadow: 0 0 20px rgba(255, 102, 0, 0.6);
    margin: 0;
}

.x4big {
    font-size: clamp(3.5rem, 14vw, 6rem);
    font-weight: 900;
    font-family: 'Orbitron';
    text-align: center;
    background: linear-gradient(135deg, #ff00ff, #ff6600);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    filter: drop-shadow(0 0 25px rgba(255,0,255,0.5));
}

/* Signals */
.sig-u {text-align:center; font-family:'Orbitron'; font-size:1.4rem; font-weight:900; color:#fff; text-shadow:0 0 20px #ff00ff; background: rgba(255,0,255,0.1); padding:15px; border-radius:12px; border:1px solid #ff00ff;}
.sig-s {text-align:center; font-family:'Orbitron'; font-size:1.2rem; font-weight:700; color:#ff6600; background: rgba(255,102,0,0.1); padding:12px; border-radius:12px; border:1px solid #ff6600;}
.sig-w {text-align:center; font-family:'Orbitron'; font-size:1rem; color:#ffcc00; padding:10px; opacity:0.9;}
.sig-x {text-align:center; font-family:'Orbitron'; font-size:1rem; color:#888; padding:10px;}

/* Boxes and Tags */
.tbox {
    background: rgba(0,0,0,0.4);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 16px 10px;
    text-align: center;
    margin: 4px;
    transition: all 0.3s ease;
}
.tbox:hover { background: rgba(255,0,255,0.05); border-color: rgba(255,0,255,0.3); transform: translateY(-3px);}
.tv {font-size: 1.8rem; font-weight: 900; font-family: 'Orbitron'; text-shadow: 0 0 10px currentColor;}
.tl {font-size: 0.65rem; color: #aaaaaa; letter-spacing: 0.15em; font-weight: 700; margin-bottom: 5px;}
.ta {font-size: 0.8rem; color: #ffffff; background: rgba(255,255,255,0.1); border-radius: 20px; padding: 2px 8px; display: inline-block; margin-top: 5px;}

.tag {background: rgba(255,0,255,0.15); border: 1px solid rgba(255,0,255,0.4); border-radius: 20px; padding: 5px 12px; font-size: 0.8rem; display: inline-block; margin: 4px; color: #fff; font-weight:600;}
.tag-o {background: rgba(255,102,0,0.15); border: 1px solid rgba(255,102,0,0.4); border-radius: 20px; padding: 5px 12px; font-size: 0.8rem; display: inline-block; margin: 4px; color: #fff; font-weight:600;}

/* Custom Streamlit Inputs (Gaming Style) */
.stTextInput label, .stNumberInput label {
    color: #ff99ff !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    font-family: 'Orbitron' !important;
    letter-spacing: 0.05em;
}
div[data-baseweb="input"] > div {
    background-color: rgba(0, 0, 0, 0.5) !important;
    border: 1px solid rgba(255, 0, 255, 0.3) !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
}
div[data-baseweb="input"] > div:focus-within {
    border-color: #ff00ff !important;
    box-shadow: 0 0 15px rgba(255, 0, 255, 0.4) !important;
    background-color: rgba(20, 0, 30, 0.8) !important;
}
.stTextInput input, .stNumberInput input {
    color: #ffffff !important;
    font-weight: 700 !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 1.1rem !important;
}
.stTextInput input::placeholder {color: #666 !important;}

/* Ultra Stylish Buttons */
.stButton > button {
    background: linear-gradient(135deg, #cc00cc 0%, #ff0066 100%) !important;
    color: #ffffff !important;
    font-weight: 900 !important;
    font-family: 'Orbitron' !important;
    font-size: 1.1rem !important;
    letter-spacing: 0.1em !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 24px !important;
    box-shadow: 0 0 20px rgba(255, 0, 255, 0.4) !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase;
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 0 35px rgba(255, 0, 255, 0.7) !important;
    background: linear-gradient(135deg, #ff00ff 0%, #ff6600 100%) !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: rgba(10, 0, 15, 0.95) !important;
    border-right: 1px solid rgba(255,0,255,0.2) !important;
}
.sb {background: rgba(0,0,0,0.5); border: 1px solid rgba(255,0,255,0.2); border-radius: 16px; padding: 15px; text-align: center; margin-bottom: 10px;}
.sv {font-size: 1.8rem; font-weight: 900; font-family: 'Orbitron'; color: #ff00ff; text-shadow: 0 0 10px #ff00ff;}
.sl {font-size: 0.65rem; color: #888; letter-spacing: 0.15em; font-weight:700;}

</style>
""", unsafe_allow_html=True)

for k,v in [("auth",False),("H",lj(HF,[])),("S",lj(SF,{"t":0,"w":0,"l":0})),("R",None),("ck",0)]:
    if k not in st.session_state: st.session_state[k]=v

ST=["COLD","NORMAL","WARM","HOT"]
def s2st(c):
    if c<1.5: return "COLD"
    if c<2.5: return "NORMAL"
    if c<3.5: return "WARM"
    return "HOT"

def markov(h,lc):
    tr={s:{s2:1 for s2 in ST} for s in ST}
    cs=[x.get("lc",2.0) for x in h if x.get("lc")]
    for i in range(len(cs)-1):
        tr[s2st(cs[i])][s2st(cs[i+1])]+=1
    mx={s:{s2:tr[s][s2]/sum(tr[s].values()) for s2 in ST} for s in ST}
    cur=s2st(lc); hp=mx[cur].get("HOT",0)+mx[cur].get("WARM",0)
    return round(hp*100,1),cur

def bayes(h,base):
    lb=[x for x in h if x.get("res") in ["W","L"]]
    if len(lb)<3: return base
    rc=lb[-20:]; w=sum(1 for x in rc if x.get("res")=="W"); n=len(rc)
    lik=(w+1)/(n+2); pr=base/100
    po=(lik*pr)/((lik*pr)+((1-lik)*(1-pr))+1e-9)
    return round(min(95,max(25,po*100)),1)

def calc_entry(hn, bp4, str_, lc, last_time_str):
    try:
        parts = last_time_str.strip().split(":")
        h2,m2,s2 = (int(parts[0]),int(parts[1]),0) if len(parts)==2 else (int(parts[0]),int(parts[1]),int(parts[2]))
        now = datetime.now(TZ)
        bt = now.replace(hour=h2,minute=m2,second=s2,microsecond=0)
        if bt < now: bt += timedelta(days=1)
    except:
        bt = datetime.now(TZ)
    hv  = (hn % 60) - 30
    pb  = int((bp4 - 30) * 0.45)
    sb  = int((str_ - 50) * 0.25)
    cb  = int(lc * 3.0)
    sh  = max(20, min(100, 50 + hv + pb + sb + cb))
    return (bt + timedelta(seconds=sh)).strftime("%H:%M:%S"), sh

def engine(h_in, last_time, lc):
    fh = hashlib.sha512(h_in.encode()).hexdigest()
    hn = int(fh[:16], 16)
    np.random.seed(int((hn&0xFFFFFFFF)+(lc*1000))%(2**32))

    if lc<1.5:   bs,sg = 2.20,0.38
    elif lc<2.5: bs,sg = 2.12,0.34
    elif lc<3.5: bs,sg = 2.05,0.31
    else:        bs,sg = 1.98,0.28
    bs += (hn%200)/1100
    sg  = max(0.22, sg - lc*0.015)

    sm = np.random.lognormal(np.log(bs), sg, 500_000)

    p4   = round(float(np.mean(sm>=4.0))*100, 2)
    p45  = round(float(np.mean(sm>=4.5))*100, 2)
    p5   = round(float(np.mean(sm>=5.0))*100, 2)
    p6   = round(float(np.mean(sm>=6.0))*100, 2)
    p3   = round(float(np.mean(sm>=3.0))*100, 2)
    sx4  = sm[sm>=4.0]

    if len(sx4) > 0:
        t4min = round(float(np.percentile(sx4, 15)), 2)
        t4moy = round(float(np.percentile(sx4, 50)), 2)
        t4max = round(float(np.percentile(sx4, 85)), 2)
        acc4min = round(p4 * 0.85, 1)
        acc4moy = round(p4 * 0.50, 1)
        acc4max = round(p4 * 0.15, 1)
    else:
        t4min, t4moy, t4max = 4.0, 5.0, 7.0
        acc4min = acc4moy = acc4max = 5.0

    hp, cur = markov(st.session_state.H, lc)
    bp4 = bayes(st.session_state.H, p4 + (hp/100-0.5)*15)

    str_ = round(
        bp4*0.45 + p45*0.25 + p5*0.15 + p3*0.05 +
        (hn%200)/14 + (hp/100)*12, 1
    )
    str_ = max(25.0, min(99.0, str_))

    ent, sh = calc_entry(hn, bp4, str_, lc, last_time)

    if   str_>=90 and bp4>=28: sig,sc = "🎯🎯🎯 SNIPER X4+ — FIRE MAX!","sig-u"
    elif str_>=78 and bp4>=22: sig,sc = "🎯🎯 STRONG X4+ — FIRE!","sig-u"
    elif str_>=65 and bp4>=16: sig,sc = "🔥 X4+ POSSIBLE — GO","sig-s"
    elif str_>=52 and bp4>=11: sig,sc = "🟡 X4 WEAK — MICRO BET","sig-w"
    else:                      sig,sc = "⚠️ SKIP — NO X4 SIGNAL","sig-x"

    return {"lc":lc,"ent":ent,"sh":sh,"sig":sig,"sc":sc,
            "bp4":bp4,"p4":p4,"p45":p45,"p5":p5,"p6":p6,"p3":p3,
            "str":str_,"cur":cur,"hp":hp,
            "t4min":t4min,"t4moy":t4moy,"t4max":t4max,
            "acc4min":acc4min,"acc4moy":acc4moy,"acc4max":acc4max,
            "res":None,"hi":len(st.session_state.H)}

# LOGIN
if not st.session_state.auth:
    st.markdown("<div class='ttl'>🎯 JETX SNIPER X4</div>",unsafe_allow_html=True)
    st.markdown("<div class='sub'>MARKOV + BAYESIAN</div>",unsafe_allow_html=True)
    _,cb,_=st.columns([1,1.2,1])
    with cb:
        st.markdown("<div class='card'>",unsafe_allow_html=True)
        pw=st.text_input("🔑 MOT DE PASSE",type="password",placeholder="Entrez: JET2026")
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("🔓 ACTIVER SNIPER",use_container_width=True):
            if pw=="JET2026": st.session_state.auth=True; st.rerun()
            else: st.error("❌ Code incorrect")
        st.markdown("</div>",unsafe_allow_html=True)
    st.stop()

with st.sidebar:
    st.markdown("<h2 style='font-family:Orbitron;color:#ff00ff;text-align:center;'>🎯 STATS X4</h2>", unsafe_allow_html=True)
    S=st.session_state.S; t,w,l=S.get("t",0),S.get("w",0),S.get("l",0)
    wr=round(w/t*100,1) if t>0 else 0
    st.markdown(f"<div class='sb'><div class='sv'>{wr}%</div><div class='sl'>WIN RATE</div></div>",unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1: st.markdown(f"<div class='sb'><div class='sv' style='color:#00ff00;'>{w}</div><div class='sl'>WINS</div></div>",unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='sb'><div class='sv' style='color:#ff3333;'>{l}</div><div class='sl'>LOSS</div></div>",unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🗑️ RESET STATS",use_container_width=True):
        st.session_state.H=[];st.session_state.S={"t":0,"w":0,"l":0};st.session_state.R=None
        for f in [HF,SF]:
            try:
                if f.exists(): f.unlink()
            except: pass
        st.success("✅"); st.rerun()

st.markdown("<div class='ttl'>🎯 JETX SNIPER X4</div>",unsafe_allow_html=True)
st.markdown("<div class='sub'>BAYESIAN PREDICTION ENGINE</div>",unsafe_allow_html=True)
ci,co=st.columns([1,2],gap="large")

with ci:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    h_in  = st.text_input("🔐 SERVER HASH",placeholder="Ex: 7db8e0141...")
    lt_in = st.text_input("⏰ LAST TIME (HH:MM:SS)",placeholder="Ex: 20:22:24")
    lc    = st.number_input("📊 LAST COTE",value=1.88,step=0.01,format="%.2f")
    if   lc<1.5: sl,sc2="🔵 COLD","#4488ff"
    elif lc<2.5: sl,sc2="⚪ NORMAL","#aaaaaa"
    elif lc<3.5: sl,sc2="🟡 WARM","#ffcc00"
    else:        sl,sc2="🔴 HOT","#ff3366"
    st.markdown(f"<div style='text-align:center;margin:15px 0;'><span style='background:rgba(255,255,255,.1);border:1px solid {sc2};border-radius:12px;padding:6px 20px;color:{sc2};font-size:.9rem;font-weight:bold;'>{sl} ZONE</span></div>",unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    if st.button("🚀 LANCER L'ANALYSE",use_container_width=True):
        if h_in and lt_in:
            with st.spinner("🎯 Analyse en cours..."):
                r=engine(h_in.strip(),lt_in.strip(),lc)
            st.session_state.R=r
            st.session_state.H.append(dict(r))
            if len(st.session_state.H)>200: st.session_state.H.pop(0)
            sj(HF,st.session_state.H); st.session_state.ck+=1; st.rerun()
        else: st.error("❌ Veuillez remplir le Hash et l'Heure")
    st.markdown("</div>",unsafe_allow_html=True)

with co:
    r=st.session_state.R
    if r:
        st.markdown("<div class='card' style='padding-top:10px;'>",unsafe_allow_html=True)
        st.markdown(f"<div style='margin-bottom:20px;'><div class='{r['sc']}'>{r['sig']}</div></div>",unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;color:#aaaaaa;font-size:0.8rem;margin:0;font-weight:bold;letter-spacing:0.1em;'>ENTRY TIME (+{r['sh']}s)</p>",unsafe_allow_html=True)
        st.markdown(f"<div class='etime'>{r['ent']}</div>",unsafe_allow_html=True)
        
        st.markdown("<div class='x4big'>X4.00+</div>",unsafe_allow_html=True)
        st.markdown(f"<div class='pct'>{r['bp4']}%</div>",unsafe_allow_html=True)
        
        st.markdown(f"""<div style='text-align:center;margin:20px 0;'>
        <span class='tag'>🔄 {r['cur']}</span><span class='tag'>🔥 {r['hp']}%</span>
        <span class='tag'>💪 STR {r['str']}</span>
        <span class='tag-o'>X3: {r['p3']}%</span>
        <span class='tag-o'>X5: {r['p5']}%</span>
        </div>""",unsafe_allow_html=True)
        
        c1,c2,c3=st.columns(3)
        with c1: st.markdown(f"<div class='tbox'><div class='tl'>CIBLE MIN</div><div class='tv' style='color:#ff00ff;'>{r['t4min']}×</div><div class='ta'>{r['acc4min']}%</div></div>",unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='tbox' style='border-color:#ff6600;'><div class='tl'>CIBLE MOYENNE</div><div class='tv' style='color:#ff6600;'>{r['t4moy']}×</div><div class='ta' style='background:#ff660044;'>{r['acc4moy']}%</div></div>",unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='tbox'><div class='tl'>CIBLE MAX</div><div class='tv' style='color:#ffcc00;'>{r['t4max']}×</div><div class='ta'>{r['acc4max']}%</div></div>",unsafe_allow_html=True)
        
        st.markdown("<br>",unsafe_allow_html=True)
        cw,cl2=st.columns(2)
        with cw:
            if st.button("✅ WIN",use_container_width=True,key="bw"):
                idx=r.get("hi",-1)
                if 0<=idx<len(st.session_state.H): st.session_state.H[idx]["res"]="W"; sj(HF,st.session_state.H)
                st.session_state.S["t"]+=1; st.session_state.S["w"]+=1; sj(SF,st.session_state.S); st.rerun()
        with cl2:
            if st.button("❌ MISS",use_container_width=True,key="bl"):
                idx=r.get("hi",-1)
                if 0<=idx<len(st.session_state.H): st.session_state.H[idx]["res"]="L"; sj(HF,st.session_state.H)
                st.session_state.S["t"]+=1; st.session_state.S["l"]+=1; sj(SF,st.session_state.S); st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)
    else:
        st.markdown("<div class='card' style='min-height:500px;display:flex;flex-direction:column;align-items:center;justify-content:center;'><div class='x4big' style='font-size:4rem;opacity:0.1;filter:none;'>X4 SNIPER</div><div style='color:rgba(255,255,255,0.3);font-family:Orbitron;margin-top:20px;font-size:1.2rem;letter-spacing:0.2em;'>EN ATTENTE DE DONNÉES...</div></div>",unsafe_allow_html=True)
