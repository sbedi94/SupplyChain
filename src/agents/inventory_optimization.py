
import numpy as np
import pandas as pd
from scipy.stats import norm

def inventory_optimization_agent(state):
    df = state["forecasts"]
    if df.empty or "store_id" not in df.columns or "sku_id" not in df.columns:
        return {"inventory_plan": pd.DataFrame()}
    z = norm.ppf(0.95)
    lead_time = 7
    rows = []

    for (store, sku), g in df.groupby(["store_id", "sku_id"]):
        mean_d = g["forecast"].mean()
        std_d = g["forecast"].std()

        safety_stock = z * std_d * np.sqrt(lead_time)
        rop = mean_d * lead_time + safety_stock

        rows.append({
            "store_id": store,
            "sku_id": sku,
            "mean_daily_demand": round(mean_d, 2),
            "safety_stock": round(safety_stock, 2),
            "reorder_point": round(rop, 2),
            "recommended_order_qty": round(rop, 0)
        })

    return {"inventory_plan": pd.DataFrame(rows)}
