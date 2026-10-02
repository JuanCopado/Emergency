# QA MATRIX — v1.36

| Gate | Check | Automated | Failure blocks release | Human required |
|---|---|---:|---:|---:|
| QA-1 | Manifest IDs resolve to exactly one bundle section | yes | yes | no |
| QA-1 | Router references known modules | yes | yes | no |
| QA-1 | No unindexed/duplicate module sections | yes | yes | no |
| QA-2 | Every manifest module has evidence record | yes | yes | no |
| QA-2 | Evidence status/date/source/version valid | yes | yes | no |
| QA-2 | High-risk module explicitly classified | yes | yes | no |
| QA-3 | Sourced clinical regression cases valid | yes | yes | no |
| QA-3 | Unit/regression tests pass | yes | yes | no |
| QA-4 | Continuous infusion invariants preserve concentration + mL/h | yes | yes | yes for release |
| QA-4 | High-risk doses/energies have explicit source/version | partial | yes | yes |
| QA-5 | Portugal/Azores local product/protocol reconciled where operational | no | yes for local release | yes |
| QA-5 | Human reviewer recorded for high-risk release | no | yes | yes |
| Imaging | Provenance/leakage validation | yes | yes | no |
| Imaging | Blinded diagnostic performance | no | no* | yes |

*Absence of diagnostic validation prevents claims of validated diagnostic accuracy but does not block use of the workflow as an explicitly unvalidated aid.
