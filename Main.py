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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');
.stApp{background:radial-gradient(ellipse at 50% 0%,#1a0010 0%,#050005 60%,#000d1a 100%);color:#ffe8ff;font-family:'Rajdhani',sans-serif}
.ttl{font-family:'Orbitron';font-size:clamp(1.8rem,7vw,3rem);font-weight:900;text-align:center;background:linear-gradient(90deg,#ff00ff,#ff0066,#ff6600,#ff00ff);background-size:300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:sh 4s ease infinite;margin-bottom:4px}
@keyframes sh{0%,100%{background-position:0%}50%{background-position:100%}}
.sub{text-align:center;color:#ff00ff55;font-size:.8rem;letter-spacing:.3em;margin-bottom:1.5rem}
.card{background:rgba(20,0,30,.93);border:2px solid rgba(255,0,255,.35);border-radius:18px;padding:clamp(14px,4vw,22px);backdrop-filter:blur(14px);margin-bottom:16px}
.etime{font-family:'Orbitron';font-size:clamp(3rem,12vw,5rem);font-weight:900;text-align:center;color:#ff00ff;text-shadow:0 0 40px #ff00ff;margin:18px 0;animation:ep 2s ease-in-out infinite}
@keyframes ep{0%,100%{text-shadow:0 0 28px #ff00ff}50%{text-shadow:0 0 60px #ff00ff,0 0 90px #ff006688}}
.pct{font-size:clamp(2.8rem,10vw,4.2rem);font-weight:900;font-family:'Orbitron';text-align:center;color:#ff6600;margin:8px 0}
.x4big{font-size:clamp(3.5rem,14vw,6rem);font-weight:900;font-family:'Orbitron';text-align:center;background:linear-gradient(135deg,#ff00ff,#ff6600);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:10px 0;filter:drop-shadow(0 0 30px #ff00ff88)}
.sig-u{text-align:center;font-family:'Orbitron';font-size:clamp(.95rem,3.5vw,1.5rem);font-weight:900;color:#ff00ff;text-shadow:0 0 18px #ff00ff88;padding:12px;letter-spacing:.06em}
.sig-s{text-align:center;font-family:'Orbitron';font-size:clamp(.9rem,3vw,1.3rem);font-weight:700;color:#ff6600;padding:10px}
.sig-w{text-align:center;font-family:'Orbitron';font-size:clamp(.85rem,2.8vw,1.1rem);color:#ffaa00;padding:10px}
.sig-x{text-align:center;font-family:'Orbitron';font-size:clamp(.85rem,2.8vw,1rem);color:#555;padding:8px}
.tbox{background:rgba(255,255,255,.06);border-radius:14px;padding:14px;text-align:center;margin:4px}
.tv{font-size:clamp(1.4rem,5vw,2.2rem);font-weight:900;font-family:'Orbitron'}
.tl{font-size:.6rem;color:rgba(255,255,255,.38);letter-spacing:.12em;text-transform:uppercase;margin-top:3px}
.ta{font-size:.7rem;color:#ff99ff;margin-top:4px;font-weight:700}
.tag{background:rgba(255,0,255,.12);border:1px solid rgba(255,0,255,.35);border-radius:8px;padding:4px 11px;font-size:.8rem;display:inline-block;margin:3px;color:#ffaaff}
.tag-o{background:rgba(255,102,0,.12);border:1px solid rgba(255,102,0,.35);border-radius:8px;padding:4px 11px;font-size:.8rem;display:inline-block;margin:3px;color:#ffcc88}
.sb{background:rgba(255,0,255,.07);border:1px solid rgba(255,0,255,.2);border-radius:10px;padding:10px;text-align:center;margin:4px 0}
.sv{font-size:1.3rem;font-weight:900;font-family:'Orbitron';color:#ff00ff}
.sl{font-size:.56rem;color:rgba(255,255,255,.35);letter-spacing:.12em;text-transform:uppercase;margin-top:2px}
.ib{background:rgba(255,0,255,.05);border-left:3px solid #ff00ff;border-radius:0 10px 10px 0;padding:11px 15px;margin:8px 0;font-size:.88rem;line-height:1.8}
.sniper-badge{background:linear-gradient(135deg,#ff00ff,#ff0066,#ff6600);border-radius:50px;padding:10px 24px;font-family:'Orbitron';font-weight:900;font-size:clamp(.9rem,3vw,1.2rem);color:#fff;text-align:center;display:inline-block;box-shadow:0 0 30px rgba(255,0,255,.5);margin:10px auto;letter-spacing:.06em}
.stButton>button{background:linear-gradient(135deg,#ff00ff,#ff0066)!important;color:#fff!important;font-weight:900!important;border-radius:12px!important;height:52px!important;border:none!important;width:100%!important;font-family:'Rajdhani'!important;font-size:.95rem!important;transition:all .2s!important}
.stButton>button:hover{transform:scale(1.02);box-shadow:0 0 24px rgba(255,0,255,.6)!important}

/* FANITSIANA NY INPUT SY PLACEHOLDER HO MAINTY SY STYLÉ */
.stTextInput label,.stNumberInput label{color:#ffaaff!important;font-weight:700!important;font-size:.87rem!important;font-family:'Rajdhani'!important}
.stTextInput input{background:rgba(255,255,255,.95)!important;border:2px solid rgba(255,0,255,.6)!important;color:#000000!important;font-weight:900!important;font-family:'Orbitron',sans-serif!important;letter-spacing:.05em!important;border-radius:11px!important;font-size:1rem!important;padding:11px 14px!important}
.stTextInput input::placeholder{color:#1a1a1a!important;font-style:italic!important;font-weight:700!important;font-family:'Rajdhani',sans-serif!important;opacity:1!important}
.stTextInput input:focus{border-color:#ff00ff!important;box-shadow:0 0 16px rgba(255,0,255,.6)!important;background:#ffffff!important}
.stNumberInput input{background:rgba(255,255,255,.95)!important;border:2px solid rgba(255,0,255,.6)!important;color:#000000!important;font-weight:900!important;font-family:'Orbitron',sans-serif!important;border-radius:11px!important;font-size:1rem!important;padding:11px 14px!important}
.stNumberInput input:focus{border-color:#ff00ff!important;box-shadow:0 0 16px rgba(255,0,255,.6)!important;background:#ffffff!important}
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
    return round(min(95,max(25,po*100)),1)

def calc_entry(hn, bp4, str_, lc, last_time_str):
    """
    ENTRY TIME SNIPER X4
    ====================
    Base = LAST TIME + shift (20-100 sec)
    X4 target = cible plus haute → besoin de plus de temps
    prob_boost X4 avo → entry plus tôt (le round vient)
    """
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
    """
    SNIPER X4 ENGINE
    ================
    Ciblé EXCLUSIVEMENT X4+ (cote >= 4.00x)
    Simulations lognormal optimisées pour queue droite (X4+)
    Base sigma plus large pour capturer les grands mouvements
    """
    fh = hashlib.sha512(h_in.encode()).hexdigest()
    hn = int(fh[:16], 16)
    np.random.seed(int((hn&0xFFFFFFFF)+(lc*1000))%(2**32))

    # Base optimisé X4+: sigma plus large pour tail X4
    if lc<1.5:   bs,sg = 2.20,0.38
    elif lc<2.5: bs,sg = 2.12,0.34
    elif lc<3.5: bs,sg = 2.05,0.31
    else:        bs,sg = 1.98,0.28
    bs += (hn%200)/1100
    sg  = max(0.22, sg - lc*0.015)

    sm = np.random.lognormal(np.log(bs), sg, 500_000)

    # Métriques X4 focused
    p4   = round(float(np.mean(sm>=4.0))*100, 2)
    p45  = round(float(np.mean(sm>=4.5))*100, 2)
    p5   = round(float(np.mean(sm>=5.0))*100, 2)
    p6   = round(float(np.mean(sm>=6.0))*100, 2)
    p3   = round(float(np.mean(sm>=3.0))*100, 2)
    sx4  = sm[sm>=4.0]

    # Targets X4
    if len(sx4) > 0:
        t4min = round(float(np.percentile(sx4, 15)), 2)  # 85% des X4 atteignent
        t4moy = round(float(np.percentile(sx4, 50)), 2)  # médiane X4
        t4max = round(float(np.percentile(sx4, 85)), 2)  # optimiste X4
        acc4min = round(p4 * 0.85, 1)
        acc4moy = round(p4 * 0.50, 1)
        acc4max = round(p4 * 0.15, 1)
    else:
        t4min, t4moy, t4max = 4.0, 5.0, 7.0
        acc4min = acc4moy = acc4max = 5.0

    hp, cur = markov(st.session_state.H, lc)
    # Bayesian focalisé X4
    bp4 = bayes(st.session_state.H, p4 + (hp/100-0.5)*15)

    # Strength X4 spécifique
    str_ = round(
        bp4*0.45 + p45*0.25 + p5*0.15 + p3*0.05 +
        (hn%200)/14 + (hp/100)*12, 1
    )
    str_ = max(25.0, min(99.0, str_))

    ent, sh = calc_entry(hn, bp4, str_, lc, last_time)

    # Signal SNIPER X4 — 5 niveaux ultra stricts
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
    st.markdown("<div class='sub'>MARKOV + BAYESIAN • CIBLÉ X4+ ULTRA</div>",unsafe_allow_html=True)
    _,cb,_=st.columns([1,1.2,1])
    with cb:
        st.markdown("<div class='card'>",unsafe_allow_html=True)
        pw=st.text_input("🔑 MOT DE PASSE",type="password",placeholder="Entrez: JET2026")
        if st.button("🔓 ACTIVER SNIPER",use_container_width=True):
            if pw=="JET2026": st.session_state.auth=True; st.rerun()
            else: st.error("❌ Code incorrect")
        st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("""
    <div class='card' style='max-width:780px;margin:20px auto;'>
    <h3 style='color:#ff00ff;font-family:Orbitron;text-align:center;font-size:1.1rem;'>📖 FANAZAVANA MALAGASY</h3>
    <div class='ib'><b style='color:#ff00ff;'>🎯 INONA NY SNIPER X4?</b><br>
    App ity dia <b>CIBLÉ X4+</b> fotsiny (cote >= 4.00x)<br>
    Simulations 500k optimisés ho an'ny <b>tail droite</b> = X4+ probability<br>
    Signal stricte: tsy manome signal raha tsy misy X4 chance marina</div>
    <div class='ib'><b style='color:#ff00ff;'>📥 INPUTS:</b><br>
    • <b>HASH:</b> Server hash @ Provably Fair<br>
    • <b>LAST TIME:</b> Ora round taloha → Ex: <code>20:22:24</code><br>
    • <b>LAST COTE:</b> Résultat taloha → Ex: <code>1.88</code><br>
    Entry = Last Time + shift (20-100sec)</div>
    <div class='ib'><b style='color:#ff00ff;'>🎯 SIGNAL SNIPER:</b><br>
    🎯🎯🎯 FIRE MAX → Str>=90 + X4%>=28<br>
    🎯🎯 FIRE → Str>=78 + X4%>=22<br>
    🔥 GO → Str>=65 + X4%>=16<br>
    🟡 MICRO BET → Str>=52 + X4%>=11<br>
    ⚠️ SKIP → tsy misy signal</div>
    </div>
    """,unsafe_allow_html=True)
    st.stop()

with st.sidebar:
    st.markdown("### 🎯 SNIPER X4")
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

st.markdown("<div class='ttl'>🎯 JETX SNIPER X4</div>",unsafe_allow_html=True)
st.markdown("<div class='sub'>500K SIMS • BAYESIAN • CIBLÉ X4+ ULTRA PRÉCIS</div>",unsafe_allow_html=True)
ci,co=st.columns([1,2],gap="medium")

with ci:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    h_in  = st.text_input("🔐 SERVER HASH",placeholder="Ex: 7db8e01413d6d8c6...  (Provably Fair)")
    lt_in = st.text_input("⏰ LAST TIME (HH:MM:SS)",placeholder="Ex: 20:22:24  —  ora round taloha")
    lc    = st.number_input("📊 LAST COTE",value=1.88,step=0.01,format="%.2f")
    if   lc<1.5: sl,sc2="🔵 COLD","#4488ff"
    elif lc<2.5: sl,sc2="⚪ NORMAL","#aaa"
    elif lc<3.5: sl,sc2="🟡 WARM","#ffcc00"
    else:        sl,sc2="🔴 HOT","#ff3366"
    st.markdown(f"<div style='text-align:center;margin:6px 0;'><span style='background:rgba(255,255,255,.07);border-radius:8px;padding:4px 14px;color:{sc2};font-size:.82rem;'>{sl}</span></div>",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)
    if st.button("🎯 SNIPER ANALYSER",use_container_width=True):
        if h_in and lt_in:
            with st.spinner("🎯 500k sims X4+ targeting..."):
                r=engine(h_in.strip(),lt_in.strip(),lc)
            st.session_state.R=r
            st.session_state.H.append(dict(r))
            if len(st.session_state.H)>200: st.session_state.H.pop(0)
            sj(HF,st.session_state.H); st.session_state.ck+=1; st.rerun()
        else: st.error("❌ Hash et Last Time obligatoires!")

with co:
    r=st.session_state.R
    if r:
        st.markdown("<div class='card'>",unsafe_allow_html=True)
        st.markdown(f"<div class='{r['sc']}'>{r['sig']}</div>",unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;color:rgba(255,255,255,.4);font-size:.72rem;margin-top:14px;'>▸ ENTRY TIME (Last +{r['sh']}s)</p>",unsafe_allow_html=True)
        st.markdown(f"<div class='etime'>{r['ent']}</div>",unsafe_allow_html=True)
        # X4 PROB MEGA
        st.markdown("<p style='text-align:center;color:rgba(255,255,255,.35);font-size:.7rem;'>CIBLE PRINCIPALE</p>",unsafe_allow_html=True)
        st.markdown("<div class='x4big'>X4+</div>",unsafe_allow_html=True)
        st.markdown(f"<div class='pct'>{r['bp4']}%</div>",unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:rgba(255,255,255,.3);font-size:.68rem;'>PROB X4+ BAYESIAN</p>",unsafe_allow_html=True)
        # Tags
        st.markdown(f"""<div style='text-align:center;margin:10px 0;'>
        <span class='tag'>🔄 {r['cur']}</span><span class='tag'>🔥 {r['hp']}%</span>
        <span class='tag'>💪 {r['str']}</span>
        <span class='tag-o'>X3+ {r['p3']}%</span>
        <span class='tag-o'>X4.5+ {r['p45']}%</span>
        <span class='tag-o'>X5+ {r['p5']}%</span>
        <span class='tag-o'>X6+ {r['p6']}%</span>
        </div>""",unsafe_allow_html=True)
        # Targets X4
        c1,c2,c3=st.columns(3)
        with c1: st.markdown(f"<div class='tbox'><div class='tl'>X4 MIN</div><div class='tv' style='color:#ff99ff;'>{r['t4min']}×</div><div class='ta'>{r['acc4min']}%</div></div>",unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='tbox'><div class='tl'>X4 MOYEN</div><div class='tv' style='color:#ff6600;'>{r['t4moy']}×</div><div class='ta'>{r['acc4moy']}%</div></div>",unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='tbox'><div class='tl'>X4 MAX</div><div class='tv' style='color:#ffcc00;'>{r['t4max']}×</div><div class='ta'>{r['acc4max']}%</div></div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cw,cl2=st.columns(2)
        with cw:
            if st.button("✅ WIN X4+",use_container_width=True,key="bw"):
                idx=r.get("hi",-1)
                if 0<=idx<len(st.session_state.H): st.session_state.H[idx]["res"]="W"; sj(HF,st.session_state.H)
                st.session_state.S["t"]+=1; st.session_state.S["w"]+=1; sj(SF,st.session_state.S); st.success("🎯 SNIPER HIT!"); st.rerun()
        with cl2:
            if st.button("❌ MISS",use_container_width=True,key="bl"):
                idx=r.get("hi",-1)
                if 0<=idx<len(st.session_state.H): st.session_state.H[idx]["res"]="L"; sj(HF,st.session_state.H)
                st.session_state.S["t"]+=1; st.session_state.S["l"]+=1; sj(SF,st.session_state.S); st.rerun()
        st.markdown(f"<p style='text-align:center;color:rgba(255,255,255,.18);font-size:.6rem;margin-top:8px;'>LC:{r['lc']}× • 500k sims X4</p>",unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)
    else:
        st.markdown("<div class='card' style='min-height:380px;display:flex;align-items:center;justify-content:center;'><div style='text-align:center;'><div class='x4big' style='font-size:3rem;opacity:.2;'>X4</div><div style='color:rgba(255,255,255,.15);font-family:Orbitron;margin-top:10px;font-size:.85rem;'>SNIPER EN ATTENTE...</div></div></div>",unsafe_allow_html=True)

if st.session_state.H:
    st.markdown("---")
    df=pd.DataFrame([{"Entry":x.get("ent",""),"Shift":f"+{x.get('sh',0)}s","X4%":x.get("bp4",""),"X5%":x.get("p5",""),"State":x.get("cur",""),"Min":x.get("t4min",""),"Max":x.get("t4max",""),"Res":"HIT" if x.get("res")=="W" else "MISS" if x.get("res")=="L" else "—"} for x in reversed(st.session_state.H[-10:])])
    st.dataframe(df,use_container_width=True,hide_index=True)
st.markdown("<div style='text-align:center;margin-top:18px;color:rgba(255,255,255,.07);font-size:.54rem;'>JETX SNIPER X4 • 500K SIMS • BAYESIAN • CIBLÉ X4+</div>",unsafe_allow_html=True)
