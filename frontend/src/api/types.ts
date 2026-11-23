// Mirror of backend/fairsched/schema.py (the source of truth; JSON Schema in /schemas).
// Keep in sync when the schema changes. All times are minutes since clinic opens.

export type PolicyName = "fifo" | "sjf" | "urgency" | "wspt" | "optimal";

export interface Patient {
  id: string;
  arrival_time: number;
  visit_length: number;
  urgency: number; // 1 (routine) .. 5 (critical)
  group: string;
}

export interface Provider {
  id: string;
  name: string;
  shift_start: number;
  shift_end: number;
}

export interface DatasetMeta {
  name: string;
  schema_version: string;
  seed: number | null;
  horizon: number;
  groups: string[];
  description: string;
}

export interface Dataset {
  meta: DatasetMeta;
  providers: Provider[];
  patients: Patient[];
}

export interface GeneratorParams {
  name?: string;
  n_patients?: number;
  n_providers?: number;
  horizon?: number;
  group_mix?: Record<string, number>;
  urgency_weights?: number[]; // length 5, for urgency 1..5
  visit_length_min?: number;
  visit_length_max?: number;
  seed?: number | null;
}

export interface WeightConfig {
  urgency_power: number;
  group_multipliers: Record<string, number>;
  aging_rate: number;
}

export interface SimulationRequest {
  dataset: Dataset;
  policies: PolicyName[];
  weights?: WeightConfig;
  top_k?: number;
}

export interface Appointment {
  patient_id: string;
  provider_id: string;
  start: number;
  end: number;
  wait: number;
  order: number;
}

export interface Schedule {
  policy: PolicyName;
  appointments: Appointment[];
  unserved: string[];
}

export interface PatientWait {
  patient_id: string;
  wait: number;
}

export interface WaitStats {
  count: number;
  mean: number;
  median: number;
  p90: number;
  max: number;
  top_k: PatientWait[];
}

export interface FairnessStats {
  n: number;
  inversions_vs_arrival: number;
  inversions_vs_urgency: number;
  disagreement_vs_arrival: number; // 0..1
  disagreement_vs_urgency: number; // 0..1
}

export interface GroupMetrics {
  group: string;
  served: number;
  unserved: number;
  waits: WaitStats;
  fairness: FairnessStats;
}

export interface PolicyMetrics {
  served: number;
  unserved: number;
  makespan: number;
  total_weighted_wait: number;
  provider_utilization: Record<string, number>;
  waits: WaitStats;
  fairness: FairnessStats;
  per_group: GroupMetrics[];
}

export interface EngineInfo {
  scheduler: "team" | "reference";
  analytics: "team" | "reference";
}

export interface PolicyResult {
  policy: PolicyName;
  schedule: Schedule;
  metrics: PolicyMetrics;
  engine: EngineInfo;
  runtime_ms: number;
}

export interface SimulationResponse {
  schema_version: string;
  dataset_name: string;
  weights: WeightConfig;
  results: PolicyResult[];
}

export interface PolicyInfo {
  name: PolicyName;
  description: string;
  max_patients: number | null;
}
