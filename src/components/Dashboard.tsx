'use client';

import { useEffect, useState, useMemo } from 'react';
import {
  BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Line, ComposedChart,
} from 'recharts';
import { DataRow, ModelData } from '@/lib/types';
import {
  loadData, pearson, CHART, ENSO_FILL, MONTH_LABELS,
  yearTotals, monthlyAverages, linreg,
} from '@/lib/data';
import { loadModel } from '@/lib/predict';
import { FEATURE_BY_KEY } from '@/lib/features';
import { buildInsights } from '@/lib/insights';
import KPICard from './KPICard';
import InfoDot from './InfoDot';
import Insights from './Insights';
import Disclaimer from './Disclaimer';

const CORR_KEYS = ['oni', 'nino34', 'wPacSST', 'windShear', 'humidity', 'slp', 'prevMonth'] as const;

export default function Dashboard() {
  const [data, setData] = useState<DataRow[]>([]);
  const [model, setModel] = useState<ModelData | null>(null);
  useEffect(() => { loadData().then(setData); loadModel().then(setModel).catch(() => {}); }, []);

  const actual = useMemo(() => data.filter(d => !d.predicted), [data]);
  const predicted = useMemo(() => data.filter(d => d.predicted), [data]);
  const insights = useMemo(() => buildInsights(data, model), [data, model]);

  const kpis = useMemo(() => {
    if (!actual.length) return null;
    const total = actual.reduce((s, d) => s + d.typhoons, 0);
    const yt = yearTotals(actual);
    const avg = (total / yt.length).toFixed(1);
    const worst = yt.reduce((a, b) => (b.total > a.total ? b : a));
    const pred = predicted.reduce((s, d) => s + d.typhoons, 0);
    return { total, avg, worst, pred, years: yt.length };
  }, [actual, predicted]);

  const annual = useMemo(() => {
    const yt = yearTotals(data);
    const actualYt = yt.filter(y => !y.predicted);
    const { slope, intercept } = linreg(actualYt.map(y => y.year), actualYt.map(y => y.total));
    return yt.map(y => ({
      year: y.year.toString(),
      actual: y.predicted ? 0 : y.total,
      forecast: y.predicted ? y.total : 0,
      trend: Math.round((slope * y.year + intercept) * 10) / 10,
    }));
  }, [data]);

  const monthly = useMemo(() => {
    const avgs = monthlyAverages(actual);
    return MONTH_LABELS.map((month, i) => ({ month, avg: Math.round(avgs[i] * 100) / 100 }));
  }, [actual]);

  const enso = useMemo(() => (['La Nina', 'Neutral', 'El Nino'] as const).map(phase => ({
    phase, total: actual.filter(d => d.ensoPhase === phase).reduce((s, d) => s + d.typhoons, 0),
  })), [actual]);

  const correlations = useMemo(() => {
    if (!actual.length) return [];
    const typ = actual.map(d => d.typhoons);
    return CORR_KEYS
      .map(key => ({
        feature: FEATURE_BY_KEY[key].label,
        r: Math.round(pearson(actual.map(d => d[key] as number), typ) * 100) / 100,
      }))
      .sort((a, b) => a.r - b.r);
  }, [actual]);

  if (!data.length || !kpis) return <div className="loading">Loading…</div>;

  return (
    <>
      <div className="page-header">
        <div className="page-title">Typhoon dashboard</div>
        <div className="page-sub">How often typhoons hit the Philippines, and what goes with them.</div>
      </div>

      <Disclaimer dataThrough={model?.dataThrough} />

      <div className="kpi-grid">
        <KPICard value={kpis.total} label="Typhoons on record" hint={`Across ${kpis.years} years`} />
        <KPICard value={kpis.avg} label="Typical year" hint="Average per year" variant="blue" />
        <KPICard value={kpis.pred} label="Next 12 months" hint="Model estimate" variant="amber" />
        <KPICard value={kpis.worst.year} label="Busiest year" hint={`${kpis.worst.total} typhoons`} variant="red" />
      </div>

      <div className="section-label">What the data shows</div>
      <Insights items={insights} />

      <div className="chart-card">
        <div className="chart-head">
          <div className="chart-title">Typhoons per year</div>
          <div className="chart-note">Amber = model forecast · dashed line = long-term trend</div>
        </div>
        <ResponsiveContainer width="100%" height={250}>
          <ComposedChart data={annual}>
            <CartesianGrid stroke={CHART.grid} strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="year" tick={{ fill: CHART.tick, fontSize: 11 }} />
            <YAxis tick={{ fill: CHART.tick, fontSize: 11 }} width={28} />
            <Tooltip {...CHART.tooltip} />
            <Bar dataKey="actual" fill={CHART.accent} radius={[3, 3, 0, 0]} name="Recorded" stackId="a" />
            <Bar dataKey="forecast" fill={CHART.forecast} radius={[3, 3, 0, 0]} name="Forecast" stackId="a" />
            <Line dataKey="trend" stroke={CHART.neutral} strokeDasharray="5 4" strokeWidth={1.5} dot={false} name="Trend" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-2">
        <div className="chart-card" style={{ marginBottom: 0 }}>
          <div className="chart-head">
            <div className="chart-title">Typical typhoons by month</div>
          </div>
          <ResponsiveContainer width="100%" height={210}>
            <BarChart data={monthly}>
              <CartesianGrid stroke={CHART.grid} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="month" tick={{ fill: CHART.tick, fontSize: 10 }} interval={0} />
              <YAxis tick={{ fill: CHART.tick, fontSize: 10 }} width={28} />
              <Tooltip {...CHART.tooltip} />
              <Bar dataKey="avg" fill={CHART.blue} radius={[3, 3, 0, 0]} name="Avg / year" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card" style={{ marginBottom: 0 }}>
          <div className="chart-head">
            <div className="chart-title">Typhoons by ocean pattern</div>
            <InfoDot title="El Niño / La Niña">
              A Pacific Ocean cycle. La Niña usually brings more typhoons to the
              Philippines; El Niño usually calms them.
            </InfoDot>
          </div>
          <ResponsiveContainer width="100%" height={210}>
            <PieChart>
              <Pie data={enso} dataKey="total" nameKey="phase" innerRadius={48} outerRadius={78} paddingAngle={2}>
                {enso.map(e => (
                  <Cell key={e.phase} fill={ENSO_FILL[e.phase]} stroke="#141b26" strokeWidth={2} />
                ))}
              </Pie>
              <Tooltip {...CHART.tooltip} />
              <Legend wrapperStyle={{ fontSize: '0.8rem' }} iconSize={9} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="chart-card">
        <div className="chart-head">
          <div className="chart-title">What goes with more (or fewer) typhoons</div>
          <div className="chart-note">Right = more typhoons · Left = fewer</div>
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={correlations} layout="vertical" margin={{ left: 8 }}>
            <CartesianGrid stroke={CHART.grid} strokeDasharray="3 3" horizontal={false} />
            <XAxis type="number" domain={[-0.7, 0.7]} tick={{ fill: CHART.tick, fontSize: 10 }} />
            <YAxis type="category" dataKey="feature" tick={{ fill: CHART.tick, fontSize: 11 }} width={130} />
            <Tooltip {...CHART.tooltip} />
            <Bar dataKey="r" name="Link strength" radius={2}>
              {correlations.map((c, i) => (
                <Cell key={i} fill={c.r < 0 ? CHART.negative : CHART.positive} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}
