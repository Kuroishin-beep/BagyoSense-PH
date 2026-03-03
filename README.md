# 🌀 BagyoSense

> **Professional typhoon intelligence platform for the Philippines**  
> AI-powered analytics · Machine learning predictions · 10-year climate data (2014–2024)

*Bagyo (Filipino) — typhoon*

---

## Overview

BagyoSense is a Streamlit-based data science application that combines climate analytics, machine learning, and LLM-powered insights to analyze typhoon patterns in the Philippines. It uses 132 monthly observations spanning 2014–2024, incorporating ENSO indices, sea surface temperatures, wind shear, humidity, and MJO phase data.

---

## Features

| Module | Description |
|---|---|
| 📊 **Dashboard** | KPI cards, annual trends, ENSO breakdown, heatmaps, correlation charts |
| 🔬 **Analysis** | Rolling averages, cumulative curves, scatter matrices, climate driver analysis |
| 🤖 **ML Predictor** | Random Forest, Gradient Boosting, Linear Regression with interactive sliders |
| 💬 **AI Analyst** | Claude-powered Q&A and auto-report generation using dataset as context |

---

## Project Structure

```
typhoon-app/
├── typhoon_app.py                            # Main Streamlit application
├── philippines_typhoon_monthly_2014_2024.csv # Dataset
└── README.md                                 # This file
```

---

## Dataset

**File:** `philippines_typhoon_monthly_2014_2024.csv`  
**Records:** 132 monthly rows (Jan 2014 – Dec 2024)

| Column | Description |
|---|---|
| `Year` | Year (2014–2024) |
| `Month` | Month (1–12) |
| `Number_of_Typhoons` | Target variable — typhoons that month |
| `ONI` | Oceanic Niño Index (ENSO signal) |
| `Nino3.4_SST_anomaly` | Niño 3.4 sea surface temperature anomaly |
| `Western_Pacific_SST` | Western Pacific SST anomaly |
| `Vertical_Wind_Shear` | Wind shear (suppresses typhoon formation) |
| `Midlevel_Humidity` | Mid-level atmospheric humidity (%) |
| `SeaLevelPressure` | Sea level pressure (hPa) |
| `MJO_Phase` | Madden-Julian Oscillation phase (0–8) |
| `Prev_month_typhoons` | Lagged typhoon count (previous month) |

---

## Requirements

- Python 3.8+
- Anthropic API key ([get one here](https://console.anthropic.com))

### Python packages

```
streamlit
plotly
scikit-learn
anthropic
pandas
numpy
```

---

## Installation & Setup

### 1. Clone or download the project

```bash
mkdir typhoon-app && cd typhoon-app
# Place typhoon_app.py and the CSV here
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Activate — Windows:
venv\Scripts\activate

# Activate — Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install streamlit plotly scikit-learn anthropic pandas numpy
```

### 4. Set your Anthropic API key

**Windows:**
```bash
set ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Mac/Linux:**
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 5. Run the app

```bash
streamlit run typhoon_app.py
```

Open your browser at **http://localhost:8501**

---

## Machine Learning Models

BagyoSense trains three regression models on every app load (cached for performance):

| Model | Notes |
|---|---|
| **Random Forest** | 200 estimators, max depth 8 — best for non-linear patterns |
| **Gradient Boosting** | 200 estimators, max depth 4 — strong on feature interactions |
| **Linear Regression** | Baseline model with StandardScaler normalization |

**Features used for prediction:**
Month, ONI, Niño 3.4 SST anomaly, Western Pacific SST, Vertical Wind Shear, Midlevel Humidity, Sea Level Pressure, MJO Phase, Previous month typhoons

The interactive predictor averages all three models into an **ensemble forecast**.

---

## AI Analyst

The AI Analyst tab is powered by **Claude Sonnet** (Anthropic). It is given a structured data context including:
- Annual and monthly typhoon summaries
- ENSO phase averages
- Feature correlations
- Key climate patterns

You can ask free-form questions or use preset prompts, and generate a full auto-written analytical report.

---

## Key Findings (from the data)

- **Peak season** is June–November, accounting for ~85% of annual typhoons
- **La Niña** years correlate with higher typhoon frequency; El Niño years suppress activity
- **Vertical wind shear** has the strongest negative correlation with typhoon count
- **July–October** are the most active months on average
- The **MJO phase** and **previous month count** are strong short-term predictors

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Run `pip install <module>` inside the active venv |
| AI tab returns API error | Check that `ANTHROPIC_API_KEY` is set correctly |
| CSV not found | Ensure the CSV is in the same folder as `typhoon_app.py` |
| Port in use | Run `streamlit run typhoon_app.py --server.port 8502` |
| Slow model training | Normal on first load — results are cached after that |

---

## License

MIT License — free to use, modify, and distribute.

---

*Built with Streamlit · Plotly · scikit-learn · Claude AI*
