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

/* ── Calm, role-based colour palette ───────────────────────────────────────────
 * Fewer simultaneous hues, softer saturation, and stronger axis contrast than
 * the old neon set — easier on the eyes. Hues are drawn from a CVD-checked
 * categorical ramp; colour is assigned by the job it does, not decoration.      */
export const CHART = {
  grid: '#1b2532',
  tick: '#8b96a8',           // was #64748b — lifted for readability
  accent: '#33b79f',          // teal — primary / "actual"
  forecast: '#e0a44b',        // amber — model forecast
  blue: '#5590d9',
  positive: '#33b79f',        // diverging: linked to MORE typhoons
  negative: '#e0736e',        // diverging: linked to FEWER typhoons
  neutral: '#64748b',
  tooltip: {
    contentStyle: {
      background: '#141b26',
      border: '1px solid #263243',
      borderRadius: 8,
      fontSize: '0.78rem',
      color: '#e6ebf2',
      boxShadow: '0 6px 20px rgba(0,0,0,0.35)',
    },
    labelStyle: { color: '#e6ebf2', fontWeight: 600, marginBottom: 2 },
    cursor: { fill: 'rgba(255,255,255,0.03)' },
  },
} as const;

/** ENSO categories — cool=blue, warm=coral, neutral=slate (intuitive mapping). */
export const ENSO_FILL: Record<string, string> = {
  'El Nino': '#e0736e',
  'La Nina': '#5590d9',
  'Neutral': '#8a94a3',
};

export const MONTH_LABELS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
export const MONTH_INITIALS = ['J','F','M','A','M','J','J','A','S','O','N','D'];
export const MONTH_FULL = [
  'January','February','March','April','May','June',
  'July','August','September','October','November','December',
];

/** A few emphasis colours for the most-recent years; older years render muted. */
export const RECENT_YEAR_COLORS = ['#33b79f', '#5590d9', '#e0a44b'];
export const MUTED_YEAR = '#3a4658';

/* ── Shared aggregation helpers (compute once, reuse across pages) ─────────────*/

export interface YearTotal { year: number; total: number; predicted: boolean; }

/** Total typhoons per year, flagged if the year contains forecast months. */
export function yearTotals(rows: DataRow[]): YearTotal[] {
  const map = new Map<number, { total: number; predicted: boolean }>();
  for (const r of rows) {
    const e = map.get(r.year) ?? { total: 0, predicted: false };
    e.total += r.typhoons;
    e.predicted = e.predicted || r.predicted;
    map.set(r.year, e);
  }
  return [...map.entries()]
    .map(([year, v]) => ({ year, total: v.total, predicted: v.predicted }))
    .sort((a, b) => a.year - b.year);
}

/** Average typhoons for each calendar month (1–12), over the given rows. */
export function monthlyAverages(rows: DataRow[]): number[] {
  const sum = new Array(12).fill(0);
  const cnt = new Array(12).fill(0);
  for (const r of rows) { sum[r.month - 1] += r.typhoons; cnt[r.month - 1] += 1; }
  return sum.map((s, i) => (cnt[i] ? s / cnt[i] : 0));
}

/** Simple least-squares slope + intercept of y against x. */
export function linreg(x: number[], y: number[]): { slope: number; intercept: number } {
  const n = x.length;
  if (n < 2) return { slope: 0, intercept: y[0] ?? 0 };
  const mx = x.reduce((a, b) => a + b, 0) / n;
  const my = y.reduce((a, b) => a + b, 0) / n;
  let num = 0, den = 0;
  for (let i = 0; i < n; i++) { num += (x[i] - mx) * (y[i] - my); den += (x[i] - mx) ** 2; }
  const slope = den ? num / den : 0;
  return { slope, intercept: my - slope * mx };
}
