# 🛡️ KSP Crime Intelligence Platform

An end-to-end criminal intelligence & analytics platform built for the **Karnataka State Police (KSP)**. The platform features a high-fidelity intelligence dashboard, bilingual Kannada/English support, automated intent routing, incident heatmaps, suspect dossier management, and a hybrid RAG (Retrieval-Augmented Generation) query engine.

---

## 🌟 Key Features & Architecture

* **Bilingual Intelligence Console**: Instant script translation toggle between Kannada (ಕನ್ನಡ) and English.
* **Brutalist Command Dashboard**: 3-column operational layout featuring:
  * **Live Investigation Stream**: Dynamic query chat with cited FIR source documents.
  * **Matrix Telemetry**: Active entity counting, linkage identification, and critical anomaly indicators.
  * **Live Incident Feed**: Real-time ticker stream of recent crime reports.
* **Specialized Analytics Modules**:
  * **Spatial Mapping (Heatmap)**: Incident hotspot clustering with dispatch simulation.
  * **Node/Entity Graph (Network)**: Visualizing suspect connections and co-accused linkages.
  * **Forecasting Model (Predict)**: Predictive risk scoring and timeline estimations.
  * **Case File Directory (FIR)** & **Suspect Dossiers**: Master repositories with dossier drawer modals.
* **Resilient Dual-Mode RAG Engine**:
  * **Mode A (High Performance / Offline-Ready)**: Uses fast in-memory keyword matching over `track1_dataset.json` for zero-cold-start startup (<1s) with zero external database requirements.
  * **Mode B (Vector Store Mode)**: Supports PostgreSQL + `pgvector` with LaBSE multi-lingual embedding models (`sentence-transformers/LaBSE`).

---

## 📁 Repository Structure

```text
ksp/
├── frontend/             # Next.js 16 (App Router), React 19, Tailwind CSS v4, Leaflet Maps
│   ├── app/
│   │   ├── components/   # Reusable map & UI components (HeatmapMap.tsx, etc.)
│   │   ├── dashboard/    # Main Operations Console (/dashboard)
│   │   ├── login/        # Auth gate (/login)
│   │   ├── globals.css   # Custom Tailwind theme tokens & wireframe animations
│   │   └── layout.tsx    # Root HTML shell
│   └── package.json
├── query/                # RAG & Intelligence Gateway Service
│   ├── api.py            # Main FastAPI gateway (/api/query, /api/telemetry, /api/feed, etc.)
│   ├── app.py            # Standalone API runner with full route alias support
│   ├── generate.py       # RAG report generation pipeline with fallback logic
│   ├── intent_router.py  # Intent classifier (LOOKUP, PATTERN, PREDICT, NETWORK)
│   ├── llm_gateway.py    # Unified multi-vendor LLM client (Catalyst, Groq, OpenAI)
│   ├── retrieve.py       # Hybrid vector/dataset retrieval engine
│   └── translate.py      # Cross-lingual translation helpers
├── backend/              # Core Relational API & Database Schemas
│   ├── app/              # FastAPI routers for FIRs, Criminals, Officers & Auth
│   └── geocoded_stations.json # Station spatial coordinate mappings
├── track1_dataset.json   # Denormalized FIR dataset for instant offline operation
├── requirements.txt      # Python backend & ML dependencies
└── README.md             # Developer onboarding & documentation
```

---

## 🚀 Getting Started

### Prerequisites

* **Node.js**: v18.x or v20.x
* **npm**: v9.x or newer
* **Python**: v3.10, v3.11, or v3.12
* **Git**

---

### Step 1: Clone & Setup Workspace

```bash
git clone <repository-url>
cd ksp
```

---

### Step 2: Set Up Python Backend Environment

1. **Create and activate a virtual environment (recommended):**

   * **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   * **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

### Step 3: Set Up Frontend Environment

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node dependencies:**
   ```bash
   npm install
   ```

3. **Return to the project root:**
   ```bash
   cd ..
   ```

---

## 💻 Running the Application Locally

To run the complete platform locally, open **two separate terminal windows**:

### Terminal 1: Start the Intelligence Gateway (Backend API)

From the project root directory (`ksp/`):

```bash
python query/api.py
```
* **Endpoint URL**: `http://127.0.0.1:8000`
* **Health Check**: `http://127.0.0.1:8000/health`

---

### Terminal 2: Start the Next.js Frontend

From the `frontend/` directory (`ksp/frontend`):

```bash
npm run dev
```
* **Frontend App**: `http://localhost:3000`
* **Direct Dashboard Link**: `http://localhost:3000/dashboard`

---

## ⚙️ Environment Configuration (.env)

The application is pre-configured with zero-config defaults for instant local development. For production deployments or custom API keys, configure environment variables:

### Query Gateway (`query/.env` or root `.env`)
```env
# Server Port & Database settings
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=ksp_db
DB_USER=postgres
DB_PASSWORD=postgres

# Toggle Vector Store Mode (0 = Fast dataset fallback, 1 = pgvector mode)
ENABLE_VECTOR_STORE=0

# Active LLM Provider (catalyst, groq, openai, or anthropic)
LLM_PROVIDER=catalyst
CATALYST_API_KEY=your_catalyst_key
# GROQ_API_KEY=your_groq_key
```

### Frontend (`frontend/.env.local`)
```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
NEXT_PUBLIC_QUERY_API_BASE_URL=http://127.0.0.1:8000
```

---

## 🧪 Testing & Diagnostics

Run validation scripts from the project root:

* **Validate Intent Router Accuracy**:
  ```bash
  python test_router_accuracy.py
  ```
* **Run Multilingual Batch Test**:
  ```bash
  python multilingual_test.py
  ```
* **Test Dataset ETL Generation**:
  ```bash
  python etl_to_json.py
  ```

---

## 🛠️ Troubleshooting

* **`ERR_CONNECTION_REFUSED` in Dashboard**:
  Ensure `python query/api.py` is running on port `8000` before accessing `http://localhost:3000/dashboard`.
* **Slow startup / 1.88GB model download**:
  Keep `ENABLE_VECTOR_STORE=0` (default). This uses the instant in-memory dataset search engine which boots in under 1 second without downloading large model weights.
