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
    print("  GET  /docs                   - API documentation (Swagger UI)")
    print("  GET  /redoc                  - API documentation (ReDoc)")
    print("\n")
    
    uvicorn.run(app, host='0.0.0.0', port=8000)
