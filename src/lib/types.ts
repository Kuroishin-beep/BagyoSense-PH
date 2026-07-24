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
  predicted: boolean;
}

export interface ModelMetrics {
  cvR2: number | null;
  cvRmse?: number | null;
  testR2: number | null;
  rmse: number | null;
  mae: number | null;
}

export interface Baseline {
  name: string;
  r2: number;
  rmse: number;
  mae: number;
}

export interface FeatureImportance {
  feature: string;
  importance: number;
  direction: 'up' | 'down';
}

export interface ModelData {
  features: string[];
  scaler: { mean: number[]; scale: number[] };
  coefficients: number[];
  intercept: number;
  metrics: Record<string, ModelMetrics>;
  baseline?: Baseline;
  featureImportance?: FeatureImportance[];
  bestModel: string;
  predictorModel?: string;
  dataThrough?: string;
  holdoutMonths?: number;
  illustrative?: boolean;
  note?: string;
}
