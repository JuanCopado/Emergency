// Direct imports from the source-preserving clinical JSON; no copied clinical text.
import femoral from '../../../clinical/data/procedures/PROC-VASC-007.json';
import jugular from '../../../clinical/data/procedures/PROC-VASC-006.json';
import radial from '../../../clinical/data/procedures/PROC-VASC-010.json';
import cric from '../../../clinical/data/procedures/PROC-AIR-015.json';
import chest from '../../../clinical/data/procedures/PROC-THX-003.json';
import pericardial from '../../../clinical/data/procedures/PROC-CV-006.json';
import cardioversion from '../../../clinical/data/procedures/PROC-CV-001.json';
import pacing from '../../../clinical/data/procedures/PROC-CV-004.json';
import binder from '../../../clinical/data/procedures/PROC-TRA-004.json';
import shoulder from '../../../clinical/data/procedures/PROC-ORTHO-001.json';

export type ProcedurePilot = {
  procedure_id: string; name: string; family: string; level: string; status: string;
  rescue: string[] | null; escalation: string[] | null;
  provenance: { source_path: string; family_preamble: string; sections: Record<string, string> };
};
export const procedurePilots: ProcedurePilot[] = [femoral, jugular, radial, cric, chest, pericardial, cardioversion, pacing, binder, shoulder];
export const getProcedurePilot = (id: string) => procedurePilots.find(p => p.procedure_id === id);
