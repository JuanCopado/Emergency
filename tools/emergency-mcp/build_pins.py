from pathlib import Path
import json,hashlib,re,subprocess
r=Path(__file__).resolve().parents[2]
SOURCE_COMMIT='a4e84b008e08ef67f41ff1645832b88821d3bb92'
def source_bytes(path):
 return subprocess.check_output(['git','show',f'{SOURCE_COMMIT}:{path}'],cwd=r).replace(b'\r\n',b'\n')
paths=['STATE.md','clinical/references/module-index.md','clinical/references/evidence-registry.json','clinical/references/evidence-sources.json','clinical/references/owner-decisions-2026-11-27.json','clinical/references/acute-contract-owner-acceptance-2026-11-16.json','clinical/qa/R54_MEDICAL_OWNER_DECISIONS_20261124.json','clinical/qa/global-medication-audit-v144/entity-inventory.json','clinical/qa/global-medication-audit-v144/products.json','clinical/qa/global-medication-audit-v144/regimens.json','clinical/pharmacology/corticosteroids.json','docs/coordination/supercoord-20261127/TASK_MATRIX.json','docs/coordination/clinical-minimal-http-20261127/CLINICAL_MINIMAL_HTTP_QA.json','clinical/scripts/build_project_graph.py']
text=source_bytes('clinical/references/module-index.md').decode('utf8')
paths+=['clinical/'+p for p in re.findall(r'^\| [a-z0-9-]+ \| `([^`]+)` \|$',text,re.M)]
records={}
for p in sorted(set(paths)):
 b=source_bytes(p)
 records[p]={'sha256_lf':hashlib.sha256(b).hexdigest(),'bytes_lf':len(b)}
d={'schema':'emergency-mcp-source-pins-v1','source_commit':SOURCE_COMMIT,'hash_mode':'UTF8 LF-normalized source bytes','files':records}
out=r/'tools/emergency-mcp/source-pins.json';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8',newline='\n')
print(hashlib.sha256(out.read_bytes()).hexdigest(),len(records))
