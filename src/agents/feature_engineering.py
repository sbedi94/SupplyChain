
import pandas as pd

def feature_engineering_agent(state):
    df = state["processed_data"]
    rows = []

    for (_, _), g in df.groupby(["store_id", "sku_id"]):
        g = g.sort_values("date")
        g["lag_1"] = g["units_sold"].shift(1)
        g["lag_7"] = g["units_sold"].shift(7)
        g["rolling_7"] = g["units_sold"].rolling(7).mean()
        g["weekday"] = g["date"].dt.weekday
        g["month"] = g["date"].dt.month
        rows.append(g)

    features = pd.concat(rows).dropna()
    return {"features": features}
