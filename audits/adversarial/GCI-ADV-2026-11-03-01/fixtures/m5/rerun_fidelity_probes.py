"""Re-run the 13 adversarial cases of fidelity_211_probes.json. Run in gci-pr-208: PYTHONPATH=src:tests python rerun_fidelity_probes.py <path to fidelity_211_probes.json>"""
import sys, json, tempfile, pathlib
sys.path.insert(0,'tests')
import test_fidelidade_211 as T
cf=T.cf
fx=json.load(open(sys.argv[1]))["fixture"]
for c in fx["cases"]:
    with tempfile.TemporaryDirectory() as tmp:
        w=T.World(pathlib.Path(tmp),fx); mission,bundle=w.case(c)
        det=cf.run_deterministic(w.board,mission,bundle); rep=cf.audit_compression(w.board,mission,bundle,T.FakeModel(w,c.get("auditor"))); gate=T.gate_of(w,mission,bundle,rep)
        print(f"{c['nome']:52} decision={rep['audit_decision']:20} gate={gate.allowed} det={sorted({f.code for f in det.findings})} suspeitas={sorted({s['codigo'] for s in rep.get('suspeitas',[])})}")
