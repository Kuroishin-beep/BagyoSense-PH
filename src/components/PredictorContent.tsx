'use client';

import { useEffect, useState, useMemo } from 'react';
import { ModelData } from '@/lib/types';
import { loadModel, predict } from '@/lib/predict';
import { MONTH_FULL } from '@/lib/data';

const SLIDERS = [
  { key: 'month',     label: 'Month',           min: 1,     max: 12,     step: 1,    init: 8    },
  { key: 'oni',       label: 'ONI Index',        min: -2.5,  max: 2.5,    step: 0.05, init: 0    },
  { key: 'nino34',    label: 'Nino 3.4 SST',     min: -2.5,  max: 2.5,    step: 0.05, init: 0    },
  { key: 'wPacSST',   label: 'W. Pacific SST',   min: -1.5,  max: 1.5,    step: 0.05, init: 0    },
  { key: 'windShear', label: 'Wind Shear',       min: 5,     max: 16,     step: 0.1,  init: 8    },
  { key: 'humidity',  label: 'Humidity %',       min: 45,    max: 80,     step: 0.5,  init: 68   },
  { key: 'slp',       label: 'Sea Level Pressure', min: 1002, max: 1013,  step: 0.1,  init: 1005 },
  { key: 'mjoPhase',  label: 'MJO Phase',        min: 0,     max: 8,      step: 1,    init: 4    },
  { key: 'prevMonth', label: 'Prev Month Count', min: 0,     max: 8,      step: 1,    init: 1    },
] as const;

export default function PredictorContent() {
  const [model, setModel] = useState<ModelData | null>(null);
  const [values, setValues] = useState<Record<string, number>>(
    Object.fromEntries(SLIDERS.map(s => [s.key, s.init]))
  );

  useEffect(() => { loadModel().then(setModel); }, []);

  const features = useMemo(() => {
    return SLIDERS.map(s => values[s.key]);
  }, [values]);

  const prediction = useMemo(() => {
    if (!model) return null;
    return predict(model, features);
  }, [model, features]);

  const ensoLabel = values.oni >= 0.5 ? 'El Nino' : values.oni <= -0.5 ? 'La Nina' : 'Neutral';
  const risk = prediction !== null
    ? prediction >= 4 ? 'alert' : prediction >= 2 ? 'warn' : ''
    : '';
  const riskLabel = prediction !== null
    ? prediction >= 4 ? 'High risk' : prediction >= 2 ? 'Moderate' : 'Low activity'
    : '';

  const handleChange = (key: string, val: number) => {
    setValues(prev => ({ ...prev, [key]: val }));
  };

  if (!model) return <div className="loading">Loading model...</div>;

  return (
    <>
      <div className="page-header">
        <div className="page-title">Predictor</div>
        <div className="page-sub">Interactive typhoon forecast</div>
      </div>

      {/* Model metrics */}
      <div className="section-label">Trained model performance</div>
      <div className="metrics-grid">
        {Object.entries(model.metrics).map(([name, m]) => (
          <div key={name} className={`model-card ${name === model.bestModel ? 'best' : ''}`}>
            <div className="model-name">
              {name === model.bestModel ? `${name} (best)` : name}
            </div>
            <div>
              {m.testR2 != null && <span className="chip">R2 {m.testR2.toFixed(3)}</span>}
              {m.rmse != null && <span className="chip">RMSE {m.rmse.toFixed(2)}</span>}
              {m.mae != null && <span className="chip">MAE {m.mae.toFixed(2)}</span>}
            </div>
          </div>
        ))}
      </div>

      <hr className="section-divider" />

      {/* Sliders */}
      <div className="section-label">Input parameters</div>
      <div className="slider-grid">
        {SLIDERS.map(s => (
          <div key={s.key} className="slider-group">
            <label>
              {s.label}
              <span>{values[s.key]}</span>
            </label>
            <input
              type="range"
              min={s.min}
              max={s.max}
              step={s.step}
              value={values[s.key]}
              onChange={e => handleChange(s.key, parseFloat(e.target.value))}
            />
          </div>
        ))}
      </div>

      {/* Prediction */}
      <div className={`prediction-box ${risk}`}>
        <div>
          <div className="prediction-value">{prediction}</div>
          <div className="prediction-label">Typhoons expected</div>
        </div>
        <div>
          <div className="prediction-context">
            {MONTH_FULL[values.month - 1]} &middot; {ensoLabel} &middot; {riskLabel}
          </div>
          <div style={{ marginTop: '0.4rem' }}>
            <span className="chip">Linear Regression</span>
          </div>
        </div>
      </div>
    </>
  );
}
