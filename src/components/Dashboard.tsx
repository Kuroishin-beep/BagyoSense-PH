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

  const kpis = useMemo(() => {
    if (!data.length) return null;
    const total = data.reduce((s, d) => s + d.typhoons, 0);
    const years = [...new Set(data.map(d => d.year))];
    const avg = (total / years.length).toFixed(1);

    const monthTotals = Array.from({ length: 12 }, (_, i) => {
      const vals = data.filter(d => d.month === i + 1);
      return vals.reduce((s, d) => s + d.typhoons, 0) / Math.max(vals.length, 1);
    });
    const peakIdx = monthTotals.indexOf(Math.max(...monthTotals));
    const peakMonth = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][peakIdx];

    const yearTotals = years.map(y => ({
      year: y,
      total: data.filter(d => d.year === y).reduce((s, d) => s + d.typhoons, 0),
    }));
    const worst = yearTotals.reduce((a, b) => b.total > a.total ? b : a);

    return { total, avg, peakMonth, worstYear: worst.year };
  }, [data]);

  const annual = useMemo(() => {
    const years = [...new Set(data.map(d => d.year))].sort();
    const points = years.map(y => ({
      year: y.toString(),
      total: data.filter(d => d.year === y).reduce((s, d) => s + d.typhoons, 0),
    }));
    if (points.length > 1) {
      const xs = years;
      const ys = points.map(p => p.total);
      const n = xs.length;
      const mx = xs.reduce((a, b) => a + b, 0) / n;
      const my = ys.reduce((a, b) => a + b, 0) / n;
      let num = 0, den = 0;
      for (let i = 0; i < n; i++) { num += (xs[i] - mx) * (ys[i] - my); den += (xs[i] - mx) ** 2; }
      const slope = den ? num / den : 0;
      const intercept = my - slope * mx;
      points.forEach((p, i) => { (p as any).trend = Math.round((slope * xs[i] + intercept) * 10) / 10; });
    }
    return points;
  }, [data]);

  const monthly = useMemo(() => {
    return MONTH_LABELS.map((label, i) => {
      const vals = data.filter(d => d.month === i + 1);
      const avg = vals.length ? vals.reduce((s, d) => s + d.typhoons, 0) / vals.length : 0;
      return { month: label, avg: Math.round(avg * 100) / 100 };
    });
  }, [data]);

  const enso = useMemo(() => {
    return ['El Nino', 'La Nina', 'Neutral'].map(phase => ({
      phase,
      total: data.filter(d => d.ensoPhase === phase).reduce((s, d) => s + d.typhoons, 0),
    }));
  }, [data]);

  const correlations = useMemo(() => {
    if (!data.length) return [];
    const typhoons = data.map(d => d.typhoons);
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
        r: Math.round(pearson(data.map(d => d[f.key] as number), typhoons) * 1000) / 1000,
      }))
      .sort((a, b) => a.r - b.r);
  }, [data]);

  if (!data.length) return <div className="loading">Loading...</div>;

  return (
    <>
      <div className="page-header">
        <div className="page-title">Dashboard</div>
        <div className="page-sub">Typhoon intelligence overview</div>
      </div>

      <div className="kpi-grid">
        <KPICard value={kpis!.total} label="Total Typhoons" />
        <KPICard value={kpis!.avg} label="Avg Per Year" />
        <KPICard value={kpis!.peakMonth} label="Peak Month" variant="amber" />
        <KPICard value={kpis!.worstYear} label="Most Active Year" variant="red" />
      </div>

      {/* Annual Trend */}
      <div className="chart-card" style={{ marginBottom: '0.75rem' }}>
        <div className="chart-title">Annual typhoon count</div>
        <ResponsiveContainer width="100%" height={240}>
          <ComposedChart data={annual}>
            <CartesianGrid stroke={CHART.grid} strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="year" tick={{ fill: CHART.tick, fontSize: 11 }} />
            <YAxis tick={{ fill: CHART.tick, fontSize: 11 }} />
            <Tooltip {...CHART.tooltip} />
            <Bar dataKey="total" fill={CHART.primary} radius={[3, 3, 0, 0]} name="Typhoons" />
            <Line dataKey="trend" stroke={CHART.amber} strokeDasharray="4 4" strokeWidth={2} dot={false} name="Trend" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-2">
        {/* Monthly Average */}
        <div className="chart-card">
          <div className="chart-title">Avg typhoons by month</div>
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
