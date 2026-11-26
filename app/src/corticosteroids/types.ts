export type CorticosteroidLocale = 'es' | 'pt' | 'en' | 'zh';
export type LocalizedName = Record<CorticosteroidLocale, string>;
export type SystemicRoute = 'oral' | 'iv';
export type DoseBasis = 'single_dose' | 'daily_total';

export interface ReferenceSource {
  id: string;
  title: string;
  version: string;
  url: string;
  locator: string;
  checked_on: string;
  access: string;
}
export interface CorticosteroidDrug {
  id: string;
  name: LocalizedName;
  mineralocorticoid_relative_activity: number;
  mineralocorticoid_source_id: string;
}
export interface EquivalenceRow {
  drug_id: string;
  equivalent_mg: number;
  biological_half_life_hours: [number, number];
}
export interface EquivalenceTable {
  id: string;
  source_id: string;
  label: string;
  rows: EquivalenceRow[];
}
interface IndicationReference {
  module_id: string;
  source_ids: string[];
  summary_es: string;
  existing_acceptance?: string;
}
export interface CorticosteroidCatalog {
  source_path: string;
  source_sha256: string;
  schema_version: string;
  version: string;
  module_id: string;
  clinical_status: string;
  scope: {
    purpose: string;
    supported_routes: SystemicRoute[];
    unit: 'mg';
    excluded_routes: string[];
    not_equivalent: string[];
    clinical_text_language: 'es';
  };
  sources: ReferenceSource[];
  drugs: CorticosteroidDrug[];
  tables: EquivalenceTable[];
  hydrocortisone: {
    adult_adrenal_crisis: IndicationReference & {
      initial_mg: number;
      initial_routes: string[];
      maintenance_total_mg_per_24h: number;
      maintenance_alternative_mg: number;
      maintenance_interval_hours: number;
    };
    adult_septic_shock: IndicationReference & {
      common_regimen_total_mg_per_24h: number;
      common_regimen_divided_mg: number;
      common_regimen_interval_hours: number;
      not_pediatric: boolean;
    };
    pediatric_adrenal_crisis: IndicationReference & {
      product: string;
      initial_routes: string[];
      maintenance_route: string;
      maintenance_interval_hours: number;
      rows: { age_label: LocalizedName; initial_mg: number; maintenance_mg: [number, number] }[];
    };
    pediatric_septic_shock: IndicationReference;
    anaphylaxis: IndicationReference;
  };
  short_courses: {
    bell_palsy: {
      module_id: 'ent-emergencies';
      section_id: 'bell-palsy';
      source_ids: string[];
      guideline_min_age_years: number;
      adult_draft_min_age_years: number;
      onset_window_hours: number;
      reference_regimen: {
        drug_id: string;
        dose_mg: number;
        route: 'oral';
        interval_hours: number;
        duration_days: number;
        total_mg_per_day: number;
        source_id: string;
      };
      indication_es: string;
      regimen_scope_es: string;
      pediatric_es: string;
      eye_care_es: string;
      differential_es: string;
      safety_es: string;
      follow_up_es: string;
    };
    duration_withdrawal: { source_ids: string[]; summary_es: string };
    existing_module_ids: string[];
  };
  related_modules: { id: string; population: 'adult' | 'pediatric'; title_es: string; agent_ids: string[] }[];
}
