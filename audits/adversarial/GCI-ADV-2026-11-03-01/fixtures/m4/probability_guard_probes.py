"""M4 probes P-A..P-H. Run in GCI main: PYTHONPATH=src python probability_guard_probes.py  (P-G/P-H need gci-pr-203 on PYTHONPATH)."""
import sys, json
from catalyst.research.decision_gate import validate_decision_record
from catalyst.research.trigger_ontology import validate_trigger
base={"hypothesis_id":"H07","event":"decision","decision":"solicitar_estudo","actor":"gci-lider","reason":"sonda adversarial","date":"2026-11-03","alternatives_discussed":["monitorar"],
 "fundamental_exposure_evidence":{"value":None,"method":"nao medido","sources":[],"status":"unknown"},
 "conditional_economic_impact":{"value":None,"method":"nao medido","sources":[],"status":"unknown","note":"a discutir"},
 "pricing_costs_risk":{"value":None,"method":"nao medido","sources":[],"status":"unknown","note":"a discutir"}}
cases={"P-A llm score + calibration_ref textual":{"value":0.62,"method":"pontuacao do agente Sonnet (escala 0-1) convertida em probabilidade","sources":["sessao do agente 2026-11-03"],"status":"known","calibration_ref":"calibracao_v0"},
 "P-B palavra LLM":{"value":0.62,"method":"LLM score","sources":["x"],"status":"known","calibration_ref":"calibracao_v0"},
 "P-C calibration_ref inexistente":{"value":0.62,"method":"modelo logit","sources":["docs/inexistente.md"],"status":"known","calibration_ref":"docs/calibracao/nao_existe.json"},
 "P-D percentual subjetivo em note":{"value":None,"method":"estimativa subjetiva","sources":[],"status":"not_estimable","note":"o agente estima 60% de chance de corte de 50pb"}}
for k,dim in cases.items():
    errs=validate_decision_record({**base,"scenario_probability":dim}); print(f"{k}: {'ACEITO' if not errs else 'RECUSADO '+str(errs)}")
t={"id":"T1","kind":"policy_act","jurisdiction":"BR","policy_dimension":"x","stance":"unknown","actor_role":"unknown","expected_effect":"unknown","source_refs":[],"confidence":"unknown"}
print("P-F trigger scenario_probability=0.6 source='estimativa do agente Sonnet':",validate_trigger({**t,"scenario_probability":0.6,"scenario_probability_source":"estimativa do agente Sonnet"},"t") or "ACEITO")
try:
    from catalyst.research import roles
    for k,txt in {"P-G pct":"probabilidade de 60% de corte","P-H decimal":"probabilidade de 0,6 de corte","P-H 6em10":"ha 6 chances em 10 de corte","P-H odds":"odds de 3 para 2 a favor do corte","P-H p=":"corte e provavel (p=0,6)","P-H pct sem palavra":"60% dos cenarios apontam corte","P-H por cento":"cenario base com 60 por cento"}.items():
        v=roles.scan_forbidden({"claims":[{"texto":txt}]}); print(f"{k}: {txt!r} -> {[x.code for x in v] or 'PASSA'}")
except ImportError: print("P-G/P-H: roles.py indisponivel neste PYTHONPATH (usar gci-pr-203)")
