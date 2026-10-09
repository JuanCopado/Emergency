import generated from '../data/generatedProcedures.json';

export type CanonicalProcedure = {
  id: string;
  name: string;
  level: string;
  family: string;
  sourcePath: string;
  sourceHeading: string;
  aliases: string[];
};

export const canonicalProcedures: CanonicalProcedure[] = generated;
const byId = new Map(canonicalProcedures.flatMap((procedure) =>
  [procedure.id, ...procedure.aliases].map((id) => [id, procedure] as const),
));

// Alias lookup returns the same canonical object and source, never another card.
export const getCanonicalProcedure = (id: string) => byId.get(id);
