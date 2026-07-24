'use client';

import { useEffect, useState, useMemo } from 'react';
import {
  LineChart, Line, BarChart, Bar, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import { DataRow } from '@/lib/types';
import {
  loadData, CHART, ENSO_FILL, MONTH_LABELS, RECENT_YEAR_COLORS, MUTED_YEAR,
} from '@/lib/data';
import InfoDot from './InfoDot';

export default function AnalysisContent() {
  const [raw, setRaw] = useState<DataRow[]>([]);
  useEffect(() => { loadData().then(setRaw); }, []);
  const data = useMemo(() => raw.filter(d => !d.predicted), [raw]);

  const sorted = useMemo(
    () => [...data].sort((a, b) => (a.year * 12 + a.month) - (b.year * 12 + b.month)),
    [data]);

  // Rolling averages (3-month & 12-month) over the ordered series
  const rolling = useMemo(() => sorted.map((d, i) => {
    const slice3 = sorted.slice(Math.max(0, i - 2), i + 1);
    const slice12 = sorted.slice(Math.max(0, i - 11), i + 1);
    const mean = (arr: DataRow[]) =>
      Math.round(arr.reduce((s, r) => s + r.typhoons, 0) / arr.length * 100) / 100;
    return {
      date: `${d.year}-${String(d.month).padStart(2, '0')}`,
      ma3: mean(slice3),
      ma12: mean(slice12),
    };
  }), [sorted]);

  const years = useMemo(() => [...new Set(data.map(d => d.year))].sort((a, b) => a - b), [data]);

  // Cumulative count through the year, one line per year
  const cumulative = useMemo(() => {
    const byYear = new Map<number, number[]>();
    for (const y of years) byYear.set(y, new Array(12).fill(0));
    for (const d of sorted) byYear.get(d.year)![d.month - 1] += d.typhoons;
    return MONTH_LABELS.map((month, i) => {
      const point: Record<string, number | string> = { month };
      for (const y of years) {
        const arr = byYear.get(y)!;
        point[`y${y}`] = arr.slice(0, i + 1).reduce((s, v) => s + v, 0);
      }
      return point;
    });
  }, [sorted, years]);

  // Colour recent years; older years recede into muted gray
  const yearColor = (y: number) => {
    const idxFromEnd = years.length - 1 - years.indexOf(y);
    return idxFromEnd < RECENT_YEAR_COLORS.length ? RECENT_YEAR_COLORS[idxFromEnd] : MUTED_YEAR;
  };
  const isRecent = (y: number) => (years.length - 1 - years.indexOf(y)) < RECENT_YEAR_COLORS.length;

  const ensoMonthly = useMemo(() => MONTH_LABELS.map((month, i) => {
    const point: Record<string, number | string> = { month };
    (['La Nina', 'Neutral', 'El Nino'] as const).forEach(phase => {
      const vals = sorted.filter(d => d.month === i + 1 && d.ensoPhase === phase);
      point[phase] = vals.length
        ? Math.round(vals.reduce((s, d) => s + d.typhoons, 0) / vals.length * 100) / 100 : 0;
    });
    return point;
  }), [sorted]);

  const yoy = useMemo(() => {
    const totals = years.map(y => data.filter(d => d.year === y).reduce((s, d) => s + d.typhoons, 0));
    return years.slice(1).map((y, i) => ({ year: y.toString(), change: totals[i + 1] - totals[i] }));
  }, [years, data]);

  if (!data.length) return <div className="loading">Loading…</div>;

  return (
    <>
      <div className="page-header">
        <div className="page-title">Deeper analysis</div>
        <div className="page-sub">Trends over time, seasonal build-up, and how ocean patterns shift the season.</div>
      </div>

      <div className="callout">
        These charts smooth out the month-to-month noise so longer patterns stand out.
        Typhoon counts bounce around a lot, so short streaks rarely mean much on their own.
      </div>

      <div className="chart-card">
        <div className="chart-head">
          <div className="chart-title">Smoothed trend</div>
          <InfoDot title="Rolling averages">
            Each point averages the recent months. The 3-month line follows the
            season; the 12-month line shows the slow, year-round drift.
          </InfoDot>
        </div>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={rolling}>
            <CartesianGrid stroke={CHART.grid} strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="date" tick={{ fill: CHART.tick, fontSize: 9 }} interval={11} />
            <YAxis tick={{ fill: CHART.tick, fontSize: 10 }} width={28} />
            <Tooltip {...CHART.tooltip} />
            <Legend wrapperStyle={{ fontSize: '0.8rem' }} iconSize={9} />
            <Line dataKey="ma3" stroke={CHART.accent} strokeWidth={2} dot={false} name="3-month average" />
            <Line dataKey="ma12" stroke={CHART.forecast} strokeWidth={2} strokeDasharray="5 4" dot={false} name="12-month average" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-card">
        <div className="chart-head">
          <div className="chart-title">Season build-up by year</div>
          <div className="chart-note">Recent years highlighted · earlier years in gray</div>
        </div>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={cumulative}>
            <CartesianGrid stroke={CHART.grid} strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="month" tick={{ fill: CHART.tick, fontSize: 10 }} interval={0} />
            <YAxis tick={{ fill: CHART.tick, fontSize: 10 }} width={28} />
            <Tooltip {...CHART.tooltip} />
            <Legend wrapperStyle={{ fontSize: '0.78rem' }} iconSize={9} />
            {years.map(y => (
              <Line
                key={y}
                dataKey={`y${y}`}
                stroke={yearColor(y)}
                strokeWidth={isRecent(y) ? 2.2 : 1}
                strokeOpacity={isRecent(y) ? 1 : 0.5}
                dot={false}
                name={y.toString()}
                legendType={isRecent(y) ? 'line' : 'none'}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-2">
        <div className="chart-card" style={{ marginBottom: 0 }}>
          <div className="chart-head">
            <div className="chart-title">Season shape by ocean pattern</div>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={ensoMonthly}>
              <CartesianGrid stroke={CHART.grid} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="month" tick={{ fill: CHART.tick, fontSize: 10 }} interval={0} />
              <YAxis tick={{ fill: CHART.tick, fontSize: 10 }} width={28} />
              <Tooltip {...CHART.tooltip} />
              <Legend wrapperStyle={{ fontSize: '0.8rem' }} iconSize={9} />
              {(['La Nina', 'Neutral', 'El Nino'] as const).map(phase => (
                <Line key={phase} dataKey={phase} stroke={ENSO_FILL[phase]} strokeWidth={2} dot={{ r: 2 }} name={phase.replace('Nino', 'Niño').replace('Nina', 'Niña')} />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card" style={{ marginBottom: 0 }}>
          <div className="chart-head">
            <div className="chart-title">Change from the year before</div>
            <div className="chart-note">Green = busier · Red = calmer</div>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={yoy}>
              <CartesianGrid stroke={CHART.grid} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="year" tick={{ fill: CHART.tick, fontSize: 10 }} />
              <YAxis tick={{ fill: CHART.tick, fontSize: 10 }} width={28} />
              <Tooltip {...CHART.tooltip} />
              <Bar dataKey="change" name="Change vs prior year" radius={2}>
                {yoy.map((d, i) => (
                  <Cell key={i} fill={d.change >= 0 ? CHART.positive : CHART.negative} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </>
  );
}
