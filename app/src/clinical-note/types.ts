export type QualitativeConfidence = 'high' | 'moderate' | 'low';
export type ReviewState = 'pending' | 'accepted' | 'rejected';

export type ReportItem = {
  kind: string;
  time_label: string | null;
  provenance: string;
  source_reference: string | null;
  official_report: string | null;
  ai_interpretation: string | null;
  findings: string | null;
  impression: string | null;
  limitations: string[];
  privacy_checked: boolean;
  burned_in_identifiers_checked: boolean;
  routed_modules?: string[];
};

export type DiagnosticCandidate = {
  diagnosis: string;
  confidence: QualitativeConfidence;
  evidence_for: string[];
  evidence_against: string[];
  missing_discriminating_data: string[];
  source_modules: string[];
};

export type Suggestion = {
  action: string;
  priority?: 'immediate' | 'urgent' | 'routine';
  rationale?: string | null;
  source_modules?: string[];
};

export type ClinicalAssessment = {
  problem_representation: string | null;
  active_problems: string[];
  likely_diagnoses: DiagnosticCandidate[];
  differential_diagnoses: DiagnosticCandidate[];
  must_not_miss: DiagnosticCandidate[];
  suggested_tests: Suggestion[];
  treatment_suggestions: Suggestion[];
  disposition: Suggestion[];
  reassessment: Suggestion[];
  contradictions_to_clarify: string[];
  limitations: string[];
};

export type ClinicalNotePayload = {
  schema_version: '1.0';
  language: 'pt-PT' | 'es-ES' | 'en' | 'zh';
  encounter: {
    encounter_id: string;
    age: { years: number | null; months: number | null };
    sex: 'female' | 'male' | 'intersex' | 'unknown';
    origin: string | null;
    transfer_status: string | null;
    functional_status: string | null;
    cognitive_status: string | null;
    living_context: string | null;
  };
  history: {
    chief_complaint: string | null;
    present_illness: string | null;
    past_medical_history: string[];
    past_surgical_history: string[];
    chronic_medications: { name: string; dose: string | null; schedule: string | null; source: string | null }[];
    medication_discrepancies: string[];
    allergies: { substance: string | null; class: string | null; reaction: string | null; severity: string | null; confirmed: boolean | null }[];
    social_history: string | null;
    baseline_status: string | null;
    source_reliability: string | null;
  };
  timeline: { time_label: string; event: string; source: string | null }[];
  exam: {
    vitals: {
      time_label: string | null;
      bp: string | null;
      hr: number | null;
      rr: number | null;
      spo2: number | null;
      oxygen: string | null;
      temperature_c: number | null;
      gcs: string | null;
      source: string | null;
    }[];
    general: string | null;
    neurologic: string | null;
    respiratory: string | null;
    cardiovascular: string | null;
    abdominal: string | null;
    skin_wounds: string | null;
    extremities: string | null;
    other: string | null;
  };
  complementary_tests: {
    laboratory: ReportItem[];
    blood_gas: ReportItem[];
    ecg: ReportItem[];
    imaging: ReportItem[];
    microbiology: ReportItem[];
    other: ReportItem[];
  };
  assessment: ClinicalAssessment;
  clinician_validation: {
    reviewed: boolean;
    reviewer_role: string | null;
    reviewed_at: string | null;
    changes_made: string | null;
  };
  privacy: {
    mode: 'clinical_pseudonymized' | 'external_anonymized';
    direct_identifiers_removed: boolean;
    free_text_screened: boolean;
    source_metadata_checked: boolean;
    burned_in_identifiers_checked: boolean;
    export_allowed: boolean;
    privacy_notes: string[];
  };
};

export type PreparedUpload = {
  api_version: string;
  upload_id: string;
  filename: string;
  mime_type: string;
  size_bytes: number;
  sha256: string;
  kind: string;
  route: { kind: string; target_section: keyof ClinicalNotePayload['complementary_tests']; modules: string[] };
  privacy: {
    status: 'PASS' | 'REVIEW_REQUIRED' | 'STOP';
    findings: { severity: string; code: string; message: string; path?: string }[];
    manual_file_privacy_review_required: boolean;
    burned_in_identifier_review_required: boolean;
  };
  extracted: { official_report: string | null; ai_interpretation: string | null };
  processing: {
    status: 'text_extracted' | 'routed_external' | 'vision_interpreted';
    message: string;
    modules: string[];
    provider?: string | null;
    model?: string | null;
    confidence?: QualitativeConfidence | null;
    findings?: string | null;
    impression?: string | null;
    limitations?: string[];
  };
  original_retained: false;
};

export type DiagnosticApiResponse = {
  blocked: boolean;
  issues: { severity: string; code: string; message: string }[];
  signals?: { code: string; weight: number; label: string }[];
  rule_hits?: { module: string; score: number; evidence: string[] }[];
  assessment: ClinicalAssessment | null;
  note: ClinicalNotePayload | null;
  medication_safety_gate: {
    status: 'REVIEW_REQUIRED' | 'NOT_APPLICABLE';
    actionable: boolean;
    required_module: string | null;
    message: string;
  };
};
