"""M5 trace: H07 round-2 deliverables -> dossier log -> card projection -> Radar API.
Read-only. Run from the GCI repo root with PYTHONPATH=src. Writes a JSON report to the path in argv[1]."""
import json, sys, re
import yaml
from catalyst.radar import queries as qm
root='docs/descoberta'
tasks={"fund":"H07-fund-d6b93550e0","dados":"H07-dados-d148bb8897","rev":"H07-rev-7acb9d7691"}
deliv={k:json.load(open(f'{root}/tarefas/{v}/deliverable.json')) for k,v in tasks.items()}
entries=[json.loads(l) for l in open(f'{root}/hipoteses/log/H07.jsonl')]
note=entries[-1]['payload']; assert note.get('note_kind')=='investigation_round'
card=yaml.safe_load(open(f'{root}/hipoteses/H07.md').read().split('---')[1])
cls=[getattr(qm,n) for n in dir(qm) if hasattr(getattr(qm,n),'dossier') and isinstance(getattr(qm,n),type)][0]
q=cls(qm.RadarPaths.from_hypotheses_dir(f'{root}/hipoteses'))
dossier=q.dossier('H07'); changes=q.changes('H07','2026-10-31T14:00:00')
log_ev=[e for e in entries if e['kind']=='evidence_added' and e['payload']['evidence_id'].startswith('H07-')]
rep={"claims_delivered":{},"claims_in_log":len([e for e in log_ev if any(e['payload']['evidence_id'].startswith(t) for t in tasks.values())]),
     "stance_in_log":{}, "card":{}, "radar_dossier":{}, "radar_changes":{}, "note":{}, "field_loss":{}}
for k,d in deliv.items():
    rep["claims_delivered"][k]=len(d['claims'])
from collections import Counter
r2=[e for e in log_ev if any(e['payload']['evidence_id'].startswith(t) for t in tasks.values())]
rep["stance_in_log"]=dict(Counter(e['payload']['stance'] for e in r2))
rep["card"]={"evidence_for":len(card['evidence_for']),"evidence_against":len(card['evidence_against']),"neutral":0,
             "has_open_questions_field":'open_questions' in card, "dossier_block_refutation_tests":card.get('dossier',{}).get('refutation_tests'),
             "dossier_block_mentions_round2": 'Rodada 2' in json.dumps(card.get('dossier',{}),ensure_ascii=False)}
ds=json.dumps(dossier,ensure_ascii=False); cs=json.dumps(changes,ensure_ascii=False)
probe_terms=["TBLE3","Tractebel","Rede Energia","exposure_share","exposure_basis","refutation","alternative_explanations","human_review_reasons","recommended_state","needs_human_review","conflicts","Rodada 2"]
rep["radar_dossier"]={t:(t in ds) for t in probe_terms}; rep["radar_dossier"]["notes_last"]=dossier['notes'][-1]
rep["radar_changes"]={t:(t in cs) for t in probe_terms}
comp=note.get('companies',[])
rep["note"]={"companies_count":len(comp),"companies_fields_kept":sorted(comp[0].keys()) if comp else [],
    "companies_fields_in_deliverable":sorted(deliv['fund']['companies'][0].keys()),
    "alt_expl":len(note.get('alternative_explanations',[])),"ref_tests":len(note.get('refutation_tests',[])),"next_questions":len(note.get('next_questions',[])),
    "summary":note['summary']}
# counterexample check: does the lead summary mention TBLE3 (generator w/o expiring concessions, -12%)?
rep["summary_mentions"]={t:(t in note['summary']) for t in ["TBLE3","Tractebel","Taesa","CPFL","LIGT3","Light"]}
rev_claims=[c['statement'] for c in deliv['rev']['claims']]
rep["reviewer_mentions_TBLE3"]=any('TBLE3' in s for s in rev_claims)
rep["field_loss"]={"neutral_claims_dropped_from_card":rep["stance_in_log"].get('neutral',0),
    "companies_fields_dropped_in_note":sorted(set(rep["note"]["companies_fields_in_deliverable"])-set(rep["note"]["companies_fields_kept"])),
    "radar_note_body_null": dossier['notes'][-1].get('note') is None}
json.dump(rep,open(sys.argv[1],'w'),ensure_ascii=False,indent=1); print(json.dumps(rep,ensure_ascii=False,indent=1)[:3500])
