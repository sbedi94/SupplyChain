
import pandas as pd
from typing import TypedDict, Dict, List, Optional

class ForecastState(TypedDict, total=False):
    # Data Pipeline
    raw_data: pd.DataFrame
    processed_data: pd.DataFrame
    features: pd.DataFrame
    
    # Phase 1: Demand Forecasting
    forecasts: pd.DataFrame
    forecast_cache: Dict
    forecast_alerts: List[str]
    
    # Phase 2: Inventory Optimization
    inventory_plan: pd.DataFrame
    budget_constraints: Dict
    budget_alerts: List[str]
    
    # Phase 3: Supplier & Procurement
    supplier_status: Dict
    procurement_plan: pd.DataFrame
    supplier_alerts: List[str]
    escalations: List[Dict]
    
    # Phase 4: Logistics & Capacity
    logistics_plan: pd.DataFrame
    warehouse_capacity: Dict
    capacity_alerts: List[str]
    shipment_plan: pd.DataFrame
    
    # Human Review & Evaluation
    human_decision: str
    final_inventory_plan: pd.DataFrame
    metrics: Dict
    
    # Overall Status
    all_alerts: List[str]
    execution_status: str
