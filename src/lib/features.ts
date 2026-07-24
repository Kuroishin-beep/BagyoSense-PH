/**
 * Plain-language dictionary for the nine climate inputs.
 *
 * This is the single source of truth used by the predictor sliders, the
 * correlation chart labels, and the info tooltips — so a term is explained the
 * same way everywhere and the jargon lives in exactly one place.
 */

import type { DataRow } from './types';

export interface FeatureInfo {
  /** Matches the DataRow field and the model.json feature order. */
  key: 'month' | 'oni' | 'nino34' | 'wPacSST' | 'windShear'
     | 'humidity' | 'slp' | 'mjoPhase' | 'prevMonth';
  /** Short, friendly label for axes and sliders. */
  label: string;
  /** The technical name, shown small/secondary for the curious. */
  technical: string;
  /** Unit suffix for values (e.g. '%', ' hPa'), or '' for none. */
  unit: string;
  /** One plain sentence: what this measures. */
  what: string;
  /** One plain sentence: what it means for typhoons. */
  meaning: string;
  /** Slider bounds for the predictor. */
  min: number;
  max: number;
  step: number;
  init: number;
}

export const FEATURES: FeatureInfo[] = [
  {
    key: 'month', label: 'Month', technical: 'Month of year', unit: '',
    what: 'The month we are forecasting.',
    meaning: 'The Philippine typhoon season peaks from June to November.',
    min: 1, max: 12, step: 1, init: 8,
  },
  {
    key: 'oni', label: 'El Niño / La Niña', technical: 'ONI', unit: '',
    what: 'A Pacific Ocean temperature pattern that shifts weather worldwide.',
    meaning: 'El Niño (positive) usually calms typhoons; La Niña (negative) tends to bring more.',
    min: -2.5, max: 2.5, step: 0.05, init: 0,
  },
  {
    key: 'nino34', label: 'Central Pacific warmth', technical: 'Niño 3.4 SST anomaly', unit: '°C',
    what: 'How much warmer or cooler than usual the central Pacific Ocean is.',
    meaning: 'Closely tracks El Niño / La Niña and the storms it drives.',
    min: -2.5, max: 2.5, step: 0.05, init: 0,
  },
  {
    key: 'wPacSST', label: 'Local sea warmth', technical: 'W. Pacific SST anomaly', unit: '°C',
    what: 'How warm the ocean is near the Philippines.',
    meaning: 'Warm seas are the fuel that lets storms form and grow.',
    min: -1.5, max: 1.5, step: 0.05, init: 0,
  },
  {
    key: 'windShear', label: 'Wind shear', technical: 'Vertical wind shear', unit: ' m/s',
    what: 'How much the wind changes speed and direction with height.',
    meaning: 'Strong shear tears storms apart, so more shear usually means fewer typhoons.',
    min: 5, max: 16, step: 0.1, init: 8,
  },
  {
    key: 'humidity', label: 'Air moisture', technical: 'Mid-level humidity', unit: '%',
    what: 'How moist the middle of the atmosphere is.',
    meaning: 'Moist air helps thunderstorms build into typhoons.',
    min: 45, max: 80, step: 0.5, init: 68,
  },
  {
    key: 'slp', label: 'Air pressure', technical: 'Sea-level pressure', unit: ' hPa',
    what: 'The weight of the air pressing down at sea level.',
    meaning: 'Lower pressure gives storms more room to spin up.',
    min: 1002, max: 1013, step: 0.1, init: 1005,
  },
  {
    key: 'mjoPhase', label: 'Tropical rain band', technical: 'MJO phase (0–8)', unit: '',
    what: 'The position of a giant band of rain clouds that circles the tropics.',
    meaning: 'Some positions push wet, stormy weather over the Philippines.',
    min: 0, max: 8, step: 1, init: 4,
  },
  {
    key: 'prevMonth', label: "Last month's storms", technical: 'Previous-month count', unit: '',
    what: 'How many typhoons happened the month before.',
    meaning: 'Activity tends to cluster — a busy month often follows another.',
    min: 0, max: 8, step: 1, init: 1,
  },
];

/** Lookup by key, for labelling charts and tooltips. */
export const FEATURE_BY_KEY: Record<FeatureInfo['key'], FeatureInfo> =
  Object.fromEntries(FEATURES.map(f => [f.key, f])) as Record<FeatureInfo['key'], FeatureInfo>;

/** Format a value with its unit (month → month name handled by caller). */
export function formatFeature(key: FeatureInfo['key'], value: number): string {
  const f = FEATURE_BY_KEY[key];
  const rounded = f.step >= 1 ? Math.round(value) : value;
  return `${rounded}${f.unit}`;
}

/** Plain-language name for the current El Niño / La Niña state. */
export function ensoFromOni(oni: number): DataRow['ensoPhase'] {
  if (oni >= 0.5) return 'El Nino';
  if (oni <= -0.5) return 'La Nina';
  return 'Neutral';
}

/** Short, friendly one-liners describing what each ENSO state tends to do. */
export const ENSO_INFO: Record<DataRow['ensoPhase'], { title: string; blurb: string }> = {
  'El Nino': { title: 'El Niño', blurb: 'Warmer central Pacific — typically fewer typhoons reach the Philippines.' },
  'La Nina': { title: 'La Niña', blurb: 'Cooler central Pacific — typically more typhoons reach the Philippines.' },
  'Neutral': { title: 'Neutral', blurb: 'Neither El Niño nor La Niña — activity near the long-term average.' },
};
