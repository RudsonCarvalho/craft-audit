"""M2 probe: homonym PMI series under one caller-chosen series_id. Run in gci-pr-208 (or gci-pr-167):
PYTHONPATH=src python store_homonym_probe.py. Read-only; uses temp dirs."""
import tempfile
from datetime import datetime, UTC
from catalyst.sources.series_store import SeriesStore, SeriesCapture, SeriesRow
from catalyst.sources.series_consensus import ConsensusSnapshot, surprise
st=SeriesStore(tempfile.mkdtemp())
c1=SeriesCapture(series_id="china_pmi_manufacturing",unit="indice",definition="PMI manufatura China",dataset_id="stats.gov.cn",source_url="https://www.stats.gov.cn/zwfwck/sjfb/202605/t20260531_1963824.html",document_sha256="a"*64,captured_at=datetime(2026,5,31,2,0,tzinfo=UTC),published_at=datetime(2026,5,31,1,30,tzinfo=UTC),published_precision="exact")
print("capture NBS:",st.record_capture(c1,[SeriesRow("2026-04","50.3"),SeriesRow("2026-05","50.0")]))
c2=SeriesCapture(series_id="china_pmi_manufacturing",unit="indice",definition="PMI manufatura China",dataset_id="pmi.spglobal.com",source_url="https://www.pmi.spglobal.com/Public/Home/PressRelease/8537e35754134e47b49b20cb288ead9c",document_sha256="b"*64,captured_at=datetime(2026,6,1,2,0,tzinfo=UTC),published_at=datetime(2026,6,1,1,45,tzinfo=UTC),published_precision="exact")
print("capture RatingDog (same series_id):",st.record_capture(c2,[SeriesRow("2026-04","52.2"),SeriesRow("2026-05","51.8")]))
for o in st.observations(): print(" obs",o.period,o.value,o.dataset_id,"revision_of=",(o.revision_of or '')[:8],"available_precision=",o.available_precision)
fr=st.first_release("china_pmi_manufacturing","2026-05"); print("first_release 2026-05 ->",fr.value,fr.dataset_id)
ao=st.as_of("china_pmi_manufacturing","2026-05",datetime(2026,6,2,tzinfo=UTC)); print("as_of 2026-06-02 ->",ao.value,ao.dataset_id,"revision_of set:",ao.revision_of is not None)
for prov,val in (("provedor nao nomeado","51.4"),("Reuters poll (via RTHK)","51.6")):
    cs=ConsensusSnapshot(provider=prov,contract="uso interno (licenca nao verificada)",series_id="china_pmi_manufacturing",competence="2026-05",value=val,unit="indice",definition="PMI manufatura China",captured_at=datetime(2026,5,30,12,0,tzinfo=UTC),version="v1")
    print(f"surprise(first_release, consensus {prov} {val}) ->",surprise(fr,cs).to_json())
