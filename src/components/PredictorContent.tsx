'use client';

import { useEffect, useState, useMemo } from 'react';
import { ModelData } from '@/lib/types';
import { loadModel, predict } from '@/lib/predict';
import { MONTH_FULL } from '@/lib/data';
import { FEATURES, formatFeature, ensoFromOni, ENSO_INFO } from '@/lib/features';
import InfoDot from './InfoDot';
import Disclaimer from './Disclaimer';

type Values = Record<string, number>;

const DEFAULTS: Values = Object.fromEntries(FEATURES.map(f => [f.key, f.init]));

/** Representative climate settings for one-tap scenarios (peak season, August). */
const PRESETS: { label: string; icon: string; values: Values }[] = [
  { label: 'La Niña (stormy)', icon: '🌊', values: {
      month: 8, oni: -1.2, nino34: -1.2, wPacSST: 0.5, windShear: 7.5,
      humidity: 71, slp: 1004.5, mjoPhase: 5, prevMonth: 3 } },
  { label: 'Neutral', icon: '⚖️', values: {
      month: 8, oni: 0, nino34: 0, wPacSST: 0.1, windShear: 9,
      humidity: 66, slp: 1006, mjoPhase: 4, prevMonth: 2 } },
  { label: 'El Niño (calm)', icon: '☀️', values: {
      month: 8, oni: 1.2, nino34: 1.2, wPacSST: -0.2, windShear: 11,
      humidity: 60, slp: 1008, mjoPhase: 3, prevMonth: 1 } },
];

export default function PredictorContent() {
  const [model, setModel] = useState<ModelData | null>(null);
  const [values, setValues] = useState<Values>(DEFAULTS);
  useEffect(() => { loadModel().then(setModel); }, []);

  const features = useMemo(() => FEATURES.map(f => values[f.key]), [values]);
  const prediction = useMemo(() => (model ? predict(model, features) : null), [model, features]);

  const enso = ensoFromOni(values.oni);
  const risk = prediction === null ? '' : prediction >= 4 ? 'alert' : prediction >= 2 ? 'warn' : 'low';
  const riskLabel = prediction === null ? '' : prediction >= 4 ? 'High activity' : prediction >= 2 ? 'Moderate activity' : 'Quiet';

  const predictorName = model?.predictorModel ?? 'Linear model';
  const predRmse = model?.metrics?.[predictorName]?.rmse ?? null;

  const set = (key: string, val: number) => setValues(prev => ({ ...prev, [key]: val }));

  if (!model) return <div className="loading">Loading model…</div>;

  return (
    <>
      <div className="page-header">
        <div className="page-title">Try the predictor</div>
        <div className="page-sub">Move the sliders to a weather scenario and see how many typhoons the model expects that month.</div>
      </div>

      <Disclaimer dataThrough={model.dataThrough} />

      {/* One-tap scenarios */}
      <div className="section-label">Start from a scenario</div>
      <div className="preset-row">
        {PRESETS.map(p => (
          <button key={p.label} className="preset-btn" onClick={() => setValues({ ...DEFAULTS, ...p.values })}>
            {p.icon} {p.label}
          </button>
        ))}
        <button className="preset-btn reset" onClick={() => setValues(DEFAULTS)}>↺ Reset</button>
      </div>

      {/* Sliders */}
      <div className="section-label">Adjust the conditions</div>
      <div className="slider-grid">
        {FEATURES.map(f => (
          <div key={f.key} className="slider-group">
            <div className="slider-top">
              <span className="slider-name">
                {f.label}
                <InfoDot title={f.technical}>{f.what} {f.meaning}</InfoDot>
              </span>
              <span className="slider-val">
                {f.key === 'month' ? MONTH_FULL[values.month - 1] : formatFeature(f.key, values[f.key])}
              </span>
            </div>
            <input
              type="range" min={f.min} max={f.max} step={f.step}
              value={values[f.key]}
              onChange={e => set(f.key, parseFloat(e.target.value))}
            />
            <span className="slider-hint">{f.meaning}</span>
          </div>
        ))}
      </div>

      {/* Result */}
      <div className={`prediction-box ${risk}`}>
        <div className="prediction-main">
          <div className="prediction-value">{prediction}</div>
          <div className="prediction-label">typhoons expected</div>
        </div>
        <div className="prediction-read">
          <div className="prediction-headline">
            In {MONTH_FULL[values.month - 1]}, under {ENSO_INFO[enso].title} conditions
          </div>
          <div className="prediction-context">
            The model expects about <b>{prediction}</b> typhoon{prediction === 1 ? '' : 's'}
            {predRmse ? <> — give or take roughly {predRmse.toFixed(1)}</> : null}.
            {' '}{ENSO_INFO[enso].blurb}
          </div>
          <span className={`risk-pill ${risk}`}>{riskLabel}</span>
        </div>
      </div>

      <hr className="section-divider" />

      {/* Honest accuracy */}
      <div className="section-label">
        How accurate is this?
        <InfoDot title="Read this first">
          Scores are cross-validated on months the model never trained on, then
          checked on the most recent {model.holdoutMonths ?? 18} months.
        </InfoDot>
      </div>
      <div className="callout">
        Monthly typhoon counts are genuinely hard to predict. These models land
        <b> within about ±1 typhoon</b> of the real count, and only edge out a plain
        {model.baseline ? <> &ldquo;{model.baseline.name.toLowerCase()}&rdquo;</> : ' seasonal average'} baseline.
        Use this to explore how conditions relate to storms — not as a real forecast.
      </div>

      <div className="metrics-grid">
        {Object.entries(model.metrics).map(([name, m]) => (
          <div key={name} className={`model-card ${name === model.bestModel ? 'best' : ''}`}>
            <div className="model-name">
              {name}
              {name === model.bestModel && <span className="best-tag">best</span>}
              {name === model.predictorModel && name !== model.bestModel && <span className="best-tag">used here</span>}
            </div>
            {m.rmse != null && (
              <div className="metric-row"><span>Typical miss</span><span>±{m.rmse.toFixed(1)}</span></div>
            )}
            {m.cvR2 != null && (
              <div className="metric-row"><span>Skill (↑ better)</span><span>{m.cvR2.toFixed(2)}</span></div>
            )}
          </div>
        ))}
        {model.baseline && (
          <div className="model-card">
            <div className="model-name">{model.baseline.name}<span className="chip" style={{ marginLeft: 'auto' }}>baseline</span></div>
            <div className="metric-row"><span>Typical miss</span><span>±{model.baseline.rmse.toFixed(1)}</span></div>
            <div className="metric-row"><span>What it is</span><span>no ML</span></div>
          </div>
        )}
      </div>
    </>
  );
}
