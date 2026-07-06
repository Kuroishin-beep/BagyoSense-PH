'use client';

import { useEffect, useState, useMemo } from 'react';
import {
  LineChart, Line, BarChart, Bar, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import { DataRow } from '@/lib/types';
import { loadData, CHART, ENSO_FILL, MONTH_LABELS, YEAR_COLORS } from '@/lib/data';

export default function AnalysisContent() {
  const [raw, setRaw] = useState<DataRow[]>([]);
  useEffect(() => { loadData().then(setRaw); }, []);
  const data = useMemo(() => raw.filter(d => !d.predicted), [raw]);

  // Rolling averages
  const rolling = useMemo(() => {
    if (!data.length) return [];
    const sorted = [...data].sort((a, b) => a.year * 12 + a.month - (b.year * 12 + b.month));
    return sorted.map((d, i) => {
      const s3 = Math.max(0, i - 2);
      const s12 = Math.max(0, i - 11);
      const slice3 = sorted.slice(s3, i + 1);
      const slice12 = sorted.slice(s12, i + 1);
      return {
        date: `${d.year}-${String(d.month).padStart(2, '0')}`,
        raw: d.typhoons,
        ma3: Math.round(slice3.reduce((s, r) => s + r.typhoons, 0) / slice3.length * 100) / 100,
        ma12: Math.round(slice12.reduce((s, r) => s + r.typhoons, 0) / slice12.length * 100) / 100,
      };
    });
  }, [data]);

  // Cumulative by year
  const cumulative = useMemo(() => {
    if (!data.length) return { years: [] as number[], chartData: [] as any[] };
    const years = [...new Set(data.map(d => d.year))].sort();
    const chartData = Array.from({ length: 12 }, (_, i) => {
      const point: any = { month: MONTH_LABELS[i] };
      years.forEach(y => {
        const yearRows = data.filter(d => d.year === y).sort((a, b) => a.month - b.month);
        let cum = 0;
        yearRows.forEach(r => { if (r.month <= i + 1) cum += r.typhoons; });
        point[`y${y}`] = cum;
      });
      return point;
    });
    return { years, chartData };
  }, [data]);

  // ENSO monthly pattern
  const ensoMonthly = useMemo(() => {
    if (!data.length) return [];
    return Array.from({ length: 12 }, (_, i) => {
      const month = i + 1;
      const point: any = { month: MONTH_LABELS[i] };
      ['El Nino', 'La Nina', 'Neutral'].forEach(phase => {
        const vals = data.filter(d => d.month === month && d.ensoPhase === phase);
        point[phase] = vals.length
          ? Math.round(vals.reduce((s, d) => s + d.typhoons, 0) / vals.length * 100) / 100
          : 0;
      });
      return point;
    });
  }, [data]);

  // Year-over-year change
  const yoy = useMemo(() => {
    const years = [...new Set(data.map(d => d.year))].sort();
    const totals = years.map(y => data.filter(d => d.year === y).reduce((s, d) => s + d.typhoons, 0));
    return years.slice(1).map((y, i) => ({
      year: y.toString(),
      change: totals[i + 1] - totals[i],
    }));
  }, [data]);

  if (!data.length) return <div className="loading">Loading...</div>;

  return (
    <>
      <div className="page-header">
        <div className="page-title">Analysis</div>
        <div className="page-sub">Trends, patterns, and climate drivers</div>
      </div>

      {/* Rolling Averages */}
      <div className="chart-card" style={{ marginBottom: '0.75rem' }}>
        <div className="chart-title">Rolling averages</div>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={rolling}>
            <CartesianGrid stroke={CHART.grid} strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fill: CHART.tick, fontSize: 9 }} interval={11} />
            <YAxis tick={{ fill: CHART.tick, fontSize: 10 }} />
            <Tooltip {...CHART.tooltip} />
            <Legend wrapperStyle={{ fontSize: '0.7rem' }} iconSize={8} />
            <Line dataKey="ma3" stroke={CHART.primary} strokeWidth={2} dot={false} name="3-month" />
            <Line dataKey="ma12" stroke={CHART.amber} strokeWidth={2} strokeDasharray="4 4" dot={false} name="12-month" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Cumulative */}
      <div className="chart-card" style={{ marginBottom: '0.75rem' }}>
        <div className="chart-title">Cumulative typhoons by year</div>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={cumulative.chartData}>
            <CartesianGrid stroke={CHART.grid} strokeDasharray="3 3" />
            <XAxis dataKey="month" tick={{ fill: CHART.tick, fontSize: 10 }} />
            <YAxis tick={{ fill: CHART.tick, fontSize: 10 }} />
            <Tooltip {...CHART.tooltip} />
            <Legend wrapperStyle={{ fontSize: '0.65rem' }} iconSize={6} />
            {cumulative.years.map((y, i) => (
              <Line
                key={y}
                dataKey={`y${y}`}
                stroke={YEAR_COLORS[i % YEAR_COLORS.length]}
                strokeWidth={1.5}
                dot={false}
                name={y.toString()}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-2">
        {/* ENSO Monthly Pattern */}
        <div className="chart-card">
          <div className="chart-title">Monthly pattern by ENSO phase</div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={ensoMonthly}>
              <CartesianGrid stroke={CHART.grid} strokeDasharray="3 3" />
              <XAxis dataKey="month" tick={{ fill: CHART.tick, fontSize: 10 }} />
              <YAxis tick={{ fill: CHART.tick, fontSize: 10 }} />
              <Tooltip {...CHART.tooltip} />
              <Legend wrapperStyle={{ fontSize: '0.7rem' }} iconSize={8} />
              {['La Nina', 'Neutral', 'El Nino'].map(phase => (
                <Line
                  key={phase}
                  dataKey={phase}
                  stroke={ENSO_FILL[phase]}
                  strokeWidth={2}
                  dot={{ r: 2 }}
                  name={phase}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Year-over-year */}
        <div className="chart-card">
          <div className="chart-title">Year-over-year change</div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={yoy}>
              <CartesianGrid stroke={CHART.grid} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="year" tick={{ fill: CHART.tick, fontSize: 10 }} />
              <YAxis tick={{ fill: CHART.tick, fontSize: 10 }} />
              <Tooltip {...CHART.tooltip} />
              <Bar dataKey="change" name="Change" radius={[2, 2, 0, 0]}>
                {yoy.map((d, i) => (
                  <Cell key={i} fill={d.change >= 0 ? CHART.primary : CHART.red} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </>
  );
}
