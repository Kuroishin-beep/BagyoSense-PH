export interface DataRow {
  year: number;
  month: number;
  monthName: string;
  typhoons: number;
  oni: number;
  nino34: number;
  wPacSST: number;
  windShear: number;
  humidity: number;
  slp: number;
  mjoPhase: number;
  prevMonth: number;
  ensoPhase: 'El Nino' | 'La Nina' | 'Neutral';
  season: 'Peak' | 'Off-Season';
}

export interface ModelMetrics {
  cvR2: number | null;
  testR2: number | null;
  rmse: number | null;
  mae: number | null;
}

export interface ModelData {
  features: string[];
  scaler: { mean: number[]; scale: number[] };
  coefficients: number[];
  intercept: number;
  metrics: Record<string, ModelMetrics>;
  bestModel: string;
}
