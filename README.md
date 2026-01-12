# SupplyChain - Enterprise Planning System

## Setup Instructions

### 1. Create Virtual Environment
```bash
python -m venv myenv
```

### 2. Activate Virtual Environment

**On Windows (PowerShell):**
```bash
myenv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```bash
myenv\Scripts\activate.bat
```

**On macOS/Linux:**
```bash
source myenv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:
```bash
GOOGLE_API_KEY=your_api_key_here
```

Get your API key from: https://ai.google.dev/

## Running Tests

### Run All Test Cases
```bash
python -m pytest tests/test_enterprise_scenarios.py -v
```

### Run Tests with Coverage Report
```bash
python -m pytest tests/test_enterprise_scenarios.py --cov=src --cov-report=html
```

### Run Specific Scenario Tests

**Scenario 1: Q2 Planning with Budget Optimization**
```bash
python -m pytest tests/test_enterprise_scenarios.py::TestScenario1_Q2Planning -v
```

**Scenario 2: Supplier Crisis Management**
```bash
python -m pytest tests/test_enterprise_scenarios.py::TestScenario2_SupplierCrisis -v
```

**Scenario 3: ERP System Down - Graceful Degradation**
```bash
python -m pytest tests/test_enterprise_scenarios.py::TestScenario3_ERPSystemDown -v
```

**Scenario 4: Budget Overrun Detection & Escalation**
```bash
python -m pytest tests/test_enterprise_scenarios.py::TestScenario4_BudgetOverrun -v
```

**Scenario 5: Black Friday Planning**
```bash
python -m pytest tests/test_enterprise_scenarios.py::TestScenario5_BlackFridayPlanning -v
```

## Running the Main Project

### Execute Full Pipeline
```bash
python run_pipeline.py
```

This will:
- Load and profile data
- Extract features
- Run demand forecasting
- Optimize inventory
- Handle supplier procurement
- Plan logistics
- Request human review
- Generate final evaluation report

### Output Files

After running the pipeline, check:
- Console output for alerts and plan summary
- Generated Excel file with the final supply chain plan

## Project Structure

```
src/
  ├── state.py                    # Central state management
  ├── graph.py                    # Workflow orchestration
  ├── agents/                     # Core agent modules
  │   ├── demand_forecasting.py   # Phase 1: Forecasting
  │   ├── inventory_optimization_v2.py  # Phase 2: Inventory
  │   ├── supplier_procurement.py # Phase 3: Suppliers
  │   ├── logistics_capacity.py   # Phase 4: Logistics
  │   ├── human_review.py         # User approval gate
  │   └── ...                     # Support agents
  └── tools/                      # Supporting tools
      ├── forecast_cache.py       # Caching mechanism
      ├── supplier_database.py    # Supplier data
      └── capacity_simulator.py   # Warehouse capacity

tests/
  └── test_enterprise_scenarios.py  # 23 comprehensive tests

requirements.txt                    # Python dependencies
run_pipeline.py                     # Main entry point
```

## Troubleshooting

**Issue: Import errors**
- Ensure virtual environment is activated
- Verify all packages installed: `pip list`

**Issue: API key error**
- Check `.env` file exists in project root
- Verify `GOOGLE_API_KEY` is set correctly

**Issue: Test failures**
- Run `python -m pytest tests/test_enterprise_scenarios.py -v` for details
- Check console output for specific error messages