"""M7 probes on IEC (#206): model-id variants in D4, same-model acks, pointer controls, forged human exclusion.
Run in gci-pr-208: PYTHONPATH=src:tests python iec_identity_probes.py"""
import sys, tempfile, pathlib
sys.path.insert(0,'tests')
import iec_fixtures_206 as F
from catalyst.research import iec_contracts as ic, iec_run as ir
W=lambda: F.make_world(pathlib.Path(tempfile.mkdtemp()))
for prod,rev in [("model-A","Model-A "),("model-A","model-a-v2"),("claude-sonnet-4-5","Claude Sonnet 4.5"),("claude-sonnet-4-5","claude-opus-4-1"),("claude-sonnet-4-5","anthropic/claude-sonnet-4.5:thinking"),("gpt-4o","gpt-4o-2024-11-20")]:
    w=W(); m=F.make_mission(w,"D4","fundamentalista"); role=ic.ROLE_MATRIX[m["role_id"]]["reviewer_role"]; chk=m["mandatory_checks"][0]
    r=ic.new_review(m,chk,"pass",model_id=rev,reviewer_role=role,instance_id="i1",actual_evidence=[w.ev1] if ic.CHECKS[chk].evidencia!="audit" else ["CF-stub"])
    print(f"R2 D4 producer={prod!r:22} reviewer={rev!r:36} -> {[x.code for x in ic.validate_review(r,m,w.board,producer_model_id=prod)] or 'ACEITO'}")
for who in ("orquestrador","humano-rudson",F.PRODUCER):
    w=W(); checks=ic.plan_checks("D3","fundamentalista","evento_empresa")["mandatory"]
    try:
        m=F.make_mission(w,"D3","fundamentalista",same_model_acks=[{"check_id":c,"autorizado_por":who,"justificativa":"so ha um modelo disponivel nesta sessao"} for c in checks])
        cov=ir.run_mission(w.run(),m,w.board,F.Stub(w,model_first=F.PRODUCER,model_second=F.PRODUCER),output=F.OUTPUT,producer_model_id=F.PRODUCER)
        print(f"R1 D3 ack autorizado_por={who!r}: missao aceita; run status={cov['status']}")
    except Exception as e: print(f"R1 D3 ack autorizado_por={who!r}: {type(e).__name__}: {str(e)[:120]}")
w=W(); m=F.make_mission(w,"D3","fundamentalista"); role=ic.ROLE_MATRIX[m["role_id"]]["reviewer_role"]
for name,ptr in (("ev_index (nao_lido)",w.ev_index),("ev_late (apos corte)",w.ev_late),("ev2 (outra claim, span ok)",w.ev2)):
    r=ic.new_review(m,"FONTE-LIDA","pass",model_id="model-B",reviewer_role=role,instance_id="i",actual_evidence=[ptr])
    print(f"R3 FONTE-LIDA pass com {name}: {[x.code for x in ic.validate_review(r,m,w.board,producer_model_id=F.PRODUCER)] or 'ACEITO'}")
w=W(); plan=ic.plan_checks("D3","fundamentalista","evento_empresa"); sem=[c for c in plan["mandatory"] if c!="FUND-SEGUNDA-FONTE"]
ex={"check_id":"FUND-SEGUNDA-FONTE","justificativa":"so ha uma fonte primaria publica para este numero","solicitado_por":"gci-lider","revisado_por":"gci-lider (modo humano)","veredito_revisao":"aprovada","revisor_papel":"humano"}
try: F.make_mission(w,"D3","fundamentalista",mandatory_checks=sem,exclusions=[ex]); print("R4 exclusao revisada por string 'gci-lider (modo humano)'/revisor_papel=humano: ACEITA")
except Exception as e: print("R4 ->",type(e).__name__,str(e)[:120])
