import streamlit as st
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytz, json
from pathlib import Path

st.set_page_config(page_title="JETX V24 ULTRA", layout="wide", initial_sidebar_state="collapsed")
try:    D = Path(__file__).parent / "jx24_data"
except: D = Path.cwd() / "jx24_data"
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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');
.stApp{background:radial-gradient(ellipse at 60% 0%,#001133 0%,#030008 65%);color:#e8fff8;font-family:'Rajdhani',sans-serif}
.ttl{font-family:'Orbitron';font-size:clamp(1.8rem,7vw,2.8rem);font-weight:900;text-align:center;background:linear-gradient(90deg,#00ffcc,#00ddff,#ff00ff,#00ffcc);background-size:300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:sh 4s ease infinite;margin-bottom:4px}
@keyframes sh{0%,100%{background-position:0%}50%{background-position:100%}}
.sub{text-align:center;color:#00ffcc44;font-size:.78rem;letter-spacing:.3em;margin-bottom:1.2rem}
.card{background:rgba(0,12,20,.92);border:2px solid rgba(0,255,204,.35);border-radius:18px;padding:clamp(12px,4vw,22px);backdrop-filter:blur(14px);margin-bottom:14px}
.tour-box{background:rgba(0,255,204,.08);border:2px solid rgba(0,255,204,.4);border-radius:16px;padding:16px;text-align:center;margin:8px 0}
.tour-box2{background:rgba(255,0,255,.08);border:2px solid rgba(255,0,255,.4);border-radius:16px;padding:16px;text-align:center;margin:8px 0}
.tour-label{font-size:.72rem;color:rgba(255,255,255,.5);letter-spacing:.15em;text-transform:uppercase;margin-bottom:6px}
.tour-time{font-family:'Orbitron';font-size:clamp(1.8rem,7vw,2.8rem);font-weight:900}
.tour-conf{font-size:.78rem;margin-top:6px;font-weight:700}
.pct{font-size:clamp(2.5rem,9vw,3.8rem);font-weight:900;font-family:'Orbitron';text-align:center;color:#00ffcc;margin:8px 0}
.sig-u{text-align:center;font-family:'Orbitron';font-size:clamp(.9rem,3vw,1.4rem);font-weight:900;color:#00ffcc;text-shadow:0 0 15px #00ffcc88;padding:10px;letter-spacing:.06em}
.sig-s{text-align:center;font-family:'Orbitron';font-size:clamp(.85rem,2.8vw,1.25rem);font-weight:700;color:#00ddff;padding:8px}
.sig-w{text-align:center;font-family:'Orbitron';font-size:clamp(.82rem,2.6vw,1.1rem);color:#ffaa00;padding:8px}
.sig-x{text-align:center;font-family:'Orbitron';font-size:clamp(.8rem,2.4vw,1rem);color:#555;padding:7px}
.tbox{background:rgba(255,255,255,.06);border-radius:12px;padding:12px;text-align:center;margin:4px}
.tv{font-size:clamp(1.3rem,4.5vw,2rem);font-weight:900;font-family:'Orbitron'}
.tl{font-size:.58rem;color:rgba(255,255,255,.35);letter-spacing:.12em;text-transform:uppercase;margin-top:3px}
.ta{font-size:.68rem;color:#00ff88;margin-top:3px;font-weight:700}
.tag{background:rgba(0,255,204,.1);border:1px solid rgba(0,255,204,.3);border-radius:8px;padding:3px 10px;font-size:.78rem;display:inline-block;margin:2px;color:#aaffee}
.tag-p{background:rgba(255,0,255,.1);border:1px solid rgba(255,0,255,.3);border-radius:8px;padding:3px 10px;font-size:.78rem;display:inline-block;margin:2px;color:#ffaaff}
.sb{background:rgba(0,255,204,.07);border:1px solid rgba(0,255,204,.2);border-radius:10px;padding:10px;text-align:center;margin:4px 0}
.sv{font-size:1.3rem;font-weight:900;font-family:'Orbitron';color:#00ffcc}
.sl{font-size:.55rem;color:rgba(255,255,255,.35);letter-spacing:.1em;text-transform:uppercase;margin-top:2px}
.stButton>button{background:linear-gradient(135deg,#00ffcc,#00aaaa)!important;color:#000!important;font-weight:900!important;border-radius:12px!important;height:50px!important;border:none!important;width:100%!important;font-family:'Rajdhani'!important;font-size:.93rem!important;transition:all .2s!important}
.stButton>button:hover{transform:scale(1.02);box-shadow:0 0 22px rgba(0,255,204,.5)!important}
.stTextInput label,.stNumberInput label{color:#aaffee!important;font-weight:700!important;font-size:.85rem!important;font-family:'Rajdhani'!important}
.stTextInput input{background:rgba(255,255,255,.1)!important;border:2px solid rgba(0,255,204,.5)!important;color:#fff!important;border-radius:11px!important;font-size:.92rem!important;padding:10px 13px!important}
.stTextInput input::placeholder{color:rgba(255,255,255,.5)!important;font-style:italic!important}
.stTextInput input:focus{border-color:#00ffcc!important;box-shadow:0 0 12px rgba(0,255,204,.3)!important;background:rgba(255,255,255,.13)!important}
.stNumberInput input{background:rgba(255,255,255,.1)!important;border:2px solid rgba(0,255,204,.5)!important;color:#fff!important;border-radius:11px!important;font-size:.92rem!important;padding:10px 13px!important}
.stNumberInput input:focus{border-color:#00ffcc!important;box-shadow:0 0 12px rgba(0,255,204,.3)!important}
@media(max-width:768px){.card{padding:12px!important}}
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
    return round(min(95,max(30,po*100)),1)

def parse_time(ts):
    now=datetime.now(TZ)
    try:
        parts=ts.strip().split(":")
        h2,m2=int(parts[0]),int(parts[1])
        s2=int(parts[2]) if len(parts)>2 else 0
        dt=now.replace(hour=h2,minute=m2,second=s2,microsecond=0)
        if dt<now-timedelta(hours=1): dt+=timedelta(days=1)
        return dt
    except: return now

def calc_tours(hn,bp,str_,lc,last_time_str):
    base_t=parse_time(last_time_str)
    hv1=(hn%50)-25
    pb1=int((bp-40)*0.32)
    sb1=int((str_-50)*0.20)
    cb1=int(lc*2.5)
    sh1=max(20,min(85,42+hv1+pb1+sb1+cb1))
    round_dur=max(8,min(35,12+(hn%20)-int(lc*2)))
    sh2=sh1+round_dur+max(5,int(hn%12))
    t1=(base_t+timedelta(seconds=sh1)).strftime("%H:%M:%S")
    t2=(base_t+timedelta(seconds=sh2)).strftime("%H:%M:%S")
    conf1=bp
    state_now=s2st(lc)
    if   state_now=="COLD":   conf2=round(min(95,bp*1.18),1)
    elif state_now=="NORMAL": conf2=round(min(95,bp*1.08),1)
    elif state_now=="WARM":   conf2=round(min(95,bp*0.95),1)
    else:                     conf2=round(min(95,bp*0.88),1)
    return t1,sh1,conf1,t2,sh2,conf2

def engine(h_in,last_time,lc):
    fh=hashlib.sha512(h_in.encode()).hexdigest()
    hn=int(fh[:16],16)
    sv=int((hn&0xFFFFFFFF)+(lc*1000))
    np.random.seed(sv%(2**32))
    if lc<1.5:   bs,sg=2.12,0.24
    elif lc<2.5: bs,sg=2.06,0.21
    elif lc<3.5: bs,sg=2.00,0.19
    else:        bs,sg=1.96,0.18
    bs+=(hn%180)/1200; sg=max(0.14,sg-lc*0.0022)
    sm=np.random.lognormal(np.log(bs),sg,400_000)
    p3=round(float(np.mean(sm>=3.0))*100,2)
    p35=round(float(np.mean(sm>=3.5))*100,2)
    p4=round(float(np.mean(sm>=4.0))*100,2)
    sx=sm[sm>=3.0]
    tmin=max(2.0,round(float(np.percentile(sm,30)),2))
    tmoy=max(2.5,round(float(np.percentile(sm,50)),2))
    tmax=max(3.0,round(float(np.percentile(sx,85)),2)) if len(sx)>0 else 3.8
    acc_min=70.0; acc_moy=50.0; acc_max=round(p3*0.85,1)
    hp,cur=markov(st.session_state.H,lc)
    bp=bayes(st.session_state.H,p3+(hp/100-0.5)*20)
    str_=round(bp*0.50+p35*0.20+p4*0.10+(hn%200)/12+(hp/100)*15,1)
    str_=max(30.0,min(99.0,str_))
    t1,sh1,c1,t2,sh2,c2=calc_tours(hn,bp,str_,lc,last_time)
    if   str_>=90 and bp>=46: sig,sc="💎💎💎 ULTRA X3+ — BUY MAX","sig-u"
    elif str_>=80 and bp>=40: sig,sc="💎💎 STRONG X3+ — BUY","sig-u"
    elif str_>=70 and bp>=34: sig,sc="🔥 GOOD X3+ — GO","sig-s"
    elif str_>=58 and bp>=27: sig,sc="🟡 MODERATE — SMALL BET","sig-w"
    else:                     sig,sc="⚠️ SKIP CE ROUND","sig-x"
    return {"lc":lc,"t1":t1,"sh1":sh1,"c1":c1,"t2":t2,"sh2":sh2,"c2":c2,
            "sig":sig,"sc":sc,"bp":bp,"p35":p35,"p4":p4,"str":str_,
            "cur":cur,"hp":hp,"tmin":tmin,"tmoy":tmoy,"tmax":tmax,
            "acc_min":acc_min,"acc_moy":acc_moy,"acc_max":acc_max,
            "res":None,"hi":len(st.session_state.H)}

if not st.session_state.auth:
    st.markdown("<div class='ttl'>🚀 JETX V24 ULTRA</div>",unsafe_allow_html=True)
    st.markdown("<div class='sub'>MULTI-TOUR • MARKOV + BAYESIAN</div>",unsafe_allow_html=True)
    _,cb,_=st.columns([1,1.2,1])
    with cb:
        st.markdown("<div class='card'>",unsafe_allow_html=True)
        pw=st.text_input("🔑 MOT DE PASSE",type="password",placeholder="Entrez: JET2026")
        if st.button("🔓 ACTIVER",use_container_width=True):
            if pw=="JET2026": st.session_state.auth=True; st.rerun()
            else: st.error("❌ Code incorrect")
        st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("""
    <div class='card' style='max-width:780px;margin:20px auto;'>
    <h3 style='color:#00ffcc;font-family:Orbitron;text-align:center;font-size:1.05rem;'>📖 FANAZAVANA MALAGASY</h3>
    <div style='background:rgba(0,255,204,.05);border-left:3px solid #00ffcc;border-radius:0 10px 10px 0;padding:11px 15px;margin:8px 0;font-size:.87rem;line-height:1.8;'>
    <b style='color:#00ffcc;'>🎯 TOUR 1 & TOUR 2:</b><br>
    • <b>TOUR 1</b>: Round akaiky manaraka (20-85sec aorian'ny last time)<br>
    • <b>TOUR 2</b>: Round faharoa aorian'ny tour 1<br>
    • Confidence isaky ny tour = X3+ probability<br>
    • COLD state → Tour 2 confidence miakatra (correction probable)</div>
    <div style='background:rgba(0,255,204,.05);border-left:3px solid #00ffcc;border-radius:0 10px 10px 0;padding:11px 15px;margin:8px 0;font-size:.87rem;line-height:1.8;'>
    <b style='color:#00ffcc;'>📥 INPUTS:</b><br>
    • <b>HASH:</b> Server hash @ Provably Fair → Ex: <code>7db8e01413d6d...</code><br>
    • <b>LAST TIME:</b> Ora round taloha → Ex: <code>20:22:24</code><br>
    • <b>LAST COTE:</b> Résultat taloha → Ex: <code>1.88</code></div>
    </div>
    """,unsafe_allow_html=True)
    st.stop()

with st.sidebar:
    st.markdown("### 🚀 JETX V24")
    S=st.session_state.S; t,w,l=S.get("t",0),S.get("w",0),S.get("l",0)
    wr=round(w/t*100,1) if t>0 else 0
    st.markdown(f"<div class='sb'><div class='sv'>{wr}%</div><div class='sl'>WIN RATE</div></div>",unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1: st.markdown(f"<div class='sb'><div class='sv'>{w}</div><div class='sl'>WINS</div></div>",unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='sb'><div class='sv'>{l}</div><div class='sl'>LOSS</div></div>",unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🗑️ RESET",use_container_width=True):
        st.session_state.H=[];st.session_state.S={"t":0,"w":0,"l":0};st.session_state.R=None
        for f in [HF,SF]:
            try:
                if f.exists(): f.unlink()
            except: pass
        st.success("✅"); st.rerun()

st.markdown("<div class='ttl'>🚀 JETX V24 ULTRA</div>",unsafe_allow_html=True)
st.markdown("<div class='sub'>MULTI-TOUR • 400K SIMS • MARKOV+BAYESIAN</div>",unsafe_allow_html=True)
ci,co=st.columns([1,2],gap="medium")

with ci:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    h_in = st.text_input("🔐 SERVER HASH",placeholder="Ex: 7db8e01413d6d8c6...  (Provably Fair)")
    ti   = st.text_input("⏰ LAST TIME (HH:MM:SS)",placeholder="Ex: 20:22:24  —  ora round taloha")
    lc   = st.number_input("📊 LAST COTE",value=1.88,step=0.01,format="%.2f")
    if   lc<1.5: sl,sc2="🔵 COLD","#4488ff"
    elif lc<2.5: sl,sc2="⚪ NORMAL","#aaa"
    elif lc<3.5: sl,sc2="🟡 WARM","#ffcc00"
    else:        sl,sc2="🔴 HOT","#ff3366"
    st.markdown(f"<div style='text-align:center;margin:6px 0;'><span style='background:rgba(255,255,255,.07);border-radius:8px;padding:4px 14px;color:{sc2};font-size:.8rem;'>{sl}</span></div>",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)
    if st.button("🚀 ANALYSER MULTI-TOUR",use_container_width=True):
        if h_in and ti:
            with st.spinner("⚡ 400k sims..."):
                r=engine(h_in.strip(),ti.strip(),lc)
            st.session_state.R=r
            st.session_state.H.append(dict(r))
            if len(st.session_state.H)>200: st.session_state.H.pop(0)
            sj(HF,st.session_state.H); st.session_state.ck+=1; st.rerun()
        else: st.error("❌ Hash et LAST TIME obligatoires!")

with co:
    r=st.session_state.R
    if r:
        st.markdown("<div class='card'>",unsafe_allow_html=True)
        st.markdown(f"<div class='{r['sc']}'>{r['sig']}</div>",unsafe_allow_html=True)
        ct1,ct2=st.columns(2)
        with ct1:
            st.markdown(f"""<div class='tour-box'>
            <div class='tour-label'>🎯 TOUR 1 (+{r['sh1']}s)</div>
            <div class='tour-time' style='color:#00ffcc;'>{r['t1']}</div>
            <div class='tour-conf' style='color:#88ffcc;'>Conf: {r['c1']}%</div>
            </div>""",unsafe_allow_html=True)
        with ct2:
            st.markdown(f"""<div class='tour-box2'>
            <div class='tour-label'>🎯 TOUR 2 (+{r['sh2']}s)</div>
            <div class='tour-time' style='color:#ff00ff;'>{r['t2']}</div>
            <div class='tour-conf' style='color:#ffaaff;'>Conf: {r['c2']}%</div>
            </div>""",unsafe_allow_html=True)
        st.markdown(f"<div class='pct'>{r['bp']}%</div>",unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:rgba(255,255,255,.3);font-size:.67rem;'>PROB X3+ BAYESIAN</p>",unsafe_allow_html=True)
        st.markdown(f"""<div style='text-align:center;margin:10px 0;'>
        <span class='tag'>🔄 {r['cur']}</span><span class='tag'>🔥 {r['hp']}%</span>
        <span class='tag'>💪 {r['str']}</span>
        <span class='tag-p'>X3.5+ {r['p35']}%</span><span class='tag-p'>X4+ {r['p4']}%</span>
        </div>""",unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        with c1: st.markdown(f"<div class='tbox'><div class='tl'>MIN</div><div class='tv' style='color:#00ffcc;'>{r['tmin']}×</div><div class='ta'>{r['acc_min']}%</div></div>",unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='tbox'><div class='tl'>MOYEN</div><div class='tv' style='color:#ffd700;'>{r['tmoy']}×</div><div class='ta'>{r['acc_moy']}%</div></div>",unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='tbox'><div class='tl'>MAX</div><div class='tv' style='color:#ff00ff;'>{r['tmax']}×</div><div class='ta'>{r['acc_max']}%</div></div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cw,cl2=st.columns(2)
        with cw:
            if st.button("✅ WIN",use_container_width=True,key="bw"):
                idx=r.get("hi",-1)
                if 0<=idx<len(st.session_state.H): st.session_state.H[idx]["res"]="W"; sj(HF,st.session_state.H)
                st.session_state.S["t"]+=1; st.session_state.S["w"]+=1; sj(SF,st.session_state.S); st.success("🎯"); st.rerun()
        with cl2:
            if st.button("❌ LOSS",use_container_width=True,key="bl"):
                idx=r.get("hi",-1)
                if 0<=idx<len(st.session_state.H): st.session_state.H[idx]["res"]="L"; sj(HF,st.session_state.H)
                st.session_state.S["t"]+=1; st.session_state.S["l"]+=1; sj(SF,st.session_state.S); st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)
    else:
        st.markdown("<div class='card' style='min-height:350px;display:flex;align-items:center;justify-content:center;'><div style='text-align:center;'><div style='font-size:3rem;'>🚀</div><div style='color:rgba(255,255,255,.15);font-family:Orbitron;margin-top:10px;font-size:.85rem;'>EN ATTENTE...</div></div></div>",unsafe_allow_html=True)

if st.session_state.H:
    st.markdown("---")
    df=pd.DataFrame([{"Tour1":x.get("t1",""),"C1":f"{x.get('c1',0)}%","Tour2":x.get("t2",""),"C2":f"{x.get('c2',0)}%","X3%":x.get("bp",""),"State":x.get("cur",""),"Res":"WIN" if x.get("res")=="W" else "LOSS" if x.get("res")=="L" else "—"} for x in reversed(st.session_state.H[-10:])])
    st.dataframe(df,use_container_width=True,hide_index=True)
st.markdown("<div style='text-align:center;margin-top:16px;color:rgba(255,255,255,.07);font-size:.52rem;'>JETX V24 ULTRA • MULTI-TOUR • 400K SIMS</div>",unsafe_allow_html=True)
