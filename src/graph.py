
from langgraph.graph import StateGraph, END
from .state import ForecastState

from .agents.data_loader import data_loader_agent
from .agents.data_profiling import data_profiling_agent
from .agents.feature_engineering import feature_engineering_agent
from .agents.demand_forecasting import demand_forecasting_agent  # Phase 1
from .agents.inventory_optimization_v2 import inventory_optimization_agent  # Phase 2
from .agents.supplier_procurement import supplier_procurement_agent  # Phase 3
from .agents.logistics_capacity import logistics_capacity_agent  # Phase 4
from .agents.human_review import human_review_agent
from .agents.evaluation import evaluation_agent

def route_after_human(state):
    return "evaluate" if state["human_decision"] in ["approve", "modify"] else END

def build_graph():
    g = StateGraph(ForecastState)

    # Data Pipeline
    g.add_node("load", data_loader_agent)
    g.add_node("profile", data_profiling_agent)
    g.add_node("features", feature_engineering_agent)
    
    # Phase 1: Demand Forecasting (Enhanced)
    g.add_node("demand_forecast", demand_forecasting_agent)
    
    # Phase 2: Inventory Optimization (Budget-Aware)
    g.add_node("inventory", inventory_optimization_agent)
    
    # Phase 3: Supplier & Procurement
    g.add_node("procurement", supplier_procurement_agent)
    
    # Phase 4: Logistics & Capacity
    g.add_node("logistics", logistics_capacity_agent)
    
    # Human Review & Evaluation
    g.add_node("human", human_review_agent)
    g.add_node("evaluate", evaluation_agent)

    # Define edges
    g.set_entry_point("load")
    g.add_edge("load", "profile")
    g.add_edge("profile", "features")
    g.add_edge("features", "demand_forecast")
    g.add_edge("demand_forecast", "inventory")
    g.add_edge("inventory", "procurement")
    g.add_edge("procurement", "logistics")
    g.add_edge("logistics", "human")

    g.add_conditional_edges("human", route_after_human, {
        "evaluate": "evaluate",
        END: END
    })

    g.add_edge("evaluate", END)
    return g.compile()
