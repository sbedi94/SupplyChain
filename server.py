from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sys
import os
from datetime import datetime
import traceback
import uvicorn
import numpy as np
import pandas as pd
from pathlib import Path
import zipfile, io
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from graph import create_workflow

app = FastAPI(title="SupplyChain Planning System", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class HumanReviewRequest(BaseModel):
    decision: str

class HumanReviewResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    decision: str

# Initialize workflow
workflow = None
pipeline_state = None  # Store current pipeline state
pipeline_paused = False  # Track if pipeline is waiting for approval

def initialize_workflow():
    global workflow
    if workflow is not None:
        return
    try:
        workflow = create_workflow()
        print("[OK] Workflow initialized successfully")
    except Exception as e:
        print(f"[ERROR] Error initializing workflow: {e}")
        traceback.print_exc()


def make_serializable(obj):
    """Recursively convert numpy/pandas objects to JSON-serializable Python types."""
    from datetime import date, datetime as _dt

    # pandas DataFrame -> convert to records then recurse
    try:
        if isinstance(obj, pd.DataFrame):
            res = obj.to_dict(orient="records")
            return make_serializable(res)
    except Exception:
        pass

    # pandas Series -> convert to dict then recurse
    try:
        if isinstance(obj, pd.Series):
            res = obj.to_dict()
            return make_serializable(res)
    except Exception:
        pass

    # numpy scalar
    try:
        if isinstance(obj, np.generic):
            return obj.item()
    except Exception:
        pass

    # numpy array
    try:
        if isinstance(obj, (np.ndarray,)):
            return obj.tolist()
    except Exception:
        pass

    # datetime / date
    if isinstance(obj, (_dt, date)):
        return obj.isoformat()

    # dict
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}

    # list/tuple
    if isinstance(obj, (list, tuple)):
        return [make_serializable(v) for v in obj]

    # fallthrough
    return obj

@app.on_event("startup")
def startup_event():
    """Initialize workflow when app starts"""
    print("[STARTUP] Initializing workflow...")
    initialize_workflow()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "SupplyChain Planning System"
    }

@app.post("/api/pipeline/run")
async def run_pipeline():
    """Execute the pipeline up to human review approval"""
    global pipeline_state, pipeline_paused
    try:
        if not workflow:
            raise HTTPException(status_code=500, detail="Workflow not initialized")

        # Get initial state
        initial_state = {
            'stores': [],
            'skus': [],
            'forecasts': {},
            'inventory_plan': {},
            'supplier_status': {},
            'procurement_plan': {},
            'logistics_plan': {},
            'shipment_plan': {},
            'alerts': [],
            'escalations': [],
            'human_decision': None,
            'evaluation_metrics': {}
        }

        # Run workflow
        pipeline_state = initial_state
        pipeline_paused = False
        result = workflow.invoke(initial_state)
        pipeline_state = result
        print(result)
        return {
            "status": "success",
            "message": "Pipeline executed successfully - awaiting approval",
            "timestamp": datetime.now().isoformat(),
            "awaiting_approval": True,
            "alerts": result.get('alerts', []),
            "escalations": result.get('escalations', []),
            "summary": {
                "forecasts_generated": len(result.get('forecasts', {})),
                "inventory_items": len(result.get('inventory_plan', {})),
                "procurement_items": len(result.get('procurement_plan', {})),
                "total_alerts": len(result.get('alerts', [])),
                "total_escalations": len(result.get('escalations', []))
            }
        }

    except Exception as e:
        print(f"[ERROR] Error running pipeline: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pipeline/status")
async def pipeline_status():
    """Get pipeline status and configuration"""
    try:
        return {
            "status": "ready",
            "pipeline_steps": [
                "data_loading",
                "data_profiling",
                "feature_engineering",
                "demand_forecasting",
                "inventory_optimization",
                "supplier_procurement",
                "logistics_capacity",
                "human_review",
                "evaluation"
            ],
            "workflow_initialized": workflow is not None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/forecasts")
async def get_forecasts():
    """Get demand forecasts"""
    try:
        return {
            "status": "success",
            "message": "Forecasts retrieved",
            "data": {
                "description": "Run pipeline to generate forecasts",
                "phase": "demand_forecasting"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inventory")
async def get_inventory():
    """Get inventory optimization plan"""
    try:
        return {
            "status": "success",
            "message": "Inventory plan retrieved",
            "data": {
                "description": "Run pipeline to generate inventory plan",
                "phase": "inventory_optimization"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/suppliers")
async def get_suppliers():
    """Get supplier procurement plan"""
    try:
        return {
            "status": "success",
            "message": "Supplier plan retrieved",
            "data": {
                "description": "Run pipeline to generate procurement plan",
                "phase": "supplier_procurement"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logistics")
async def get_logistics():
    """Get logistics and capacity plan"""
    try:
        return {
            "status": "success",
            "message": "Logistics plan retrieved",
            "data": {
                "description": "Run pipeline to generate logistics plan",
                "phase": "logistics_capacity"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alerts")
async def get_alerts():
    """Get all alerts from pipeline execution"""
    try:
        return {
            "status": "success",
            "message": "Alerts retrieved",
            "data": {
                "description": "Run pipeline to generate alerts",
                "alert_types": ["forecast_alerts", "budget_alerts", "supplier_alerts", "capacity_alerts"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/escalations")
async def get_escalations():
    """Get escalations for management review"""
    try:
        return {
            "status": "success",
            "message": "Escalations retrieved",
            "data": {
                "description": "Run pipeline to generate escalations",
                "escalation_types": ["budget_overrun", "supplier_crisis", "capacity_constraint"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/human-review")
async def submit_human_review(request_body: HumanReviewRequest):
    """Submit human review decision and continue pipeline"""
    global pipeline_state, pipeline_paused
    try:
        decision = request_body.decision

        if decision not in ['approve', 'modify', 'reject']:
            raise HTTPException(
                status_code=400,
                detail='Invalid decision. Must be approve, modify, or reject'
            )

        # Update pipeline state with human decision
        if pipeline_state:
            pipeline_state['human_decision'] = decision
            
            # If approved or modified, continue the pipeline to completion
            if decision in ['approve', 'modify']:
                if workflow:
                    try:
                        print(f"[INFO] Continuing pipeline from human review with decision: {decision}")
                        # Continue workflow from current state
                        # This will execute the routing logic and continue to evaluation
                        final_result = workflow.invoke(pipeline_state)
                        pipeline_state = final_result
                        pipeline_paused = False
                        
                        excels_to_be_downloaded = ["final_inventory_plan", "forecasts", "logistics_plan", "supplier_status"]
                        for item in excels_to_be_downloaded:
                            df = final_result.get(item)
                            if isinstance(df, pd.DataFrame) and not df.empty:
                                df.to_excel(f"{item}.xlsx", index=False)
                                print(f"\n✓ {item} exported to '{item}.xlsx'")
                            elif isinstance(df, list) and len(df) > 0:
                                pd.DataFrame(df).to_excel(f"{item}.xlsx", index=False)
                                print(f"\n✓ {item} exported to '{item}.xlsx'")
                        print(f"[INFO] Pipeline completed successfully")
                        print(f"[INFO] Final state keys: {list(final_result.keys())}")
                        
                    except Exception as e:
                        print(f"[ERROR] Error continuing pipeline: {e}")
                        traceback.print_exc()
                        raise HTTPException(status_code=500, detail=f"Error continuing pipeline: {str(e)}")
            else:
                # Reject - don't continue
                pipeline_paused = False

        return {
            "status": "success",
            "message": f"Decision '{decision}' recorded. Pipeline {'completed' if decision in ['approve', 'modify'] else 'rejected'}",
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "pipeline_complete": decision in ['approve', 'modify'],
            "final_state": make_serializable(pipeline_state) if decision in ['approve', 'modify'] and pipeline_state is not None else None
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Error in human review: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/evaluation")
async def get_evaluation():
    """Get evaluation metrics"""
    try:
        return {
            "status": "success",
            "message": "Evaluation metrics retrieved",
            "data": {
                "description": "Run pipeline to generate evaluation metrics",
                "metrics": ["forecast_accuracy", "cost_optimization", "supplier_reliability", "capacity_utilization"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/api/download-report")
async def get_download_report():
    """Get download report"""
    try:
        base_dir = Path(".")
        xlsx_files = list(base_dir.glob("*.xlsx"))

        if not xlsx_files:
            raise HTTPException(404, "No Excel files found")

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for f in xlsx_files:
                zipf.write(f, arcname=f.name)

        zip_buffer.seek(0)

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": "attachment; filename=reports.zip"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scenarios")
async def get_scenarios():
    """Get available test scenarios"""
    try:
        scenarios = [
            {
                "id": "scenario_1",
                "name": "Q2 Planning with Budget Optimization",
                "description": "Basic supply chain planning with budget constraints"
            },
            {
                "id": "scenario_2",
                "name": "Supplier Crisis Management",
                "description": "Handle supplier outages and alternative sourcing"
            },
            {
                "id": "scenario_3",
                "name": "ERP System Down",
                "description": "Graceful degradation with cache fallback"
            },
            {
                "id": "scenario_4",
                "name": "Budget Overrun Detection",
                "description": "Detect and escalate budget overruns"
            },
            {
                "id": "scenario_5",
                "name": "Black Friday Planning",
                "description": "High surge demand planning and constraints"
            }
        ]
        return {
            "status": "success",
            "scenarios": scenarios,
            "total": len(scenarios)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": "Endpoint not found",
            "path": str(request.url)
        }
    )

# Test execution endpoints
class TestRequest(BaseModel):
    scenario_id: str = None
    run_all: bool = False

@app.post("/api/tests/run")
async def run_tests(request: TestRequest):
    """Execute test scenarios and return results"""
    import subprocess
    import json
    from datetime import datetime
    
    try:
        if request.run_all:
            # Run all tests
            cmd = ['python', 'tests/test_enterprise_scenarios.py']
        else:
            # Run specific scenario test
            cmd = ['python', '-m', 'unittest', f'tests.test_enterprise_scenarios.TestScenario{request.scenario_id.split("scenario")[1].capitalize()}_*', '-v']
        
        # Execute tests
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        # Parse test output
        output = result.stdout + result.stderr
        test_results = parse_test_output(output, request.run_all, request.scenario_id)
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            **test_results
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

def parse_test_output(output, run_all, scenario_id):
    """Parse unittest output to extract test results"""
    import re
    
    # Extract summary line (e.g., "Ran 25 tests in 203.020s")
    ran_match = re.search(r'Ran (\d+) tests in ([\d.]+)s', output)
    
    # Extract pass/fail counts
    failed_match = re.search(r'FAILED \(failures=(\d+), errors=(\d+)\)', output)
    passed_match = re.search(r'OK', output)
    
    total_tests = int(ran_match.group(1)) if ran_match else 0
    duration = float(ran_match.group(2)) if ran_match else 0
    
    if failed_match:
        failures = int(failed_match.group(1))
        errors = int(failed_match.group(2))
        passed = total_tests - failures - errors
        success_rate = passed / total_tests if total_tests > 0 else 0
    elif passed_match:
        passed = total_tests
        failures = 0
        errors = 0
        success_rate = 1.0
    else:
        passed = 0
        failures = 0
        errors = total_tests
        success_rate = 0
    
    # Extract individual test results
    test_pattern = r'(\w+.*?) \((.*?)\) \.\.\. (ok|FAIL|ERROR)'
    test_matches = re.findall(test_pattern, output)
    
    tests = []
    for match in test_matches:
        test_name, test_class, status = match
        tests.append({
            "name": test_name,
            "class": test_class,
            "passed": status == 'ok',
            "status": status,
            "message": f"Test {status.lower()}"
        })
    
    if run_all:
        # Group by scenario
        scenarios = {}
        scenario_names = {
            'scenario1': 'Q2 Inventory Planning',
            'scenario2': 'Supplier Crisis',
            'scenario3': 'ERP System Down',
            'scenario4': 'Budget Overrun',
            'scenario5': 'Black Friday Planning'
        }
        
        for test in tests:
            scenario = None
            for s_id, s_name in scenario_names.items():
                if s_id in test['class'].lower():
                    scenario = s_id
                    break
            
            if scenario:
                if scenario not in scenarios:
                    scenarios[scenario] = {
                        "name": scenario_names[scenario],
                        "tests": []
                    }
                scenarios[scenario]["tests"].append(test)
        
        return {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failures + errors,
            "success_rate": success_rate,
            "duration": duration,
            "scenarios": scenarios,
            "raw_output": output
        }
    else:
        # Single scenario
        scenario_id_num = scenario_id.split("scenario")[1] if scenario_id else "1"
        return {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failures + errors,
            "success_rate": success_rate,
            "duration": duration,
            "tests": tests,
            "scenario_id": scenario_id,
            "raw_output": output
        }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "error": str(exc)
        }
    )

if __name__ == '__main__':
    print("[INIT] Initializing SupplyChain Planning System...")
    initialize_workflow()
    
    print("[SERVER] Starting server on http://localhost:8000")
    print("\n[ENDPOINTS] Available endpoints:")
    print("  GET  /health                 - Health check")
    print("  POST /api/pipeline/run       - Execute pipeline")
    print("  GET  /api/pipeline/status    - Pipeline status")
    print("  GET  /api/forecasts          - Get forecasts")
    print("  GET  /api/inventory          - Get inventory plan")
    print("  GET  /api/suppliers          - Get supplier plan")
    print("  GET  /api/logistics          - Get logistics plan")
    print("  GET  /api/alerts             - Get alerts")
    print("  GET  /api/escalations        - Get escalations")
    print("  POST /api/human-review       - Submit human review")
    print("  GET  /api/evaluation         - Get evaluation metrics")
    print("  GET  /api/scenarios          - Get test scenarios")
    print("  POST /api/tests/run          - Run test scenarios (individual or all)")
    print("  GET  /docs                   - API documentation (Swagger UI)")
    print("\n")
    
    uvicorn.run(app, host='0.0.0.0', port=8000)
