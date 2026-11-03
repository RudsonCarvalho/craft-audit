"""M6 probes on sectioned_doc (#212). Run in gci-pr-208: PYTHONPATH=src:tests python sectioned_doc_probes.py"""
import sys, copy
sys.path.insert(0,'tests')
import test_sectioned_doc_212 as t
sd=t.sd; sy=t.sy
def mk():
    d=t.Doc(); d.do("ana",[{"op":"add_section","section_id":"SA","title":"A"}]); d.do("beto",[{"op":"add_section","section_id":"SB","title":"B"}])
    d.do("ana",[d.fato("CA1","SA","Receita ficticia 100.")]); d.do("beto",[d.fato("CB1","SB","Custo ficticio 40.")]); return d
def st(d,cid):
    s=d.state; c=s['claims'].get(cid); return None if c is None else (c.get('status'), sd.effective_approval(s,c,d.board))
def hashes(d): return {s: sd.section_hash(d.state,s) for s in d.state['section_order']}
def run(label,fn):
    try: print(label, fn())
    except Exception as e: print(label, f"{type(e).__name__}: {str(e)[:140]}")
d=mk(); d.board.add("EV-CA1-C","BC-CA1","contraria"); d.do("rev",[{"op":"add_counterevidence","claim_id":"CA1","evidence":["EV-CA1-C"]}]); print("Q1 CA1 contestada:",st(d,"CA1"))
run("Q1 replace mesmo board_claim_id ->",lambda:(d.do("ana",[{"op":"replace_claim","claim_id":"CA1","new_claim_id":"CA1b","text":"Receita ficticia 100.","board_claim_id":"BC-CA1","evidence":["EV-CA1"]}]),st(d,"CA1b"))[1])
d=mk(); d.board.add("EV-CA1-C","BC-CA1","contraria"); d.do("rev",[{"op":"add_counterevidence","claim_id":"CA1","evidence":["EV-CA1-C"]}]); d.board.add("EV-X","BC-X")
run("Q1c retract (pelo autor) + append mesmo texto, novo board_claim_id ->",lambda:(d.do("ana",[{"op":"retract_claim","claim_id":"CA1","motivo":"reescrita"}]),d.do("ana",[{"op":"append_claim","section_id":"SA","claim_id":"CA1d","kind":"fato_primario","text":"Receita ficticia 100.","board_claim_id":"BC-X","evidence":["EV-X"]}]),st(d,"CA1d"),[l for l in sd.render_index(d.state,d.board).splitlines() if l.startswith('| SA')])[2:])
d=mk(); d.do("ana",[{"op":"add_section","section_id":"SC","title":"C"}]); d.do("ana",[{"op":"append_claim","section_id":"SC","claim_id":"CC1","kind":"conclusao","text":"Receita sustenta tese.","depends_on":["CA1"]}])
h0=hashes(d); d.do("ana",[{"op":"retract_claim","claim_id":"CA1","motivo":"fonte revisada"}]); h1=hashes(d)
print("Q2 apos retract CA1: conclusions=",{k:v.get('status') for k,v in d.state['conclusions'].items()},"hashes changed=",{k:(h0[k]!=h1[k]) for k in h0})
d=mk(); p1=d.patch("ana",[d.fato("CA2","SA","Fato 1.")],key="k-same"); d.apply(p1); p2=d.patch("ana",[d.fato("CA3","SA","Fato 2 diferente.")],key="k-same")
run("Q3 idempotency_key reutilizada com conteudo diferente ->",lambda:("APLICADO",d.apply(p2).document_version))
d=mk(); d.do("ana",[{"op":"add_section","section_id":"SC","title":"C"}]); d.do("ana",[{"op":"append_claim","section_id":"SC","claim_id":"CC1","kind":"conclusao","text":"Receita sustenta tese.","depends_on":["CA1"]}]); base=copy.deepcopy(d.state)
pB=sy.prepare_patch(base,author="ana",key="k-B2",task="T1",reason="reafirma",ops=[{"op":"replace_claim","claim_id":"CC1","new_claim_id":"CC1b","text":"Receita sustenta tese (reafirmada).","kind":"conclusao","depends_on":["CA1"]}],rebase="if_disjoint")
d.do("ana",[{"op":"retract_claim","claim_id":"CA1","motivo":"fonte revisada"}]); run("Q4b patch obsoleto reafirmando conclusao dependente de claim retratada ->",lambda:("APLICADO",d.apply(pB).document_version))
d=mk(); print("Q6 default doc fidelity_gate por patch:",[e['payload'].get('fidelity_gate') for e in d.entries if e['kind']=='patch'],"| CA1:",st(d,"CA1"))
dg=t.Doc(gate_required=True); run("Q6 gate_required: add_section sem gate ->",lambda:(dg.do("ana",[{"op":"add_section","section_id":"SA","title":"A"}]),"APLICADO")[1])
d=mk(); run("Q7 view: linhas com 'gate' ->",lambda:[l for l in sd.render_markdown(d.state,board=d.board).splitlines() if 'gate' in l.lower()][:3])
