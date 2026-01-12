
import pandas as pd
from typing import TypedDict, Dict

class ForecastState(TypedDict):
    raw_data: pd.DataFrame
    processed_data: pd.DataFrame
    features: pd.DataFrame
    forecasts: pd.DataFrame
    inventory_plan: pd.DataFrame
    human_decision: str
    final_inventory_plan: pd.DataFrame
    metrics: dict
