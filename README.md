# Smart Estate AI — Production PropTech ML Web Application

> A high-performance, full-stack PropTech research platform evaluating residential property price prediction across 250,000 Indian housing listings.

---

## 🏛️ System Architecture

Smart Estate AI features a decoupled production-style architecture with an interactive React frontend, a high-throughput Python FastAPI backend, and the original Streamlit application preserved as a fallback.

```text
Smart Estate AI Architecture
├── frontend/                     # React 19 + TypeScript + Vite + Tailwind CSS + Recharts
│   ├── src/
│   │   ├── components/Navbar.tsx # Top navigation with live backend health monitor
│   │   ├── pages/
│   │   │   ├── OverviewPage.tsx              # Research KPIs, lifecycle, validation chart
│   │   │   ├── PropertyExplorerPage.tsx      # Multi-filter search, server-side pagination, CSV export
│   │   │   ├── ModelPerformanceLabPage.tsx   # Model benchmarks vs naive baseline
│   │   │   ├── ExplainabilityStudioPage.tsx  # In-sample MDI vs test permutation importance
│   │   │   ├── PredictionStudioPage.tsx      # 16-feature input form, live inference, INR conversion
│   │   │   └── MethodologyPage.tsx           # Dataset audit, leakage prevention, limitations
│   │   ├── api.ts                # Strongly-typed API client and interfaces
│   │   └── App.tsx               # Application shell and tab router
│   ├── package.json
│   └── vite.config.ts            # Development server with /api proxy to FastAPI
│
├── backend/                      # Python FastAPI + Uvicorn Inference & Analytics Engine
│   └── main.py                   # REST API endpoints (health, overview, query, predict, export)
│
├── models/
│   └── best_model.joblib         # Fitted scikit-learn Random Forest pipeline (4.06 MB)
│
├── data/
│   ├── split_indices.npz         # 70/15/15 train/val/test partition row indices
│   ├── preprocessor_tree.joblib  # Fitted tree preprocessor
│   └── preprocessor_linear.joblib# Fitted linear preprocessor
│
├── bengaluru_house_prices.csv    # Source housing dataset (13,320 rows)
├── requirements.txt              # Backend & ML dependencies
├── Dockerfile                    # Multi-stage production container
├── render.yaml                   # Render Cloud Blueprint
└── .gitignore                    # Environment, cache, and build ignore rules
```

---

## 🚀 Getting Started on macOS

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.14 arm64)
- Node.js 18+ and npm (Tested on Node.js v26.8.2 / npm 11.19.1)

---

### 2. Terminal 1: Launch FastAPI Backend

Open a terminal window and navigate to the project root:

```bash
cd "/Users/harsh/Desktop/Smart Estate AI"

# Install backend dependencies (if not already installed)
python3 -m pip install -r requirements.txt fastapi uvicorn

# Start the FastAPI server on port 8000
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- **API Base URL:** `http://127.0.0.1:8000`
- **Swagger Documentation:** `http://127.0.0.1:8000/docs`
- **Health Check Endpoint:** `http://127.0.0.1:8000/api/health`

---

### 3. Terminal 2: Launch React Frontend

Open a second terminal window:

```bash
cd "/Users/harsh/Desktop/Smart Estate AI/frontend"

# Install Node dependencies (if first time)
npm install

# Start Vite development server on port 5173
npm run dev -- --host 127.0.0.1 --port 5173
```

- **Frontend Application URL:** `http://127.0.0.1:5173`
- *The Vite development server automatically proxies all `/api/*` network requests to `http://127.0.0.1:8000`.*

---

## ☁️ Cloud Deployment (Render)

Smart Estate AI is production-ready for deployment on [Render](https://render.com/) Free Tier:

- **1-Click Blueprint:** Connect your GitHub repo to Render Blueprints using the included [`render.yaml`](render.yaml).
- **Manual Web Service:** Set build command to `./build.sh` and start command to `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`.
- **Docker Container:** Multi-stage [`Dockerfile`](Dockerfile) is provided for turnkey container deployments.

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for detailed step-by-step instructions.

---

## 🧪 Scientific Findings & Model Verification

### A. Candidate Model Validation Benchmark (40,000 rows)
| Model | Val MAE (₹ Lakhs) | Val RMSE (₹ Lakhs) | Val $R^2$ Score | Val MAE (INR) | Training Time |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Random Forest (Winner)** | **₹ 122.27L** | **₹ 141.15L** | **-0.0007** | **₹ 1,22,27,390** | 17.04s |
| **Linear Regression** | ₹ 122.28L | ₹ 141.13L | -0.0004 | ₹ 1,22,28,193 | 1.09s |
| **XGBoost Regressor** | ₹ 122.39L | ₹ 141.37L | -0.0038 | ₹ 1,22,38,735 | 1.28s |

### B. Winner Evaluation vs. Baseline on Held-Out Test Set (50,000 rows)
- **Mean Absolute Error (MAE):** ₹ 122.37 Lakhs (₹ 1,22,37,418)
- **Root Mean Squared Error (RMSE):** ₹ 141.26 Lakhs (₹ 1,41,26,455)
- **$R^2$ Score:** -0.0010
- **Naive Mean Baseline:** Guessing the training set mean (₹ 254.55 Lakhs) achieves ₹ 122.32L MAE. The Random Forest model slightly deteriorates by **+0.046% (+₹ 5,640)** due to random split noise.
- **Inference Speed:** 0.1944s for 50,000 rows (257,214 rows/sec).

---

## ⚠️ Academic Disclaimer

> **EDUCATIONAL DEMONSTRATION ONLY —**
> Empirical data audits established that target prices in this dataset were algorithmically generated independently of property attributes (|r| ≤ 0.004). With an average valuation error exceeding **₹ 1.22 Crore per home**, this model **must NEVER be deployed for commercial real estate appraisals, mortgage underwriting, lending, or taxation**.
