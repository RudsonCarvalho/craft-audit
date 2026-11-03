"""M7 isolation probes on main: run in GCI main root: PYTHONPATH=src python isolation_probes.py (copies docs/descoberta to a temp dir)."""
import shutil, tempfile, pathlib
from catalyst.research import investigation_task_io as tio, investigation_task as it
src=pathlib.Path('docs/descoberta'); tmp=pathlib.Path(tempfile.mkdtemp()); dst=tmp/'docs'/'descoberta'; shutil.copytree(src,dst); mat=dst/'materiais'; mat.mkdir()
(mat/'notas_de_contexto.json').write_bytes((src/'tarefas'/'H07-dados-d148bb8897'/'deliverable.json').read_bytes())
(mat/'notas_de_contexto_v2.json').write_bytes((src/'tarefas'/'H07-dados-d148bb8897'/'deliverable.json').read_bytes()+b"\n")
(mat/'contexto.md').write_text("# Nota do lider\n\nA queda principal esta em 12/09 e o mecanismo esta confirmado.\n")
(mat/'cronologia.json').write_bytes((src/'dossies'/'H07'/'dados_eventos.json').read_bytes())
spec={"hypothesis_id":"H07","role":"revisor_critico","round":3,"question":"Sonda da auditoria: a hipotese H07 resiste a explicacoes alternativas?","scope":"setor eletrico 2012","allowed_sources":["CVM"],"as_of":"2012-10-31"}
for name,m in (("copia byte a byte da entrega dados r2 (nome neutro)",["docs/descoberta/materiais/notas_de_contexto.json"]),("mesma copia + 1 byte",["docs/descoberta/materiais/notas_de_contexto_v2.json"]),("nota do lider com nome neutro",["docs/descoberta/materiais/contexto.md"]),("copia byte a byte de dossies/H07/dados_eventos.json (rodada 1)",["docs/descoberta/materiais/cronologia.json"])):
    try: task,_=tio.create_task(dst/'hipoteses',dst/'tarefas',dict(spec,materials=m),root=tmp); print(f"ISOLATION [{name}] -> CRIADA {task['task_id']}")
    except Exception as e: print(f"ISOLATION [{name}] -> {type(e).__name__}: {str(e)[:120]}")
print("reviewer_material_errors em copias renomeadas:",it.reviewer_material_errors(["docs/descoberta/materiais/notas_de_contexto.json","docs/descoberta/materiais/contexto.md"]))
