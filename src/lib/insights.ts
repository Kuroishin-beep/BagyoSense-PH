/**
 * Turns the dataset into a handful of plain-language findings.
 *
 * Every statement here is a pattern measured directly in the loaded data and is
 * phrased as such ("in this dataset…") — nothing is presented as an official
 * forecast. This is what powers the in-app Insights panel.
 */

import type { DataRow, ModelData } from './types';
import { pearson, monthlyAverages, yearTotals, linreg, MONTH_FULL } from './data';
import { FEATURE_BY_KEY, type FeatureInfo } from './features';

export interface Insight {
  icon: string;
  title: string;
  text: string;
}

const CORRELATED: FeatureInfo['key'][] =
  ['oni', 'nino34', 'wPacSST', 'windShear', 'humidity', 'slp', 'prevMonth'];

export function buildInsights(rows: DataRow[], model: ModelData | null): Insight[] {
  const actual = rows.filter(r => !r.predicted);
  const forecast = rows.filter(r => r.predicted);
  if (!actual.length) return [];

  const insights: Insight[] = [];

  // 1 — Season concentration (Jun–Nov)
  const total = actual.reduce((s, r) => s + r.typhoons, 0);
  const peakTotal = actual.filter(r => r.month >= 6 && r.month <= 11)
    .reduce((s, r) => s + r.typhoons, 0);
  const peakShare = Math.round((peakTotal / total) * 100);
  insights.push({
    icon: '🌀',
    title: 'The season is short and intense',
    text: `About ${peakShare}% of all typhoons in this dataset arrive between June and November. The other six months are usually quiet.`,
  });

  // 2 — Busiest month
  const avgs = monthlyAverages(actual);
  const peakIdx = avgs.indexOf(Math.max(...avgs));
  insights.push({
    icon: '📅',
    title: `${MONTH_FULL[peakIdx]} is the busiest month`,
    text: `On average, ${MONTH_FULL[peakIdx]} sees the most typhoons — about ${avgs[peakIdx].toFixed(1)} per year across the record.`,
  });

  // 3 — La Niña vs El Niño
  const avgPer = (phase: DataRow['ensoPhase']) => {
    const v = actual.filter(r => r.ensoPhase === phase);
    return v.length ? v.reduce((s, r) => s + r.typhoons, 0) / v.length : 0;
  };
  const laNina = avgPer('La Nina');
  const elNino = avgPer('El Nino');
  if (laNina > 0 && elNino > 0) {
    const laNinaBusier = laNina >= elNino;
    const busier = laNinaBusier ? 'La Niña' : 'El Niño';
    const calmer = laNinaBusier ? 'El Niño' : 'La Niña';
    const pct = Math.round((Math.abs(laNina - elNino) / Math.max(elNino, laNina)) * 100);
    insights.push({
      icon: '🌊',
      title: `${busier} months run busier`,
      text: `In this dataset, ${busier} months average about ${pct}% more typhoons than ${calmer} months.` +
        (laNinaBusier ? ' That fits the known El Niño calming effect.' : ''),
    });
  }

  // 4 — Strongest driver (by correlation strength, with plain direction)
  const typ = actual.map(r => r.typhoons);
  let best: { key: FeatureInfo['key']; r: number } | null = null;
  for (const key of CORRELATED) {
    const r = pearson(actual.map(d => d[key] as number), typ);
    if (!best || Math.abs(r) > Math.abs(best.r)) best = { key, r };
  }
  if (best) {
    const f = FEATURE_BY_KEY[best.key];
    const dir = best.r < 0 ? 'fewer' : 'more';
    insights.push({
      icon: '🔗',
      title: `${f.label} moves most with typhoons`,
      text: `Higher ${f.label.toLowerCase()} lines up with ${dir} typhoons in this dataset. ${f.meaning}`,
    });
  }

  // 5 — Long-term trend
  const yt = yearTotals(actual);
  if (yt.length >= 3) {
    const { slope } = linreg(yt.map(y => y.year), yt.map(y => y.total));
    const perDecade = Math.round(slope * 10);
    if (Math.abs(perDecade) >= 1) {
      insights.push({
        icon: slope >= 0 ? '📈' : '📉',
        title: slope >= 0 ? 'A gentle upward drift' : 'A gentle downward drift',
        text: `Annual totals have ${slope >= 0 ? 'risen' : 'fallen'} by roughly ${Math.abs(perDecade)} typhoons per decade over the record — a weak trend, easily swamped by year-to-year swings.`,
      });
    }
  }

  // 6 — Forecast summary
  if (forecast.length) {
    const fTotal = forecast.reduce((s, r) => s + r.typhoons, 0);
    const avgYear = total / new Set(actual.map(r => r.year)).size;
    const cmp = fTotal >= avgYear ? 'near or above' : 'below';
    insights.push({
      icon: '🔮',
      title: 'What the model expects next',
      text: `Under the current climate scenario the model projects about ${fTotal} typhoons over the next 12 months — ${cmp} the typical year (~${avgYear.toFixed(0)}). Treat this as illustrative, not an official forecast.`,
    });
  }

  return insights;
}
