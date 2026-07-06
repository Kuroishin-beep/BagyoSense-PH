import { ModelData } from './types';

let cache: ModelData | null = null;

export async function loadModel(): Promise<ModelData> {
  if (cache) return cache;
  const res = await fetch('/model.json');
  cache = await res.json();
  return cache!;
}

export function predict(model: ModelData, features: number[]): number {
  const { scaler, coefficients, intercept } = model;
  let pred = intercept;
  for (let i = 0; i < features.length; i++) {
    const scaled = (features[i] - scaler.mean[i]) / scaler.scale[i];
    pred += scaled * coefficients[i];
  }
  return Math.max(0, Math.min(12, Math.round(pred)));
}
