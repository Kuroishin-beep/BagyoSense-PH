import { DataRow } from './types';

let cache: DataRow[] | null = null;

export async function loadData(): Promise<DataRow[]> {
  if (cache) return cache;
  const res = await fetch('/data.json');
  cache = await res.json();
  return cache!;
}

export function pearson(x: number[], y: number[]): number {
  const n = x.length;
  if (n === 0) return 0;
  const mx = x.reduce((a, b) => a + b, 0) / n;
  const my = y.reduce((a, b) => a + b, 0) / n;
  let num = 0, dx2 = 0, dy2 = 0;
  for (let i = 0; i < n; i++) {
    const dx = x[i] - mx;
    const dy = y[i] - my;
    num += dx * dy;
    dx2 += dx * dx;
    dy2 += dy * dy;
  }
  const den = Math.sqrt(dx2 * dy2);
  return den === 0 ? 0 : num / den;
}

export const CHART = {
  grid: '#1e293b',
  tick: '#64748b',
  primary: '#10b981',
  blue: '#3b82f6',
  purple: '#8b5cf6',
  amber: '#f59e0b',
  red: '#ef4444',
  tooltip: {
    contentStyle: {
      background: '#111827',
      border: '1px solid #1e293b',
      borderRadius: 6,
      fontSize: '0.72rem',
    },
    labelStyle: { color: '#e2e8f0' },
  },
} as const;

export const ENSO_FILL: Record<string, string> = {
  'El Nino': '#ef4444',
  'La Nina': '#3b82f6',
  'Neutral': '#10b981',
};

export const MONTH_LABELS = ['J','F','M','A','M','J','J','A','S','O','N','D'];
export const MONTH_FULL = [
  'January','February','March','April','May','June',
  'July','August','September','October','November','December',
];

export const YEAR_COLORS = [
  '#10b981','#3b82f6','#8b5cf6','#f59e0b','#ef4444',
  '#06b6d4','#f43f5e','#14b8a6','#a855f7','#eab308','#22d3ee',
];
