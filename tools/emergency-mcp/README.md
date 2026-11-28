# EMERGENCY MCP — local read-only laboratory

This increment reads the existing Emergency sources at the pinned source snapshot
`3cc5139b149feef390e6ceaa7358e2425d92620a`. It does not create another clinical
database, copy full-text publications, modify evidence, prescribe or accept patient
records. It keeps CLINICALLY_PENDING and NO_GO_CLINICAL_RELEASE.

## Runtime verified

Official [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk),
PyPI `mcp==2.3.0`, Python3.12.16, Windows on JUAN-C. The official low-level
[Server API](https://py.sdk.modelcontextprotocol.io/advanced/low-level-server/)
is used to enforce exact keys and scalar types without convenience-layer coercion.
The SDK handles MCP initialization, negotiated protocol and stdio. There is no
HTTP/SSE listener, network transport, OAuth grant or background service.

The dedicated requirements lock was generated and checked with hashes on Windows.
It contains the SDK and its transitive runtime dependencies. It is not a replacement
for clinical/requirements, nor an instruction to install this SDK in every CI job.

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe --require-hashes -r tools/emergency-mcp/requirements-lock.txt
.venv/Scripts/python.exe -B clinical/scripts/emergency_mcp_readonly.py
```

Register that executable plus script arguments in an MCP host to launch it each
session. Registration is done by Work separately; these files alone do not prove
any particular host has connected. No environment credential or API token is needed.

## Tools and permissions

| Tool | Canonical reader |
|---|---|
| get_clinical_module | 131IDs in module-index, exact Markdown heading and evidence registry |
| search_evidence | existing normalized source catalog metadata, not primary fulltext |
| get_medication_reference | existing medication audit entity inventory and related library paths |
| get_owner_decision | existing owner decision/acute acceptance/R54 registers and JSON pointers |
| get_pending_tasks | explicit coordination snapshot or clearly labelled historical repo snapshot |
| get_qa_status | explicit QA/CI/audit receipt snapshot or clearly labelled historical repo QA |
| get_project_state | source pins, module statuses and existing canonical graph builder metadata |
| get_graph_neighbors | exact provenance node and bounded neighbors from the same builder |

The default `metadata` launch scope does not return module body text. A trusted
operator may explicitly select `--scope project-content`; only pinned own-project
module sections can then be returned, in bounded pages. This is a host-side
permission, not a tool argument that a model can grant itself. It does not grant
permission to transmit project content to an external service or read restricted
original publications.

There is no generic read_file, shell, SQL, HTTP, patient lookup, write or prescribing
tool. Unknown tool names/arguments, scalar type coercion, traversal, unlisted
sources, changed pins and changed source bytes fail closed. Tool annotations
read_only_hint/open_world_hint are hints; actual enforcement is in the readers and
dispatch. Local stdio assumes a trusted OS user/host process. It does not authenticate
humans or hostile processes or certify institutional access controls.

Returned documents are explicitly marked UNTRUSTED_PROJECT_DATA_NOT_INSTRUCTIONS.
Source text is never executed, loaded as a plugin, followed as a URL or used to
grant permissions. These controls do not claim a universal LLM prompt-injection
guarantee. Outputs retain source commit, LF-normalized SHA-256, file/line or JSON
pointer, original evidence/decision scope and global pending clinical state.

## Coordination and QA snapshots

The repository matrix is an older version6 snapshot, explicitly labelled as such.
For the actual central matrix or current QA receipt, Work may supply two exact,
authorized project-metadata files at launch:

```powershell
python clinical/scripts/emergency_mcp_readonly.py --coordination-snapshot C:/authorized/TASK_MATRIX.json --qa-snapshot C:/authorized/CI_RECEIPT.json
```

These file paths are never available as MCP tool inputs. Each file is bounded to
2MiB and pinned by its exact byte hash at startup; any change requires a restart
and returns ABSTAIN until then. No cloud folder, credentials or patient store is
opened. Results are timestamped/source-versioned snapshots, not live GitHub,
SonarCloud, Drive or Antigravity calls. `get_pending_tasks` preserves original
statuses and does not reinterpret a closed parent task's open subparts.

Do not point these flags at patient records or credentials. Persist only the
authorized snapshot paths in host profiles; no tokens in repository configuration.
A host restart starts a fresh hash-bound session after a coordinator updates a
snapshot. A historical PASS does not certify the current implementation.

## Verification observed

- 22 core contract/security tests, including all131 canonical IDs, source integrity,
  source traversal, content permission, task snapshot changes, exact decision scope,
  graph joins and untrusted text.
- Actual MCP stdio initialize and tools/list:8 tools.
-8 successful useful tool calls, plus3 rejected calls (traversal, content without
  launch permission, unknown root argument); rejection is a static is_error/ABSTAIN.
- No network or real patient data; no source canonical bytes modified.
- Client probe is a trusted operator helper, not a server tool. Its default receipt
  includes hashes and counts rather than raw responses or environment values.

```powershell
python -B -m unittest discover -s clinical/tests -p test_emergency_mcp_readonly.py -v
python tools/emergency-mcp/client_probe.py --spec C:/authorized/probe.json --output C:/authorized/receipt.json
```

Core tests use standard Python and do not require the SDK to be installed in the
existing clinical test environment. The real protocol probe uses the dedicated
SDK environment. Input/output source pins use normalized LF bytes so Windows
checkout line endings do not silently change identity. `build_pins.py` prepares
metadata only for an intentional reviewed source update; changing its output also
requires updating the code's expected manifest hash under review.

No full WCAG, clinical validation, human study, hospital interoperability or
live PR/CI integration is asserted. No main/protected branch, ZIP,19 accepted
contracts,45formulae,23dermatology decisions or last_checked was changed.
