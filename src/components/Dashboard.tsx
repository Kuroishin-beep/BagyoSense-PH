'use client';

import { useEffect, useState, useMemo } from 'react';
import {
  BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Line, ComposedChart,
} from 'recharts';
import { DataRow } from '@/lib/types';
import { loadData, pearson, CHART, ENSO_FILL, MONTH_LABELS } from '@/lib/data';
import KPICard from './KPICard';

export default function Dashboard() {
  const [data, setData] = useState<DataRow[]>([]);
  useEffect(() => { loadData().then(setData); }, []);

  const actual = useMemo(() => data.filter(d => !d.predicted), [data]);
  const predicted = useMemo(() => data.filter(d => d.predicted), [data]);

  const kpis = useMemo(() => {
    if (!actual.length) return null;
    const total = actual.reduce((s, d) => s + d.typhoons, 0);
    const years = [...new Set(actual.map(d => d.year))];
    const avg = (total / years.length).toFixed(1);

    const monthTotals = Array.from({ length: 12 }, (_, i) => {
      const vals = actual.filter(d => d.month === i + 1);
      return vals.reduce((s, d) => s + d.typhoons, 0) / Math.max(vals.length, 1);
    });
    const peakIdx = monthTotals.indexOf(Math.max(...monthTotals));
    const peakMonth = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][peakIdx];

    const yearTotals = years.map(y => ({
      year: y,
      total: actual.filter(d => d.year === y).reduce((s, d) => s + d.typhoons, 0),
    }));
    const worst = yearTotals.reduce((a, b) => b.total > a.total ? b : a);

    const pred2026 = predicted.reduce((s, d) => s + d.typhoons, 0);

    return { total, avg, peakMonth, worstYear: worst.year, pred2026 };
  }, [actual, predicted]);

  const annual = useMemo(() => {
    const allData = data;
    const years = [...new Set(allData.map(d => d.year))].sort();
    const points = years.map(y => {
      const yearData = allData.filter(d => d.year === y);
      const isPredicted = yearData.some(d => d.predicted);
      return {
        year: y.toString(),
        actual: isPredicted ? 0 : yearData.reduce((s, d) => s + d.typhoons, 0),
        forecast: isPredicted ? yearData.reduce((s, d) => s + d.typhoons, 0) : 0,
      };
    });
    // Trend line on actual data only
    const actualYears = years.filter(y => !data.some(d => d.year === y && d.predicted));
    if (actualYears.length > 1) {
      const ys = actualYears.map(y => data.filter(d => d.year === y && !d.predicted).reduce((s, d) => s + d.typhoons, 0));
      const n = actualYears.length;
      const mx = actualYears.reduce((a, b) => a + b, 0) / n;
      const my = ys.reduce((a, b) => a + b, 0) / n;
      let num = 0, den = 0;
      for (let i = 0; i < n; i++) { num += (actualYears[i] - mx) * (ys[i] - my); den += (actualYears[i] - mx) ** 2; }
      const slope = den ? num / den : 0;
      const intercept = my - slope * mx;
      points.forEach(p => {
        const yr = parseInt(p.year);
        (p as any).trend = Math.round((slope * yr + intercept) * 10) / 10;
      });
    }
    return points;
  }, [data]);

  const monthly = useMemo(() => {
    return MONTH_LABELS.map((label, i) => {
      const vals = actual.filter(d => d.month === i + 1);
      const avg = vals.length ? vals.reduce((s, d) => s + d.typhoons, 0) / vals.length : 0;
      return { month: label, avg: Math.round(avg * 100) / 100 };
    });
  }, [actual]);

  const enso = useMemo(() => {
    return ['El Nino', 'La Nina', 'Neutral'].map(phase => ({
      phase,
      total: actual.filter(d => d.ensoPhase === phase).reduce((s, d) => s + d.typhoons, 0),
    }));
  }, [actual]);

  const correlations = useMemo(() => {
    if (!actual.length) return [];
    const typhoons = actual.map(d => d.typhoons);
    const features: { key: keyof DataRow; label: string }[] = [
      { key: 'oni', label: 'ONI' },
      { key: 'nino34', label: 'Nino 3.4' },
      { key: 'wPacSST', label: 'W. Pacific SST' },
      { key: 'windShear', label: 'Wind Shear' },
      { key: 'humidity', label: 'Humidity' },
      { key: 'slp', label: 'Sea Level Pressure' },
      { key: 'prevMonth', label: 'Prev Month' },
    ];
    return features
      .map(f => ({
        feature: f.label,
        r: Math.round(pearson(actual.map(d => d[f.key] as number), typhoons) * 1000) / 1000,
      }))
      .sort((a, b) => a.r - b.r);
  }, [actual]);

  if (!data.length) return <div className="loading">Loading...</div>;

  return (
    <>
      <div className="page-header">
        <div className="page-title">Dashboard</div>
        <div className="page-sub">Typhoon intelligence 2014-2025 + 2026 forecast</div>
      </div>

      <div className="kpi-grid">
        <KPICard value={kpis!.total} label="Total Typhoons (actual)" />
        <KPICard value={kpis!.avg} label="Avg Per Year" />
        <KPICard value={kpis!.pred2026} label="2026 Forecast" variant="amber" />
        <KPICard value={kpis!.worstYear} label="Most Active Year" variant="red" />
      </div>

      {/* Annual Trend */}
      <div className="chart-card" style={{ marginBottom: '0.75rem' }}>
        <div className="chart-title">Annual typhoon count (2026 = forecast)</div>
        <ResponsiveContainer width="100%" height={240}>
          <ComposedChart data={annual}>
            <CartesianGrid stroke={CHART.grid} strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="year" tick={{ fill: CHART.tick, fontSize: 11 }} />
            <YAxis tick={{ fill: CHART.tick, fontSize: 11 }} />
            <Tooltip {...CHART.tooltip} />
            <Bar dataKey="actual" fill={CHART.primary} radius={[3, 3, 0, 0]} name="Actual" stackId="a" />
            <Bar dataKey="forecast" fill={CHART.amber} radius={[3, 3, 0, 0]} name="2026 Forecast" stackId="a" opacity={0.7} />
            <Line dataKey="trend" stroke="#64748b" strokeDasharray="4 4" strokeWidth={1.5} dot={false} name="Trend" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-2">
        {/* Monthly Average */}
        <div className="chart-card">
          <div className="chart-title">Avg typhoons by month (2014-2025)</div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={monthly}>
              <CartesianGrid stroke={CHART.grid} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="month" tick={{ fill: CHART.tick, fontSize: 10 }} />
              <YAxis tick={{ fill: CHART.tick, fontSize: 10 }} />
              <Tooltip {...CHART.tooltip} />
              <Bar dataKey="avg" fill={CHART.blue} radius={[2, 2, 0, 0]} name="Avg" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* ENSO Donut */}
        <div className="chart-card">
          <div className="chart-title">Distribution by ENSO phase</div>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={enso}
                dataKey="total"
                nameKey="phase"
                innerRadius={45}
                outerRadius={75}
                paddingAngle={2}
              >
                {enso.map((e) => (
                  <Cell key={e.phase} fill={ENSO_FILL[e.phase] || CHART.primary} stroke="#111827" strokeWidth={2} />
                ))}
              </Pie>
              <Tooltip {...CHART.tooltip} />
              <Legend
                wrapperStyle={{ fontSize: '0.7rem', fontFamily: 'IBM Plex Mono' }}
                iconSize={8}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Correlations */}
      <div className="chart-card">
        <div className="chart-title">Climate correlations with typhoon count</div>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={correlations} layout="vertical">
            <CartesianGrid stroke={CHART.grid} strokeDasharray="3 3" horizontal={false} />
            <XAxis type="number" domain={[-0.7, 0.7]} tick={{ fill: CHART.tick, fontSize: 10 }} />
            <YAxis type="category" dataKey="feature" tick={{ fill: CHART.tick, fontSize: 10 }} width={110} />
            <Tooltip {...CHART.tooltip} />
            <Bar dataKey="r" name="Correlation">
              {correlations.map((c, i) => (
                <Cell key={i} fill={c.r < 0 ? CHART.red : CHART.primary} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}
