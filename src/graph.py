
from langgraph.graph import StateGraph, END
from .state import ForecastState

from .agents.data_loader import data_loader_agent
from .agents.data_profiling import data_profiling_agent
from .agents.feature_engineering import feature_engineering_agent
# from .agents.model_selection import model_selection_agent
from .agents.forecasting import forecasting_agent
from .agents.inventory_optimization import inventory_optimization_agent
from .agents.human_review import human_review_agent
from .agents.evaluation import evaluation_agent

def route_after_human(state):
    return "evaluate" if state["human_decision"] in ["approve", "modify"] else END

def build_graph():
    g = StateGraph(ForecastState)

    g.add_node("load", data_loader_agent)
    g.add_node("profile", data_profiling_agent)
    g.add_node("features", feature_engineering_agent)
    # g.add_node("model", model_selection_agent)
    g.add_node("forecast", forecasting_agent)
    g.add_node("inventory", inventory_optimization_agent)
    g.add_node("human", human_review_agent)
    g.add_node("evaluate", evaluation_agent)

    g.set_entry_point("load")
    g.add_edge("load", "profile")
    g.add_edge("profile", "features")
    g.add_edge("features", "forecast")
    g.add_edge("forecast", "inventory")
    g.add_edge("inventory", "human")

    g.add_conditional_edges("human", route_after_human, {
        "evaluate": "evaluate",
        END: END
    })

    g.add_edge("evaluate", END)
    return g.compile()
