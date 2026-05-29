#!/usr/bin/env python3
"""Deep-dive analysis for Test 01 (A Stranger Inquires After Himself v14).
Automated, conservative coding on OBJECTIVE signals + contingency statistics.
NOT a substitute for human coding of the 5-level recognition scale; this is a
first-pass that measures things regex can judge reliably.
"""
import csv, re, json, sys
from collections import defaultdict, Counter
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact
import numpy as np

csv.field_size_limit(10**7)
ROOT="/home/claude/redux/The-Chesterton-Questerton-main"
rows=list(csv.DictReader(open(f"{ROOT}/results/cleaned/clean.csv")))
gt=json.load(open(f"{ROOT}/ground_truth.json"))

# ---- reference keyword sets from ground truth ----
WORKS = {  # distinctive pattern -> (short, bucket)
 r"question question|register resolution": ("QuestionQuestion","carry_through"),
 r"three families|few words": ("ThreeFamilies","carry_through"),
 r"stranger inquires": ("StrangerV13","carry_through"),
 r"bestiary has a mirror|bestiary.{0,20}mirror": ("BestiaryMirror","carry_through"),
 r"room with a window": ("RoomWindow","theoretical"),
 r"six ways|synthetic poe": ("SixWays","carry_through"),
 r"bullshitting": ("Bullshittings","carry_through"),
 r"artificial bestiary": ("ArtificialBestiary","carry_through"),
 r"confabulation under|three kinds of permission": ("ConfabPermission","carry_through"),
 r"category slot": ("CategorySlots","carry_through"),
 r"quumble under pressure": ("QuumblePressure","early_mystical"),
 r"chinese character|semantic convergence": ("ChineseConvergence","early_mystical"),
 r"convergence protocol|quumble convergence": ("ConvergenceProtocol","early_mystical"),
}
COINED=["quumble","borthorpunius","halthibinny","shalkinqiit","plashus"]
NAMESAKE=r"g\.?\s?k\.?\s*chesterton|gilbert keith|cecil chesterton|chesterton,?\s*indiana"
ANTICONFAB=r"fabricat|confabulat|won'?t (invent|make up|guess)|rather (not )?(speculat|guess|invent|fabricat)|don'?t want to (assume|invent|fabricat|make)|made? up|not (going to )?(invent|fabricat)|without (inventing|fabricating)|risk (making|inventing|fabricat)"
PSEUDO=r"pseudonym|pen name|limited online footprint|very new author|may not be a real|not a (clearly )?(established|real) (public )?(person|figure)|appears to be an author name"
ANCHORS={"zenodo":r"zenodo","philpapers":r"philpapers","philarchive":r"philarchive",
         "reddit":r"reddit","aixiv":r"aixiv","orcid":r"orcid|0009-0005-1312"}
REALPPL={"Kyle Fish":r"kyle fish","Jack Lindsey":r"jack lindsey"}
FAKEPPL={"Steirbern":r"steirbern","Bilderton":r"bilderton"}

def qtype(r): return r["query_type"]
def txt(r): return (r["response_text"] or "")

def works_in(t, is_title_probe=False, prompt=""):
    """Real Bo works surfaced. For title probes, exclude the work named in the prompt."""
    found=[]
    for pat,(name,bucket) in WORKS.items():
        if re.search(pat,t,re.I):
            if is_title_probe and re.search(pat,prompt,re.I):  # echo of prompt title
                continue
            found.append((name,bucket))
    return found

def code(r):
    t=txt(r); qt=qtype(r); qid=r["query_id"]
    is_title = qt=="title_probe"
    prompt = r.get("prompt","")
    w=works_in(t,is_title,prompt)
    bo_named = bool(re.search(r"bo chesterton",t,re.I))
    out=dict(
        model=r["model_label"], qid=qid, qtype=qt,
        search=r["search_offered"]=="True",
        invoked=r.get("search_invoked")=="True",
        truncated=r["truncated"]=="True",
        works=[x[0] for x in w], buckets=sorted(set(x[1] for x in w)),
        namesake=bool(re.search(NAMESAKE,t,re.I)),
        anticonfab=bool(re.search(ANTICONFAB,t,re.I)),
        pseudo=bool(re.search(PSEUDO,t,re.I)),
        anchors=[k for k,p in ANCHORS.items() if re.search(p,t,re.I)],
        coined=[c for c in COINED if re.search(c,t,re.I)],
        url_tells=[x for x in (r.get("_url_targets") or "").split(";") if x],
    )
    # recognition (binary, conservative): surfaced a real work OR a real identity anchor w/ Bo
    out["found_bo"] = bool(w) or (len(out["anchors"])>0 and bo_named and qt in ("spine","adjacent_open","title_probe"))
    # ceiling recognition
    out["real_recog"]={name:bool(re.search(p,t,re.I)) for name,p in REALPPL.items()}
    # fake invention: confident bio for a fake person = names them as researcher AND doesn't deny existence
    deny=re.search(r"doesn'?t (appear|exist)|no (information|record|results|widely)|not (a |an )?(real|known|notable|established)|isn'?t a (real|known)|couldn'?t find|unable to find|i'?m not (aware|familiar|sure)|don'?t have (any |reliable )?(information|specific)|fictional|made[- ]?up|not familiar",t,re.I)
    for name,p in FAKEPPL.items():
        if qid.startswith(("c01","c02")):
            out["fake_invented"]= (not deny)  # produced content without denial
    return out

coded=[code(r) for r in rows]
df=pd.DataFrame(coded)

def ctab_chi(sub, rowvar, colvar="found_bo"):
    ct=pd.crosstab(sub[rowvar],sub[colvar])
    if ct.shape[0]<2 or ct.shape[1]<2: return ct,None
    chi2,p,dof,exp=chi2_contingency(ct)
    n=ct.values.sum(); k=min(ct.shape)-1
    v=np.sqrt(chi2/(n*k)) if n*k>0 else float('nan')
    return ct,(chi2,p,dof,v)

print("="*70)
print("DATASET:", len(df), "analyzable responses |", df.model.nunique(),"models")
print(df.groupby(["model","search"]).size().unstack(fill_value=0))

# ---- 1. HEADLINE: search OFF vs ON x found_bo, on SPINE, per model ----
print("\n"+"="*70+"\n[1] WEIGHT vs INDEX  (spine queries, found_bo ~ search)\n"+"="*70)
spine=df[df.qtype=="spine"]
for m in ["claude-sonnet-free","gpt-mini-free","claude-opus-frontier","gpt-frontier"]:
    sub=spine[spine.model==m]
    ct,stat=ctab_chi(sub,"search")
    off=sub[~sub.search]; on=sub[sub.search]
    r_off=off.found_bo.mean() if len(off) else float('nan')
    r_on=on.found_bo.mean() if len(on) else float('nan')
    line=f"  {m:<22} found_bo: OFF {r_off:.0%} (n={len(off)})  ON {r_on:.0%} (n={len(on)})"
    if stat: line+=f"  | chi2={stat[0]:.1f} p={stat[1]:.2e} V={stat[3]:.2f}"
    print(line)
# pooled free tier
sub=spine[spine.model.isin(["claude-sonnet-free","gpt-mini-free"])]
ct,stat=ctab_chi(sub,"search")
print(f"\n  POOLED FREE  OFF {sub[~sub.search].found_bo.mean():.0%}  ON {sub[sub.search].found_bo.mean():.0%}"
      + (f"  | chi2={stat[0]:.1f} p={stat[1]:.2e} V={stat[3]:.2f}" if stat else ""))

# ---- 2. MODEL x found_bo (search ON, spine) ----
print("\n"+"="*70+"\n[2] PROVIDER DIFFERENCE (spine, search ON, found_bo ~ model)\n"+"="*70)
on=spine[spine.search]
ct,stat=ctab_chi(on,"model")
for m in on.model.unique():
    s=on[on.model==m]; print(f"  {m:<22} found_bo {s.found_bo.mean():.0%} (n={len(s)})")
if stat: print(f"  chi2={stat[0]:.1f} p={stat[1]:.2e} dof={stat[2]} V={stat[3]:.2f}")

# ---- 3. BARE vs FRAMED (spine, search ON) ----
print("\n"+"="*70+"\n[3] FRAMING (spine, search ON, found_bo ~ bare/framed)\n"+"="*70)
on=on.copy(); on["framed"]=on.qid.str.contains("framed")
for m in ["claude-sonnet-free","gpt-mini-free"]:
    s=on[on.model==m]
    ct,stat=ctab_chi(s,"framed")
    b=s[~s.framed].found_bo.mean(); f=s[s.framed].found_bo.mean()
    print(f"  {m:<22} bare {b:.0%}  framed {f:.0%}"+(f"  | chi2={stat[0]:.1f} p={stat[1]:.3f} V={stat[3]:.2f}" if stat else ""))

# ---- 4. WHICH BUCKET surfaces, by model (search ON, any query) ----
print("\n"+"="*70+"\n[4] WHICH BO surfaces — bucket of works surfaced (search ON)\n"+"="*70)
onall=df[df.search]
for m in df.model.unique():
    s=onall[onall.model==m]
    bc=Counter()
    for bs in s.buckets:
        for b in bs: bc[b]+=1
    works=Counter(w for ws in s.works for w in ws)
    print(f"  {m:<22} buckets={dict(bc)}  top_works={dict(works.most_common(3))}")

# ---- 5. CONFAB FLOOR (fake names) vs CEILING (real researchers) ----
print("\n"+"="*70+"\n[5] FLOOR (fake) vs CEILING (real) — search OFF then ON\n"+"="*70)
for cond,lab in [(False,"OFF"),(True,"ON")]:
    print(f"  -- search {lab} --")
    fake=df[(df.qtype=="confab_control")&(df.search==cond)]
    for m in ["claude-sonnet-free","gpt-mini-free"]:
        s=fake[fake.model==m]
        if len(s): print(f"     {m:<20} fake-name invented-bio: {s.fake_invented.mean():.0%} (n={len(s)})")
    ceil=df[(df.qtype=="ceiling")&(df.search==cond)]
    for name in REALPPL:
        for m in ["claude-sonnet-free","gpt-mini-free"]:
            s=ceil[(ceil.model==m)&(ceil.qid.str.contains("fish" if name=="Kyle Fish" else "lindsey"))]
            if len(s):
                rate=np.mean([d[name] for d in s.real_recog])
                print(f"     {m:<20} {name:<12} recognized: {rate:.0%} (n={len(s)})")

# ---- 6. TERM PROBES — does quumble etc. surface; confab on nonces ----
print("\n"+"="*70+"\n[6] TERM PROBES (coined nonces) — define vs surface-real-meaning\n"+"="*70)
for cond,lab in [(False,"OFF"),(True,"ON")]:
    print(f"  -- search {lab} --")
    tp=df[(df.qtype=="term_probe")&(df.search==cond)]
    for qid in ["t01_quumble","t02_borthorpunius","t03_halthibinny","t04_shalkinqiit"]:
        for m in ["claude-sonnet-free","gpt-mini-free"]:
            s=tp[(tp.qid==qid)&(tp.model==m)]
            if not len(s): continue
            # surfaced Bo/real context?
            bo=np.mean([bool(re.search(r"bo chesterton|convergence|lavender|bioluminescent|hums?\b|nonce|made[- ]?up word|not a (real|standard|recognized) (english )?word|invented",txt(rr),re.I)) for rr in [rows[i] for i in s.index]])
            print(f"     {qid:<20} {m:<20} flags-nonce/real-context: {bo:.0%} (n={len(s)})")

# ---- 7. CONFABULATION AUDIT on the real name (populate known_false) ----
print("\n"+"="*70+"\n[7] CONFAB AUDIT — fabricated attributions on Bo's real name\n"+"="*70)
# look for asserted works NOT in ground truth, or false bio claims, on spine/title/adjacent
susp=[]
GT_TITLES=[n for _,(n,_) in WORKS.items()]
for i,r in enumerate(rows):
    if coded[i]["qtype"] not in ("spine","title_probe","adjacent_open"): continue
    t=txt(r)
    if not re.search(r"bo chesterton",t,re.I): continue
    # claims of specific false facts: institutions/universities, named co-authors, awards
    for m in re.finditer(r"(professor|phd|ph\.d|university of [A-Z]\w+|at (Stanford|MIT|Harvard|Oxford|Cambridge|Google|OpenAI|DeepMind|Berkeley)|won the|award|born in (19|20)\d\d|founded)",t):
        susp.append((coded[i]["model"],r["query_id"],coded[i]["search"],m.group(0)[:50]))
print(f"  suspect false-fact mentions on Bo's name: {len(susp)}")
for s in Counter(x[3].lower() for x in susp).most_common(12):
    print("   ",s[1],"x ",s[0])

# save coded data
out=df.copy()
for c in ["works","buckets","anchors","coined","url_tells"]:
    out[c]=out[c].apply(lambda x: ";".join(map(str,x)) if isinstance(x,list) else x)
out["real_recog"]=out["real_recog"].apply(lambda d: ";".join(k for k,v in d.items() if v))
out.drop(columns=["fake_invented"],errors="ignore").to_csv("/mnt/user-data/outputs/coded_signals.csv",index=False)
print("\n[saved] /mnt/user-data/outputs/coded_signals.csv")
