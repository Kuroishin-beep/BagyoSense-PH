# BagyoSense

> Philippines typhoon intelligence platform
> Machine learning predictions · Climate analytics · 10-year data (2014–2024)

*Bagyo (Filipino) — typhoon*

---

## Overview

BagyoSense is a Next.js dashboard that combines climate analytics and machine learning to analyze typhoon patterns in the Philippines. It uses 132 monthly observations spanning 2014–2024, incorporating ENSO indices, sea surface temperatures, wind shear, humidity, and MJO phase data.

Built with TypeScript and deployed on Vercel. All computation runs client-side — no backend required.

---

## Features

| Module | Description |
|---|---|
| **Dashboard** | KPI cards, annual trend with trendline, ENSO breakdown, monthly averages, climate correlations |
| **Analysis** | Rolling averages (3M/12M), cumulative curves by year, ENSO monthly patterns, year-over-year change |
| **Predictor** | Interactive sliders for 9 climate parameters, real-time typhoon forecast using exported ML model |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, React |
| Charts | Recharts |
| Styling | Vanilla CSS (dark theme) |
| ML Inference | Client-side (exported Linear Regression coefficients) |
| Training | Python, scikit-learn, XGBoost (local only) |
| Deployment | Vercel |

---

## Project Structure

```
BagyoSense-PH/
├── public/
│   ├── data.json                     # Dataset (exported from CSV)
│   └── model.json                    # Model coefficients + metrics
├── src/
│   ├── app/
│   │   ├── layout.tsx                # Root layout + sidebar
│   │   ├── page.tsx                  # Dashboard
│   │   ├── globals.css               # Dark theme
│   │   ├── analysis/page.tsx         # Analysis
│   │   └── predictor/page.tsx        # Predictor
│   ├── components/
│   │   ├── Sidebar.tsx               # Navigation
│   │   ├── KPICard.tsx               # Metric card
│   │   ├── Dashboard.tsx             # Dashboard charts
│   │   ├── AnalysisContent.tsx       # Analysis charts
│   │   └── PredictorContent.tsx      # Sliders + prediction
│   └── lib/
│       ├── types.ts                  # TypeScript types
│       ├── data.ts                   # Data loading + helpers
│       └── predict.ts                # Client-side inference
├── scripts/
│   └── export_data.py                # CSV + model → JSON export
├── dataset/
│   └── philippines_typhoon_monthly_2014_2024.csv
├── models/                           # Trained models (local only)
├── train_model.py                    # Model training script
├── package.json
├── tsconfig.json
└── next.config.mjs
```

---

## Dataset

**File:** `dataset/philippines_typhoon_monthly_2014_2024.csv`
**Records:** 132 monthly rows (Jan 2014 – Dec 2024)

| Column | Description |
|---|---|
| `Year` | Year (2014–2024) |
| `Month` | Month (1–12) |
| `Number_of_Typhoons` | Target variable |
| `ONI` | Oceanic Nino Index |
| `Nino3.4_SST_anomaly` | Nino 3.4 sea surface temperature anomaly |
| `Western_Pacific_SST` | Western Pacific SST anomaly |
| `Vertical_Wind_Shear` | Wind shear |
| `Midlevel_Humidity` | Mid-level atmospheric humidity (%) |
| `SeaLevelPressure` | Sea level pressure (hPa) |
| `MJO_Phase` | Madden-Julian Oscillation phase (0–8) |
| `Prev_month_typhoons` | Lagged typhoon count |

---

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.8+ (only for model training)

### Install and Run

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Production Build

```bash
npm run build
npm start
```

---

## ML Training (Optional)

The trained models are already exported to `public/model.json`. To retrain:

```bash
# Install Python dependencies
pip install pandas numpy scikit-learn xgboost joblib

# Train models with 5-fold cross-validation
python train_model.py

# Export to JSON for the frontend
python scripts/export_data.py
```

### Trained Models

| Model | CV R² | Test R² | RMSE | MAE |
|---|---|---|---|---|
| **XGBoost** | 0.2252 | 0.4280 | 1.2910 | 0.9259 |
| Random Forest | 0.1605 | 0.2500 | 1.4782 | 1.0741 |
| Gradient Boosting | 0.1229 | 0.1483 | 1.5753 | 1.1481 |
| Linear Regression | 0.1757 | 0.3008 | 1.4272 | 1.0000 |

XGBoost is the best-performing model. Linear Regression coefficients are exported for client-side interactive prediction.

---

## Deployment

### Vercel

1. Push to GitHub
2. Import the repository on [vercel.com](https://vercel.com)
3. Vercel auto-detects Next.js — deploy with defaults

No environment variables or build configuration needed.

---

## Key Findings

- Peak season is June–November, accounting for ~85% of annual typhoons
- La Nina years correlate with higher typhoon frequency; El Nino suppresses activity
- Vertical wind shear has the strongest negative correlation with typhoon count
- July–October are the most active months on average
- Previous month count is the strongest short-term positive predictor

---

## License

MIT License — free to use, modify, and distribute.
