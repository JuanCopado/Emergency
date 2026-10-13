import sheets from '../data/generatedProcedureSheets.json';
import type { ProcedurePilot } from './procedurePilots';

export const procedureSheets: ProcedurePilot[] = sheets as ProcedurePilot[];
const byId = new Map(procedureSheets.map(sheet => [sheet.procedure_id, sheet]));
export const getProcedureSheet = (id:string) => byId.get(id);
