# SupplyChain - Enterprise Planning System

An AI-powered supply chain optimization platform that uses LangGraph with multi-LLM support (OpenAI GPT-4o-mini or Google Gemini) to forecast demand, optimize inventory, manage supplier relationships, and plan logistics—with human-in-the-loop approval.

---

## 🎯 Quick Start (2 Minutes)

### Windows Users (Easiest)
```powershell
start_server.bat
```
Then in **another terminal**:
```powershell
python -m http.server 8001 --directory .
```
Open: http://localhost:8001/index.html

### macOS/Linux Users
**Terminal 1:**
```bash
source myenv/bin/activate
python server.py
```

**Terminal 2:**
```bash
python -m http.server 8001 --directory .
```
Open: http://localhost:8001/index.html

---

## 📋 Full Setup Instructions

### Prerequisites
- Python 3.9 or higher
- **API Key** (choose one):
  - OpenAI API key (recommended for production) - https://platform.openai.com/
  - OR Google Gemini API key (free tier) - https://ai.google.dev/

### Step 1: Create Virtual Environment
```bash
python -m venv myenv
```

### Step 2: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
myenv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```bash
myenv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source myenv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
Create `.env` file in project root with your API credentials:

**Option A: Using OpenAI (Currently Active)**
```bash
OPENAI_API_KEY=your_openai_key_here
```
Get your key: https://platform.openai.com/api-keys

**Option B: Using Google Gemini**
```bash
GOOGLE_API_KEY=your_gemini_key_here
```
Get your key: https://ai.google.dev/

To switch between LLMs, edit `src/agents/demand_forecasting.py` and uncomment/comment the appropriate LLM initialization.

---

## 🚀 Running the System

### Two Servers Required

This system has **two separate servers**:

| Server | Port | Purpose |
|--------|------|---------|
| **Backend API** | 8000 | FastAPI server (LLM + orchestration) |
| **Frontend UI** | 8001 | Static HTML/JS dashboard |

### Option 1: Automated (Windows Only)
```bash
start_server.bat
```
Then in another terminal:
```bash
python -m http.server 8001 --directory .
```

### Option 2: Manual Start (Windows PowerShell)

**Terminal 1 - Backend API:**
```powershell
myenv\Scripts\Activate.ps1
python server.py
```

**Terminal 2 - Frontend UI:**
```powershell
python -m http.server 8001 --directory .
```

### Option 3: Manual Start (macOS/Linux)

**Terminal 1 - Backend API:**
```bash
source myenv/bin/activate
python server.py
```

**Terminal 2 - Frontend UI:**
```bash
python -m http.server 8001 --directory .
```

### Verify Both Servers Are Running

✅ **Backend running**: http://localhost:8000/health (should show `{"status": "ok"}`)
✅ **Frontend running**: http://localhost:8001/index.html (should load dashboard)

---

## 🌐 Access the Application

Once both servers are running:

| URL | Purpose |
|-----|---------|
| **http://localhost:8001/index.html** | Main dashboard |
| **http://localhost:8000** | API base URL |
| **http://localhost:8000/docs** | API Swagger UI |
| **http://localhost:8000/redoc** | API ReDoc documentation |

---

## 📊 Using the Dashboard

### Workflow Steps

1. **Click "▶ Run Pipeline"** - Starts the supply chain planning
2. **Review Phase Results** - See forecasts, inventory, suppliers, logistics
3. **Make Decision** - Click "✓ Approve" or "✗ Reject"
4. **View Final Results** - See optimization metrics and recommendations

### Dashboard Tabs

- **Alerts** - Critical issues and warnings
- **Forecasts** - Demand predictions by location
- **Inventory** - Stock levels and reorder points
- **Suppliers** - Procurement plan and alternatives
- **Logistics** - Warehouse capacity and shipments
- **Metrics** - Performance evaluation (after approval)

---

## 🧪 Running Tests

### All Tests (5 Scenarios, 22 Tests)
```bash
python -m pytest tests/test_enterprise_scenarios.py -v
```

### Specific Scenario

**Scenario 1: Q2 Planning**
```bash
python -m pytest tests/test_enterprise_scenarios.py::TestScenario1_Q2Planning -v
```

**Scenario 2: Supplier Crisis**
```bash
python -m pytest tests/test_enterprise_scenarios.py::TestScenario2_SupplierCrisis -v
```

**Scenario 3: ERP System Down**
```bash
python -m pytest tests/test_enterprise_scenarios.py::TestScenario3_ERPSystemDown -v
```

**Scenario 4: Budget Overrun**
```bash
python -m pytest tests/test_enterprise_scenarios.py::TestScenario4_BudgetOverrun -v
```

**Scenario 5: Black Friday**
```bash
python -m pytest tests/test_enterprise_scenarios.py::TestScenario5_BlackFridayPlanning -v
```

### Coverage Report
```bash
python -m pytest tests/test_enterprise_scenarios.py --cov=src --cov-report=html
```

---

## 🔧 Command-Line Execution (No Browser)

For batch processing without the web UI:

```bash
python run_pipeline.py
```

This will:
- Load and profile data
- Generate demand forecasts
- Optimize inventory allocation
- Plan supplier procurement
- Calculate logistics requirements
- Prompt for human approval
- Generate evaluation report
- Export `final_inventory_plan.xlsx`

---

## 📁 Project Structure

```
src/
  ├── state.py                      # Central state definition (ForecastState)
  ├── graph.py                      # LangGraph workflow orchestration
  ├── agents/                       # 6 core agents
  │   ├── data_loader.py           # Load Excel data
  │   ├── data_profiling.py        # Sort, clean, normalize
  │   ├── feature_engineering.py   # Create time-series features
  │   ├── demand_forecasting.py    # OpenAI GPT-4o-mini or Gemini forecasting
  │   ├── inventory_optimization_v2.py  # Safety stock, ROP, budget
  │   ├── supplier_procurement.py  # Outage detection, alternatives
  │   ├── logistics_capacity.py    # Warehouse planning
  │   ├── human_review.py          # Approval gate
  │   └── evaluation.py            # Metrics calculation
  └── tools/                        # Supporting utilities
      ├── forecast_cache.py        # Fallback forecasting
      ├── supplier_database.py     # 5 supplier configurations
      └── capacity_simulator.py    # 4 warehouse models

server.py                           # FastAPI server (13 endpoints)
index.html                          # Web dashboard (vanilla JS)
tests/
  └── test_enterprise_scenarios.py # 22 comprehensive tests
```

---

## 🏗️ System Architecture

### 7-Node Workflow

```
Data Pipeline (3 agents)
    ↓
Demand Forecasting (LLM-powered)
    ↓
Inventory Optimization (Safety stock calc)
    ↓
Supplier Procurement (Outage detection)
    ↓
Logistics & Capacity (Warehouse planning)
    ↓
Human Review (Approval gate)
    ↓
Evaluation (Metrics calculation)
```

### Key Features

- **LLM Integration**: OpenAI GPT-4o-mini (currently active) or Google Gemini 2.5 Flash (switch in demand_forecasting.py)
- **Fallback Mechanism**: Graceful degradation when API fails (uses statistical forecasting)
- **Budget Constraints**: Inventory plan respects $100K budget limit
- **Supplier Outage Handling**: Automatic sourcing from alternative suppliers
- **Black Friday Planning**: Special surge capacity detection and planning
- **Human-in-Loop**: Approval gate for critical decisions
- **Real-time Polling**: Frontend polls every 3 seconds for status updates

---

## ⚙️ API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/pipeline/run` | POST | Start pipeline execution |
| `/api/pipeline/status` | GET | Get current status |
| `/api/forecasts` | GET | Get demand forecasts |
| `/api/inventory-plan` | GET | Get inventory optimization |
| `/api/supplier-plan` | GET | Get procurement plan |
| `/api/logistics-plan` | GET | Get logistics plan |
| `/api/alerts` | GET | Get system alerts |
| `/api/escalations` | GET | Get escalations |
| `/api/human-review` | POST | Submit approval decision |
| `/api/metrics` | GET | Get evaluation metrics |
| `/api/test-scenarios` | GET | Get test data |

See **API_DOCUMENTATION.md** for complete details and cURL examples.

---

## 🔴 Troubleshooting

### Port Already in Use

**Windows:**
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**macOS/Linux:**
```bash
lsof -i :8000
kill -9 <PID>
```

### Import Errors

```bash
# Verify venv is activated
which python  # Should show path inside myenv/

# Reinstall packages
pip install -r requirements.txt --force-reinstall
```

### API Key Not Working

```bash
# Check .env file exists
cat .env

# Should contain ONE of these:
# Option 1: OpenAI (recommended)
# OPENAI_API_KEY=sk-...

# Option 2: Google Gemini
# GOOGLE_API_KEY=AIzaSy...

# Get OpenAI key from: https://platform.openai.com/api-keys
# Get Gemini key from: https://ai.google.dev/
```

**Common Issues:**
- Empty or missing `.env` file
- Incorrect API key format
- API key has been revoked
- Insufficient API credits/quota

To switch LLMs, edit `src/agents/demand_forecasting.py` and toggle the commented lines.

### Frontend Can't Connect to Backend

1. Verify backend is running: http://localhost:8000/health
2. Check browser console (F12) for CORS errors
3. Ensure backend started BEFORE frontend
4. Try refreshing frontend page (F5)

### Approval Buttons Not Working

1. Open browser DevTools
2. Check Console for JavaScript errors
3. Verify pipeline is in "human_review" status
4. Try refreshing page

---

## 🆘 Need Help?

1. Check **Troubleshooting** section above
2. Review **API_DOCUMENTATION.md** for endpoint details
3. Check browser console (F12) for JavaScript errors
4. Verify both servers are running on correct ports
