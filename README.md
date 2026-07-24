# BagyoSense

> Philippine typhoon patterns, explained simply.
> An educational dashboard: climate analytics + a small machine-learning model, in plain language.

*Bagyo (Filipino) — typhoon*

> ⚠️ **Educational demo.** BagyoSense runs on *illustrative* climate data so you
> can explore how typhoon seasons behave and how a forecasting model is built and
> judged. It is **not** an official PAGASA or NOAA product and must not be used for
> planning or safety decisions.

---

## What it does

BagyoSense is a Next.js dashboard that turns monthly typhoon data into something a
non-expert can read. Every technical term (ONI, wind shear, MJO…) is given a plain
label and a one-line explanation on hover, and the headline patterns are written out
as short, human sentences.

| Page | What you get |
|---|---|
| **Dashboard** | Key numbers, auto-generated plain-language **insights**, typhoons-per-year with trend & forecast, seasonal averages, ocean-pattern breakdown, and "what goes with more/fewer typhoons". |
| **Analysis** | Smoothed trends (3- & 12-month averages), season build-up by year (recent years highlighted, older ones muted), season shape by El Niño/La Niña, and year-over-year change. |
| **Predictor** | One-tap climate scenarios, friendly sliders with explanations, a readable result ("about 2 typhoons, give or take ~1"), and an **honest** accuracy panel comparing models to a no-ML baseline. |

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, React |
| Charts | Recharts |
| Styling | Vanilla CSS, calm dark theme (CVD-checked palette) |
| In-browser prediction | Exported linear-model coefficients (no backend) |
| Training | Python · scikit-learn (`train_model.py`) |
| Deployment | Vercel |

All charts and the interactive predictor run **client-side** — there is no server or
API. The Python script is only needed if you want to retrain and regenerate the JSON.

---

## Project structure

```
BagyoSense-PH/
├── public/
│   ├── data.json          # History + 12-month model forecast (generated)
│   └── model.json         # Linear coefficients + honest metrics (generated)
├── src/
│   ├── app/               # Routes + global styles
│   ├── components/        # Dashboard, Analysis, Predictor, Insights, InfoDot…
│   └── lib/
│       ├── types.ts       # Shared types
│       ├── data.ts        # Data loading, palette, aggregation helpers
│       ├── features.ts    # Plain-language dictionary for the 9 climate inputs
│       ├── insights.ts    # Auto-generated plain-language findings
│       └── predict.ts     # Client-side linear inference
├── dataset/               # Monthly CSVs (illustrative)
├── models/                # Fitted estimators (local convenience, git-ignored ok)
├── train_model.py         # Single honest train → evaluate → export pipeline
└── package.json
```

---

## Getting started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Production build:

```bash
npm run build && npm start
```

---

## Retraining (optional)

The app ships with `public/data.json` and `public/model.json` already generated.
To rebuild them from the dataset:

```bash
pip install pandas numpy scikit-learn joblib
python train_model.py
```

`train_model.py` does everything in one honest pass:

1. Loads the most complete dataset CSV and sorts it by time.
2. Reserves the most recent 18 months as an untouched hold-out.
3. Selects models with **TimeSeriesSplit** cross-validation (no peeking at the future).
4. Reports metrics on the hold-out — never on the rows it trained on.
5. Compares every model against a plain **seasonal-average baseline**.
6. Produces a 12-month forecast under a stated climate scenario (clearly flagged).
7. Exports `public/data.json` and `public/model.json`.

### Honest model performance

Small monthly counts are genuinely hard to predict, and the metrics say so.
Cross-validated skill is low; the linear models' edge over the seasonal baseline is
real but modest. (Numbers below are from the shipped `model.json`.)

| Model | CV skill (R²) | Hold-out R² | Typical miss (RMSE) | MAE |
|---|---|---|---|---|
| Random Forest *(best CV)* | 0.16 | 0.46 | ±1.2 | 0.83 |
| Ridge *(used in predictor)* | 0.13 | 0.65 | ±0.9 | 0.67 |
| Linear Regression | 0.10 | 0.65 | ±0.9 | 0.67 |
| Gradient Boosting | −0.09 | 0.39 | ±1.2 | 0.89 |
| *Seasonal average (baseline)* | — | 0.43 | ±1.2 | 0.89 |

The interactive predictor uses the best-performing **linear** model, because its
coefficients can run directly in the browser.

---

## Patterns in this dataset

The in-app Insights panel derives these automatically; they describe *this* dataset,
not the real world:

- Roughly **82%** of typhoons fall in the June–November peak season.
- **October** is the busiest month on average.
- **Wind shear** has the strongest link to typhoon counts (more shear → fewer storms).
- El Niño / La Niña shifts the season, matching the known El Niño calming effect.
- The long-term trend is weak and easily swamped by year-to-year swings.

---

## License

MIT License — free to use, modify, and distribute.
